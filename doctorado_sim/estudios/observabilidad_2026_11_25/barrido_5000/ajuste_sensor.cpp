#define DOS_ETAPAS_LIBRARY
#include "dos_etapas.cpp"

#include <cstring>

namespace {
struct ExtendedState {
    double theta, omega, stheta, somega;
};

ExtendedState diff(ExtendedState x, double u, double inertia,
                   double damping, double stiffness) {
    return {
        x.omega,
        (0.02*u - damping*x.omega - stiffness*std::sin(x.theta))/inertia,
        x.somega,
        (-damping*x.somega - stiffness*std::cos(x.theta)*x.stheta -
         0.5*damping*x.omega)/inertia
    };
}
ExtendedState add_state(ExtendedState x, ExtendedState dx, double h) {
    return {x.theta+h*dx.theta, x.omega+h*dx.omega,
            x.stheta+h*dx.stheta, x.somega+h*dx.somega};
}

void forward(double rho, double log_mu, const std::vector<Step>& events,
             double cutoff, double* output, double* jacobian) {
    const double mu=std::exp(log_mu);
    const double inertia=8e-5+rho*5e-8;
    const double stiffness=5e-7*rho;
    const double damping=0.005*std::sqrt(mu/0.02);
    const double lowpass=1-std::exp(-2*pi*cutoff/104);
    ExtendedState x{};
    double filtered=0, filtered_sensitivity=0;
    int count=1;
    output[0]=0;
    jacobian[0]=0;
    for (const Step& e:events) {
        if (e.t>60.000000001) break;
        auto k1=diff(x,e.u1,inertia,damping,stiffness);
        auto k2=diff(add_state(x,k1,e.h/2),e.um,inertia,damping,stiffness);
        auto k3=diff(add_state(x,k2,e.h/2),e.um,inertia,damping,stiffness);
        auto k4=diff(add_state(x,k3,e.h),e.u2,inertia,damping,stiffness);
        x.theta+=e.h/6*(k1.theta+2*k2.theta+2*k3.theta+k4.theta);
        x.omega+=e.h/6*(k1.omega+2*k2.omega+2*k3.omega+k4.omega);
        x.stheta+=e.h/6*(k1.stheta+2*k2.stheta+2*k3.stheta+k4.stheta);
        x.somega+=e.h/6*(k1.somega+2*k2.somega+2*k3.somega+k4.somega);
        if (e.sensor) {
            filtered+=lowpass*(x.omega-filtered);
            filtered_sensitivity+=lowpass*(x.somega-filtered_sensitivity);
        }
        if (e.host) {
            if (count>=6001) throw std::runtime_error("Muestras excesivas");
            output[count]=filtered;
            jacobian[count]=filtered_sensitivity;
            ++count;
        }
    }
    if (count!=6001) throw std::runtime_error("Muestras insuficientes");
}

void forward(double rho, double log_mu, double* output, double* jacobian) {
    static const std::vector<Step> events = protocol_steps();
    forward(rho, log_mu, events, 20, output, jacobian);
}
}  // namespace

extern "C" int generate_trial(double rho, double mu, unsigned long long seed,
                              double sensor_cutoff, double actuator_factor,
                              double* gyro, double* values) {
    try {
        static const std::vector<Step> events=protocol_steps();
        Case c{0,0,"test",rho,mu};
        std::mt19937_64 rng(seed);
        std::vector<double> samples;
        ProtocolResult result=protocol(c,events,rng,0,&samples,
                                       sensor_cutoff,actuator_factor);
        if (samples.size()!=6001) throw std::runtime_error("Muestras incorrectas");
        std::memcpy(gyro,samples.data(),samples.size()*sizeof(double));
        std::copy(result.values.begin(),result.values.end(),values);
        values[14]=result.clips;
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "generate_trial: " << e.what() << '\n';
        return 1;
    }
}

extern "C" int predict_gyro(double rho, double log_mu, double* output,
                            double* jacobian) {
    try {
        forward(rho,log_mu,output,jacobian);
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "predict_gyro: " << e.what() << '\n';
        return 1;
    }
}

extern "C" int generate_sweep_trial(
        double rho, double mu, unsigned long long seed, double sensor_cutoff,
        double drive_frequency, double* gyro, double* values) {
    try {
        const std::vector<Step> events = protocol_steps(false, drive_frequency);
        Case c{0,0,"test",rho,mu};
        std::mt19937_64 rng(seed);
        std::vector<double> samples;
        ProtocolResult result=protocol(
            c,events,rng,0,&samples,sensor_cutoff,1,drive_frequency);
        if (samples.size()!=6001)
            throw std::runtime_error("Muestras incorrectas");
        std::memcpy(gyro,samples.data(),samples.size()*sizeof(double));
        std::copy(result.values.begin(),result.values.end(),values);
        values[14]=result.clips;
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "generate_sweep_trial: " << e.what() << '\n';
        return 1;
    }
}

extern "C" int predict_sweep_gyro(
        double rho, double log_mu, double sensor_cutoff,
        double drive_frequency, double* output, double* jacobian) {
    try {
        const std::vector<Step> events = protocol_steps(false, drive_frequency);
        forward(rho, log_mu, events, sensor_cutoff, output, jacobian);
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "predict_sweep_gyro: " << e.what() << '\n';
        return 1;
    }
}
