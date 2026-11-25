#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
constexpr double pi = 3.14159265358979323846;
constexpr double duration = 60.0;
constexpr double dt = 0.005;
constexpr int steps = static_cast<int>(duration / dt);
constexpr int cases = 5000;

struct Parameters {
    double rho;
    double mu;
};

struct Features {
    std::array<double, 7> value{};
};

enum class Drive { Fixed, ChirpLegacy, ChirpLinear, MultisineRms, MultisinePeak };

constexpr std::array<double, 9> frequencies{
    0.05, 0.1, 0.2, 0.4, 0.8, 1.6, 3.2, 6.4, 12.8
};
std::array<double, frequencies.size()> phases{};
double multisine_rms_scale = 1.0;
double multisine_peak_scale = 1.0;
double multisine_rms = 0.0;
double multisine_peak = 0.0;

double raw_multisine(double t) {
    double result = 0.0;
    for (std::size_t k = 0; k < frequencies.size(); ++k) {
        result += std::sin(2.0 * pi * frequencies[k] * t + phases[k]);
    }
    return result;
}

void initialize_multisine() {
    double sum_squares = 0.0;
    double peak = 0.0;
    for (std::size_t k = 0; k < phases.size(); ++k) {
        phases[k] = -pi * static_cast<double>(k * (k + 1)) /
                    static_cast<double>(frequencies.size());
    }
    for (int i = 0; i <= steps; ++i) {
        const double value = raw_multisine(i * dt);
        sum_squares += value * value;
        peak = std::max(peak, std::abs(value));
    }
    multisine_rms_scale = (0.03 / std::sqrt(2.0)) /
        std::sqrt(sum_squares / static_cast<double>(steps + 1));
    multisine_peak_scale = 0.03 / peak;
    multisine_peak = peak * multisine_peak_scale;
    multisine_rms = std::sqrt(sum_squares / static_cast<double>(steps + 1)) *
                    multisine_peak_scale;
}

double input(double t, Drive drive) {
    if (drive == Drive::Fixed) {
        return 0.03 * std::sin(2.0 * pi * t);
    }
    if (drive == Drive::ChirpLegacy) {
        const double frequency = 0.1 + (2.0 - 0.1) * std::min(t / duration, 1.0);
        return 0.03 * std::sin(2.0 * pi * frequency * t);
    }
    if (drive == Drive::ChirpLinear) {
        const double phase_cycles = 0.1 * t + (2.0 - 0.1) * t * t /
                                    (2.0 * duration);
        return 0.03 * std::sin(2.0 * pi * phase_cycles);
    }
    const double scale = drive == Drive::MultisineRms
        ? multisine_rms_scale : multisine_peak_scale;
    return scale * raw_multisine(t);
}

struct State {
    double theta;
    double omega;
};

State derivative(double t, State x, double inertia, double damping,
                 double stiffness, Drive drive) {
    return {
        x.omega,
        (0.02 * input(t, drive) - damping * x.omega -
         stiffness * std::sin(x.theta)) / inertia
    };
}

State add_scaled(State x, State dx, double scale) {
    return {x.theta + scale * dx.theta, x.omega + scale * dx.omega};
}

Features simulate(const Parameters& p, Drive drive) {
    const double inertia = 8e-5 + p.rho * 5e-8;
    const double stiffness = 5e-7 * p.rho;
    const double damping = 5e-3 * std::sqrt(p.mu / 0.02);
    State x{0.0, 0.0};
    std::vector<double> theta(steps + 1);
    std::vector<double> omega(steps + 1);
    double theta_max = 0.0;
    double omega_max = 0.0;
    double alpha_max = 0.0;
    double e_theta = 0.0;
    double e_omega = 0.0;

    for (int i = 0; i <= steps; ++i) {
        const double t = i * dt;
        theta[i] = x.theta;
        omega[i] = x.omega;
        theta_max = std::max(theta_max, std::abs(x.theta));
        omega_max = std::max(omega_max, std::abs(x.omega));
        const double alpha =
            (0.02 * input(t, drive) - damping * x.omega -
             stiffness * std::sin(x.theta)) / inertia;
        alpha_max = std::max(alpha_max, std::abs(alpha));

        if (i > 0) {
            e_theta += 0.5 * dt *
                (theta[i - 1] * theta[i - 1] + x.theta * x.theta);
            e_omega += 0.5 * dt *
                (omega[i - 1] * omega[i - 1] + x.omega * x.omega);
        }
        if (i == steps) break;

        const State k1 = derivative(t, x, inertia, damping, stiffness, drive);
        const State k2 = derivative(t + dt / 2.0,
            add_scaled(x, k1, dt / 2.0), inertia, damping, stiffness, drive);
        const State k3 = derivative(t + dt / 2.0,
            add_scaled(x, k2, dt / 2.0), inertia, damping, stiffness, drive);
        const State k4 = derivative(t + dt,
            add_scaled(x, k3, dt), inertia, damping, stiffness, drive);
        x.theta += dt / 6.0 *
            (k1.theta + 2.0 * k2.theta + 2.0 * k3.theta + k4.theta);
        x.omega += dt / 6.0 *
            (k1.omega + 2.0 * k2.omega + 2.0 * k3.omega + k4.omega);
    }

    int last_above = -1;
    const double threshold = 0.05 * theta_max;
    for (int i = 0; i <= steps; ++i) {
        if (std::abs(theta[i]) > threshold) last_above = i;
    }
    const double td = last_above < 0 ? 0.0 : last_above * dt;
    const double ratio = e_theta /
        (e_omega + std::numeric_limits<double>::epsilon());
    return {{{theta_max, omega_max, alpha_max, e_theta, e_omega, td, ratio}}};
}

void write_dataset(const std::string& path, const std::vector<Parameters>& params,
                   Drive drive) {
    std::ofstream out(path);
    if (!out) throw std::runtime_error("Cannot open output CSV: " + path);
    out << "ThetaMax,OmegaMax,AlphaMax,Etheta,Eomega,Td,R,rho,mu\n";
    out << std::setprecision(12);
    for (std::size_t i = 0; i < params.size(); ++i) {
        const Features f = simulate(params[i], drive);
        for (double value : f.value) out << value << ',';
        out << params[i].rho << ',' << params[i].mu << '\n';
        if ((i + 1) % 1000 == 0) {
            std::cerr << path << ": " << i + 1 << '/' << params.size() << '\n';
        }
    }
}
}  // namespace

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "Usage: comparar_excitaciones OUTPUT_DIR\n";
        return 2;
    }
    const std::string dir = argv[1];
    std::mt19937 rng(1);
    std::uniform_real_distribution<double> rho_dist(800.0, 1400.0);
    std::uniform_real_distribution<double> mu_dist(0.001, 0.100);
    std::vector<Parameters> params(cases);
    for (auto& p : params) p = {rho_dist(rng), mu_dist(rng)};
    initialize_multisine();
    std::cerr << "RMS-matched multisine peak: "
              << multisine_rms_scale * multisine_peak / multisine_peak_scale
              << "; peak-matched multisine RMS: " << multisine_rms
              << "; maximum frequency: " << frequencies.back() << " Hz\n";
    write_dataset(dir + "/frecuencia_fija_1hz.csv", params, Drive::Fixed);
    write_dataset(dir + "/chirp_anterior.csv", params, Drive::ChirpLegacy);
    write_dataset(dir + "/chirp_lineal.csv", params, Drive::ChirpLinear);
    write_dataset(dir + "/multisine_rmsmatched.csv", params, Drive::MultisineRms);
    write_dataset(dir + "/multisine_peakmatched.csv", params, Drive::MultisinePeak);
}
