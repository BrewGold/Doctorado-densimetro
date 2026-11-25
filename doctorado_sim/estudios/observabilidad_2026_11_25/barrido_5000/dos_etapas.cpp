#define main previous_imu_main
#include "imu_sim.cpp"
#undef main

namespace {
constexpr double eq_reference = -0.9746388227722308;
constexpr double eq_slope = 0.0021440041612968324;
constexpr double eq_width = 0.45;

double equilibrium(double rho) {
    return eq_reference - eq_width * std::atan(eq_slope * (rho - 1000) / eq_width);
}

double chirp(double t) {
    return 0.03 * std::sin(2 * pi * (0.1 * t + 1.9 * t * t / 120));
}

double excitation(double t, double drive_frequency) {
    return drive_frequency > 0
        ? 0.03 * std::sin(2 * pi * drive_frequency * t)
        : chirp(t);
}

std::vector<Step> protocol_steps(bool refined = false,
                                 double drive_frequency = 0) {
    constexpr int ticks = 2600;
    std::vector<Step> events;
    int last = 0;
    for (int tick = 1; tick <= 90 * ticks; ++tick) {
        bool sensor = tick % 25 == 0;
        bool host = tick % 26 == 0;
        if (!sensor && !host) continue;
        double t0 = static_cast<double>(last) / ticks;
        double t1 = static_cast<double>(tick) / ticks;
        double middle = (t0 + t1) / 2;
        auto make_step = [&](double start, double end, bool s, bool h) {
            double mid = (start+end)/2;
            double a, b, d;
            if (middle < 60) {
                a = excitation(start, drive_frequency);
                b = excitation(mid, drive_frequency);
                d = excitation(end, drive_frequency);
            } else if (middle < 60.2) {
                a = b = d = 0.03;
            } else {
                a = b = d = 0;
            }
            events.push_back({end, end-start, a, b, d, s, h});
        };
        if (refined) {
            make_step(t0, middle, false, false);
            make_step(middle, t1, sensor, host);
        } else {
            make_step(t0, t1, sensor, host);
        }
        last = tick;
    }
    return events;
}

struct ProtocolResult {
    std::array<double, 14> values;
    int clips;
};

std::array<double, 4> fit_integral_ode(
        const std::vector<double>& theta, const std::vector<double>& omega,
        int first, int last, bool driven, double drive_frequency = 0) {
    const int n = driven ? 4 : 3;
    double matrix[4][5]{};
    constexpr int width = 20;
    for (int start = first; start+width<=last; start+=width) {
        std::array<double, 4> features{};
        for (int i=start; i<start+width; ++i) {
            double u0 = driven ? excitation(i/100.0, drive_frequency) : 0;
            double u1 = driven ? excitation((i+1)/100.0, drive_frequency) : 0;
            features[0] -= (omega[i]+omega[i+1])/200;
            features[1] -= (theta[i]+theta[i+1]-2*theta[first])/200;
            if (driven) features[2] += (u0+u1)/200;
        }
        features[n-1] = width/100.0;
        double target=omega[start+width]-omega[start];
        for (int i=0; i<n; ++i) {
            for (int j=0; j<n; ++j) matrix[i][j]+=features[i]*features[j];
            matrix[i][n]+=features[i]*target;
        }
    }
    for (int i=0; i<n; ++i) {
        int pivot=i;
        for (int j=i+1; j<n; ++j)
            if (std::abs(matrix[j][i])>std::abs(matrix[pivot][i])) pivot=j;
        if (std::abs(matrix[pivot][i])<1e-18)
            throw std::runtime_error("Ajuste de EDO singular");
        for (int j=i; j<=n; ++j) std::swap(matrix[i][j],matrix[pivot][j]);
        double divisor=matrix[i][i];
        for (int j=i; j<=n; ++j) matrix[i][j]/=divisor;
        for (int k=0; k<n; ++k) {
            if (k==i) continue;
            double factor=matrix[k][i];
            for (int j=i; j<=n; ++j) matrix[k][j]-=factor*matrix[i][j];
        }
    }
    std::array<double, 4> out{};
    for (int i=0; i<n; ++i) out[i]=matrix[i][n];
    return out;
}

ProtocolResult protocol(const Case& c, const std::vector<Step>& events,
                        std::mt19937_64& rng, int sensor_variant = 0,
                        std::vector<double>* dynamic_gyro = nullptr,
                        double sensor_cutoff = 20,
                        double actuator_factor = 1,
                        double drive_frequency = 0) {
    const double inertia = 8e-5 + c.rho * 5e-8;
    const double stiffness = 5e-7 * c.rho;
    const double damping = 5e-3 * std::sqrt(c.mu / 0.02);
    const double theta_eq = equilibrium(c.rho);
    std::normal_distribution<double> normal(0, 1);
    const bool noise_enabled = sensor_variant == 0 || sensor_variant == 3;
    const double noise_scale = noise_enabled ? 1 : 0;
    const double bias_ax = noise_scale*0.005*g*normal(rng);
    const double bias_az = noise_scale*0.005*g*normal(rng);
    const double bias_gyro = noise_scale*0.05*pi/180*normal(rng);
    const double sigma_a = noise_scale*70e-6*g*std::sqrt(52.0);
    const double sigma_g = noise_scale*0.0038*pi/180*std::sqrt(52.0);
    const double lowpass = (sensor_variant == 3 || sensor_variant == 4 ||
                            sensor_variant == 6)
        ? 1 : 1-std::exp(-2*pi*sensor_cutoff/104);
    const double alpha_filter = 1-std::exp(-2*pi*5/100);
    const double acc_quantum = 0.000061*g, gyro_quantum = 0.00875*pi/180;
    const double gyro_limit = 250*pi/180;
    int clips = 0;
    State x{0, 0};
    double ax = quantize(g*std::sin(theta_eq)+bias_ax+sigma_a*normal(rng),
                         acc_quantum, 2*g, clips);
    double az = quantize(g*std::cos(theta_eq)+bias_az+sigma_a*normal(rng),
                         acc_quantum, 2*g, clips);
    double gyro = quantize(bias_gyro+sigma_g*normal(rng),
                           gyro_quantum, gyro_limit, clips);
    double theta = std::atan2(ax, az);
    std::vector<double> angles{theta}, velocities{gyro};
    if (dynamic_gyro) {
        dynamic_gyro->clear();
        dynamic_gyro->reserve(6001);
        dynamic_gyro->push_back(gyro);
    }
    angles.reserve(9001); velocities.reserve(9001);
    for (const Step& e : events) {
        State k1 = derivative(x, e.u1*actuator_factor, inertia, damping, stiffness);
        State k2 = derivative(add(x, k1, e.h/2), e.um*actuator_factor, inertia, damping, stiffness);
        State k3 = derivative(add(x, k2, e.h/2), e.um*actuator_factor, inertia, damping, stiffness);
        State k4 = derivative(add(x, k3, e.h), e.u2*actuator_factor, inertia, damping, stiffness);
        x.theta += e.h/6*(k1.theta+2*k2.theta+2*k3.theta+k4.theta);
        x.omega += e.h/6*(k1.omega+2*k2.omega+2*k3.omega+k4.omega);
        if (e.sensor) {
            double raw_ax = g*std::sin(theta_eq+x.theta)+bias_ax+sigma_a*normal(rng);
            double raw_az = g*std::cos(theta_eq+x.theta)+bias_az+sigma_a*normal(rng);
            double raw_gyro = x.omega+bias_gyro+sigma_g*normal(rng);
            if (std::abs(raw_ax)>2*g) ++clips;
            if (std::abs(raw_az)>2*g) ++clips;
            if (std::abs(raw_gyro)>gyro_limit) ++clips;
            raw_ax = std::clamp(raw_ax,-2*g,2*g);
            raw_az = std::clamp(raw_az,-2*g,2*g);
            raw_gyro = std::clamp(raw_gyro,-gyro_limit,gyro_limit);
            ax = quantize(ax+lowpass*(raw_ax-ax),acc_quantum,2*g,clips);
            az = quantize(az+lowpass*(raw_az-az),acc_quantum,2*g,clips);
            gyro = quantize(gyro+lowpass*(raw_gyro-gyro),gyro_quantum,gyro_limit,clips);
        }
        if (e.host) {
            if (sensor_variant == 1) {
                theta = theta_eq+x.theta;
                gyro = x.omega;
            } else if (sensor_variant == 6) {
                theta = theta_eq+x.theta;
            } else {
                if (sensor_variant == 5) {
                    gyro = x.omega;
                    ax = g*std::sin(theta_eq+x.theta);
                    az = g*std::cos(theta_eq+x.theta);
                }
                theta = 0.98*(theta+gyro/100)+0.02*std::atan2(ax,az);
            }
            angles.push_back(theta);
            velocities.push_back(gyro);
            if (dynamic_gyro && angles.size() <= 6001) dynamic_gyro->push_back(gyro);
        }
    }
    if (angles.size()!=9001) throw std::runtime_error("Muestreo incorrecto");
    double eq_hat = 0;
    for (int i=8001; i<=9000; ++i) eq_hat += angles[i]/1000;
    // The dynamic stage uses its first measurement as its independent baseline.
    const double initial = angles[0];
    double tmax=0, omax=0, amax=0, et=0, eo=0, filtered_alpha=0;
    for (int i=0; i<=6000; ++i) {
        double dtheta=angles[i]-initial;
        tmax=std::max(tmax,std::abs(dtheta));
        omax=std::max(omax,std::abs(velocities[i]));
        if (i>0) {
            double previous=angles[i-1]-initial;
            et+=(previous*previous+dtheta*dtheta)/200;
            eo+=(velocities[i-1]*velocities[i-1]+velocities[i]*velocities[i])/200;
            filtered_alpha+=alpha_filter*((velocities[i]-velocities[i-1])*100-filtered_alpha);
            amax=std::max(amax,std::abs(filtered_alpha));
        }
    }
    double eq_prev=0;
    for (int i=7001; i<=8000; ++i) eq_prev += angles[i]/1000;
    auto driven=fit_integral_ode(
        angles,velocities,0,6000,true,drive_frequency);
    auto free=fit_integral_ode(angles,velocities,6020,9000,false);
    double free_eq=angles[6020]+free[2]/free[1];
    return {{{eq_hat,tmax,omax,amax,et,eo,et/(eo+1e-16),eq_hat-eq_prev,
              driven[0],driven[1],driven[2],free[0],free[1],free_eq}},clips};
}
}  // namespace

#ifndef DOS_ETAPAS_LIBRARY
int main(int argc, char** argv) {
    if (argc<2 || argc>3) throw std::runtime_error("Uso: dos_etapas DIRECTORIO [check]");
    std::string dir=argv[1];
    auto cases=read_cases(dir+"/imu_casos.csv");
    if (cases.size()!=9000) throw std::runtime_error("Se esperaban 9000 filas");
    auto events=protocol_steps();
    if (argc==3 && std::string(argv[2])=="diagnose") {
        std::array<std::string, 7> names{"imu", "truth", "filter_no_noise",
            "noise_no_lowpass", "no_noise_no_lowpass", "synchronous_complementary",
            "true_angle_held_gyro"};
        for (int variant=0; variant<7; ++variant) {
            std::mt19937_64 rng(2026);
            double a_ratio=0, gain_ratio=0, mu_rho_error=0, mu_ratio_error=0;
            constexpr int count=100;
            for (int i=0; i<count; ++i) {
                const Case& c=cases[(i*47)%cases.size()];
                auto result=protocol(c,events,rng,variant);
                double inertia=8e-5+c.rho*5e-8;
                double true_a=0.005*std::sqrt(c.mu/0.02)/inertia;
                double true_gain=0.02/inertia;
                double est_a=result.values[8];
                double est_gain=result.values[10];
                if (est_a<=0 || est_gain<=0) throw std::runtime_error("Ajuste no fisico");
                double mu_rho=0.02*std::pow(est_a*inertia/0.005,2);
                double mu_ratio=0.02*std::pow(est_a*0.02/est_gain/0.005,2);
                a_ratio+=est_a/true_a/count;
                gain_ratio+=est_gain/true_gain/count;
                mu_rho_error+=100*std::abs(mu_rho/c.mu-1)/count;
                mu_ratio_error+=100*std::abs(mu_ratio/c.mu-1)/count;
            }
            std::cout << names[variant] << " a/real=" << a_ratio
                      << " ganancia/real=" << gain_ratio
                      << " MAPE_mu_con_rho_real=" << mu_rho_error
                      << " MAPE_mu_con_ratio=" << mu_ratio_error << '\n';
        }
        return 0;
    }
    if (argc==3) {
        if (std::string(argv[2])!="check") throw std::runtime_error("Modo desconocido");
        auto refined=protocol_steps(true);
        std::mt19937_64 coarse_rng(2026), fine_rng(2026);
        std::array<double, 14> max_diff{};
        for (int i=0; i<20; ++i) {
            auto a=protocol(cases[i],events,coarse_rng);
            auto b=protocol(cases[i],refined,fine_rng);
            for (std::size_t j=0; j<max_diff.size(); ++j)
                max_diff[j]=std::max(max_diff[j],std::abs(a.values[j]-b.values[j]));
        }
        std::cout << "Diferencia maxima absoluta por indicador: ";
        for (auto v:max_diff) std::cout << v << ' ';
        std::cout << '\n';
        return 0;
    }
    std::ofstream out(dir+"/dos_etapas.csv");
    if (!out) throw std::runtime_error("No se pudo abrir la salida");
    out << "id,set,rep,ThetaEq,ThetaMax,OmegaMax,AlphaMax,Etheta,Eomega,R,eq_drift,"
           "drive_a,drive_b,drive_gain,free_a,free_b,free_eq,rho,mu,clips\n";
    out << std::setprecision(12);
    std::mt19937_64 rng(2026);
    for (std::size_t i=0; i<cases.size(); ++i) {
        auto result=protocol(cases[i],events,rng);
        out << cases[i].id << ',' << cases[i].set << ',' << cases[i].rep;
        for (auto v:result.values) out << ',' << v;
        out << ',' << cases[i].rho << ',' << cases[i].mu << ',' << result.clips << '\n';
        if ((i+1)%1000==0) std::cerr << i+1 << "/9000\n";
    }
}
#endif
