#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
constexpr double pi = 3.14159265358979323846;
constexpr double g = 9.80665;
constexpr int sensor_rate = 104;
constexpr int host_rate = 100;
constexpr int seconds = 60;
constexpr std::array<double, 9> frequencies{
    0.05, 0.1, 0.2, 0.4, 0.8, 1.6, 3.2, 6.4, 12.8
};
struct Case {
    int id, rep;
    std::string set;
    double rho, mu;
};
struct Step {
    double t, h, u1, um, u2;
    bool sensor, host;
};
struct State { double theta, omega; };

std::vector<Case> read_cases(const std::string& path) {
    std::ifstream in(path);
    if (!in) throw std::runtime_error("No se puede abrir " + path);
    std::string line;
    std::getline(in, line);
    std::vector<Case> cases;
    while (std::getline(in, line)) {
        std::replace(line.begin(), line.end(), ',', ' ');
        std::istringstream parser(line);
        Case c;
        if (!(parser >> c.id >> c.set >> c.rep >> c.rho >> c.mu))
            throw std::runtime_error("Fila invalida: " + line);
        cases.push_back(c);
    }
    return cases;
}

double raw_multisine(double t) {
    double value = 0;
    for (std::size_t k = 0; k < frequencies.size(); ++k) {
        double phase = -pi * static_cast<double>(k * (k + 1)) /
                       static_cast<double>(frequencies.size());
        value += std::sin(2 * pi * frequencies[k] * t + phase);
    }
    return value;
}

double input(double t, int drive, double scale) {
    if (drive == 0) return 0.03 * std::sin(2 * pi * t);
    if (drive == 1) return 0.03 * std::sin(2 * pi * (0.1 + 1.9 * t / 60) * t);
    if (drive == 2) return 0.03 * std::sin(2 * pi * (0.1 * t + 1.9 * t * t / 120));
    return scale * raw_multisine(t);
}

std::vector<Step> make_steps(int drive, double scale, bool refined = false) {
    // Both sampling clocks are synchronous at t=0; this is an explicit assumption.
    constexpr int ticks = 2600;  // lcm(100,104)
    constexpr int sensor_tick = ticks / sensor_rate;
    constexpr int host_tick = ticks / host_rate;
    std::vector<Step> events;
    int previous = 0;
    for (int tick = 1; tick <= seconds * ticks; ++tick) {
        const bool sensor = tick % sensor_tick == 0;
        const bool host = tick % host_tick == 0;
        if (!sensor && !host) continue;
        const double t0 = static_cast<double>(previous) / ticks;
        const double t1 = static_cast<double>(tick) / ticks;
        if (refined) {
            double middle = (t0 + t1) / 2;
            events.push_back({middle, middle - t0, input(t0, drive, scale),
                              input((t0 + middle) / 2, drive, scale),
                              input(middle, drive, scale), false, false});
            events.push_back({t1, t1 - middle, input(middle, drive, scale),
                              input((middle + t1) / 2, drive, scale),
                              input(t1, drive, scale), sensor, host});
        } else {
            events.push_back({t1, t1 - t0, input(t0, drive, scale),
                              input((t0 + t1) / 2, drive, scale),
                              input(t1, drive, scale), sensor, host});
        }
        previous = tick;
    }
    return events;
}

State derivative(State x, double u, double inertia, double damping, double stiffness) {
    return {x.omega, (0.02 * u - damping * x.omega -
                       stiffness * std::sin(x.theta)) / inertia};
}
State add(State x, State dx, double h) {
    return {x.theta + h * dx.theta, x.omega + h * dx.omega};
}
double quantize(double x, double quantum, double limit, int& clipped) {
    if (x > limit || x < -limit) ++clipped;
    x = std::clamp(x, -limit, limit - quantum);
    return std::round(x / quantum) * quantum;
}
struct Result {
    std::array<double, 7> features;
    int clips;
};

Result simulate(const Case& c, const std::vector<Step>& events,
                std::mt19937_64& rng) {
    const double inertia = 8e-5 + c.rho * 5e-8;
    const double stiffness = 5e-7 * c.rho;
    const double damping = 5e-3 * std::sqrt(c.mu / 0.02);
    std::normal_distribution<double> normal(0, 1);
    const double bias_ax = 0.005 * g * normal(rng);
    const double bias_az = 0.005 * g * normal(rng);
    const double bias_gyro = 0.05 * pi / 180 * normal(rng);
    const double sigma_a = 70e-6 * g * std::sqrt(sensor_rate / 2.0);
    const double sigma_g = 0.0038 * pi / 180 * std::sqrt(sensor_rate / 2.0);
    const double lowpass = 1 - std::exp(-2 * pi * 20 / sensor_rate);
    const double alpha_filter = 1 - std::exp(-2 * pi * 5 / host_rate);
    const double accel_quantum = 0.000061 * g;
    const double gyro_quantum = 0.00875 * pi / 180;
    const double gyro_limit = 250 * pi / 180;
    int clips = 0;
    State x{0, 0};
    double ax = quantize(bias_ax + sigma_a * normal(rng), accel_quantum, 2 * g, clips);
    double az = quantize(g + bias_az + sigma_a * normal(rng), accel_quantum, 2 * g, clips);
    double gyro = quantize(bias_gyro + sigma_g * normal(rng), gyro_quantum, gyro_limit, clips);
    double theta_est = std::atan2(ax, az);
    std::vector<double> theta{theta_est}, omega{gyro};
    theta.reserve(seconds * host_rate + 1);
    omega.reserve(seconds * host_rate + 1);
    for (const Step& e : events) {
        State k1 = derivative(x, e.u1, inertia, damping, stiffness);
        State k2 = derivative(add(x, k1, e.h / 2), e.um, inertia, damping, stiffness);
        State k3 = derivative(add(x, k2, e.h / 2), e.um, inertia, damping, stiffness);
        State k4 = derivative(add(x, k3, e.h), e.u2, inertia, damping, stiffness);
        x.theta += e.h / 6 * (k1.theta + 2*k2.theta + 2*k3.theta + k4.theta);
        x.omega += e.h / 6 * (k1.omega + 2*k2.omega + 2*k3.omega + k4.omega);
        if (e.sensor) {
            double raw_ax = g * std::sin(x.theta) + bias_ax + sigma_a * normal(rng);
            double raw_az = g * std::cos(x.theta) + bias_az + sigma_a * normal(rng);
            double raw_gyro = x.omega + bias_gyro + sigma_g * normal(rng);
            if (std::abs(raw_ax) > 2*g) ++clips;
            if (std::abs(raw_az) > 2*g) ++clips;
            if (std::abs(raw_gyro) > gyro_limit) ++clips;
            raw_ax = std::clamp(raw_ax, -2*g, 2*g);
            raw_az = std::clamp(raw_az, -2*g, 2*g);
            raw_gyro = std::clamp(raw_gyro, -gyro_limit, gyro_limit);
            // Explicit software low-pass approximation, not the undocumented hardware filter.
            ax += lowpass * (raw_ax - ax);
            az += lowpass * (raw_az - az);
            gyro += lowpass * (raw_gyro - gyro);
            ax = quantize(ax, accel_quantum, 2*g, clips);
            az = quantize(az, accel_quantum, 2*g, clips);
            gyro = quantize(gyro, gyro_quantum, gyro_limit, clips);
        }
        if (e.host) {
            theta_est = 0.98 * (theta_est + gyro / host_rate) +
                        0.02 * std::atan2(ax, az);
            theta.push_back(theta_est);
            omega.push_back(gyro);
        }
    }
    if (theta.size() != seconds * host_rate + 1)
        throw std::runtime_error("Numero de muestras inesperado");
    double theta_max = 0, omega_max = 0, alpha_max = 0;
    double e_theta = 0, e_omega = 0, filtered_alpha = 0;
    for (std::size_t i = 0; i < theta.size(); ++i) {
        theta_max = std::max(theta_max, std::abs(theta[i]));
        omega_max = std::max(omega_max, std::abs(omega[i]));
        if (i > 0) {
            e_theta += (theta[i-1]*theta[i-1] + theta[i]*theta[i]) / (2*host_rate);
            e_omega += (omega[i-1]*omega[i-1] + omega[i]*omega[i]) / (2*host_rate);
            const double derivative = (omega[i] - omega[i-1]) * host_rate;
            filtered_alpha += alpha_filter * (derivative - filtered_alpha);
            alpha_max = std::max(alpha_max, std::abs(filtered_alpha));
        }
    }
    int last = -1;
    for (std::size_t i = 0; i < theta.size(); ++i)
        if (std::abs(theta[i]) > 0.05 * theta_max) last = static_cast<int>(i);
    return {{{theta_max, omega_max, alpha_max, e_theta, e_omega,
              last < 0 ? 0.0 : static_cast<double>(last) / host_rate,
              e_theta / (e_omega + 1e-16)}}, clips};
}
}  // namespace

int main(int argc, char** argv) {
    if (argc < 2 || argc > 3) throw std::runtime_error("Uso: imu_sim DIRECTORIO [check]");
    const std::string dir = argv[1];
    auto cases = read_cases(dir + "/imu_casos.csv");
    if (cases.size() != 9000) throw std::runtime_error("Se esperaban 9000 filas");
    double peak = 0;
    for (int i = 0; i <= 600000; ++i)
        peak = std::max(peak, std::abs(raw_multisine(i * 0.0001)));
    const double scale = 0.03 / peak;
    const std::array<std::string, 4> names{
        "fija", "chirp_anterior", "chirp_lineal", "multiseno_pico"
    };
    if (argc == 3) {
        if (std::string(argv[2]) != "check") throw std::runtime_error("Modo desconocido");
        for (int drive = 0; drive < static_cast<int>(names.size()); ++drive) {
            auto coarse = make_steps(drive, scale);
            auto fine = make_steps(drive, scale, true);
            std::mt19937_64 coarse_rng(2026), fine_rng(2026);
            double max_relative = 0;
            for (int i = 0; i < 10; ++i) {
                Result a = simulate(cases[i], coarse, coarse_rng);
                Result b = simulate(cases[i], fine, fine_rng);
                for (std::size_t j = 0; j < a.features.size(); ++j)
                    max_relative = std::max(max_relative,
                        std::abs(a.features[j] - b.features[j]) /
                        std::max(std::abs(b.features[j]), 1e-12));
            }
            std::cout << names[drive] << " max error relativo: " << max_relative << '\n';
        }
        return 0;
    }
    for (int drive = 0; drive < static_cast<int>(names.size()); ++drive) {
        auto events = make_steps(drive, scale);
        std::mt19937_64 rng(2026);
        std::ofstream out(dir + "/imu_" + names[drive] + ".csv");
        if (!out) throw std::runtime_error("No se pudo abrir la salida");
        out << "id,set,rep,ThetaMax,OmegaMax,AlphaMax,Etheta,Eomega,Td,R,rho,mu,clips\n";
        out << std::setprecision(12);
        for (std::size_t i = 0; i < cases.size(); ++i) {
            const auto& c = cases[i];
            const Result r = simulate(c, events, rng);
            out << c.id << ',' << c.set << ',' << c.rep;
            for (double value : r.features) out << ',' << value;
            out << ',' << c.rho << ',' << c.mu << ',' << r.clips << '\n';
            if ((i + 1) % 1000 == 0) std::cerr << names[drive] << ' ' << i+1 << "/9000\n";
        }
    }
    return 0;
}
