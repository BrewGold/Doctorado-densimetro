#include <algorithm>
#include <cmath>
#include <cstddef>
#include <iostream>
#include <stdexcept>

namespace {
constexpr double pi = 3.14159265358979323846;
constexpr double gravity = 9.80665;
constexpr double pulse_amplitude = 0.003;
constexpr double gamma0 = 0.06447;
constexpr double wd0 = 2*pi*1.89991;
constexpr double i0 = 8e-5 + 1000*5e-8;
constexpr double k0 = i0*(wd0*wd0+gamma0*gamma0);
constexpr double c0 = 2*i0*gamma0;
constexpr double alpha = 1 - std::exp(-2*pi*20/104);
constexpr int sensor_count = 15*104+1;
constexpr int host_count = 15*100+1;

struct Plant {
    double theta = 0, omega = 0;
    double gamma, wd, acceleration;

    Plant(double rho, double mu) {
        double inertia = 8e-5 + rho*5e-8;
        double k = k0*rho/1000;
        double c = c0*std::sqrt(mu/0.02);
        gamma = c/(2*inertia);
        wd = std::sqrt(k/inertia-gamma*gamma);
        acceleration = 0.02/inertia;
    }

    void advance(double h, double u) {
        const double equilibrium = acceleration*u/(wd*wd+gamma*gamma);
        const double e = std::exp(-gamma*h), cs = std::cos(wd*h);
        const double sn = std::sin(wd*h), q = theta-equilibrium;
        const double next_theta = equilibrium + e*(q*(cs+gamma*sn/wd)+omega*sn/wd);
        const double next_omega = e*(omega*(cs-gamma*sn/wd)
            -q*(wd*wd+gamma*gamma)*sn/wd);
        theta = next_theta;
        omega = next_omega;
    }
};

double angle_eq(double rho) {
    return -0.9746388227722308
        -0.45*std::atan(0.0021440041612968324*(rho-1000)/0.45);
}
double quantize(double x, double step) { return std::round(x/step)*step; }

void simulate(double rho, double mu, int mode, const double* noise,
              const double* biases, const double* fixed_input,
              const double* disturbance,
              double* angles, double* gyro, double* input, double* frequencies,
              int* clips) {
    Plant plant(rho, mu);
    const double equilibrium = angle_eq(rho);
    const double quantum_a = 0.000061*gravity;
    const double quantum_g = 0.00875*pi/180;
    const double limit_g = 250*pi/180;
    double ax = gravity*std::sin(equilibrium) + biases[0] + noise[0];
    double az = gravity*std::cos(equilibrium) + biases[1] + noise[sensor_count];
    double omega = biases[2] + noise[2*sensor_count];
    double phase = 0, frequency = mode == 1 ? 1.9 : 1.7, in_phase = 0, quadrature = 0;
    double current_input = fixed_input ? fixed_input[0] :
        (mode == 0 ? pulse_amplitude : 0);
    double last_host_phase = 0;
    angles[0] = fixed_input ? std::atan2(ax,az)
        : std::atan2(quantize(ax, quantum_a),quantize(az, quantum_a));
    gyro[0] = quantize(omega,quantum_g);
    input[0] = current_input;
    frequencies[0] = mode == 0 ? 0 : frequency;
    *clips = 0;
    int last_tick = 0, host_index = 0, sensor_index = 0;
    for (int tick = 1; tick <= 15*2600; ++tick) {
        bool sensor = tick%25 == 0, host = tick%26 == 0;
        if (!sensor && !host) continue;
        double h = (tick-last_tick)/2600.0;
        plant.advance(h,current_input + (disturbance ? disturbance[host_index] : 0));
        phase += 2*pi*frequency*h;
        if (sensor) {
            ++sensor_index;
            double raw_ax = gravity*std::sin(equilibrium+plant.theta)
                +biases[0]+noise[sensor_index];
            double raw_az = gravity*std::cos(equilibrium+plant.theta)
                +biases[1]+noise[sensor_count+sensor_index];
            double raw_g = plant.omega+biases[2]+noise[2*sensor_count+sensor_index];
            if (std::abs(raw_ax)>2*gravity || std::abs(raw_az)>2*gravity
                || std::abs(raw_g)>limit_g) ++*clips;
            raw_ax = std::clamp(raw_ax,-2*gravity,2*gravity);
            raw_az = std::clamp(raw_az,-2*gravity,2*gravity);
            raw_g = std::clamp(raw_g,-limit_g,limit_g);
            ax += alpha*(raw_ax-ax);
            az += alpha*(raw_az-az);
            omega += alpha*(raw_g-omega);
        }
        if (host) {
            ++host_index;
            angles[host_index] = fixed_input ? std::atan2(ax,az)
                : std::atan2(quantize(ax,quantum_a),quantize(az,quantum_a));
            gyro[host_index] = quantize(omega,quantum_g);
            if (fixed_input) {
                current_input = fixed_input[host_index];
            } else if (mode == 0) {
                current_input = tick < 520 ? pulse_amplitude : 0;
            } else if (mode == 1) {
                current_input = pulse_amplitude*std::sin(phase);
            } else {
                // Demodulate against the previously held command phase.
                const double beta = 1-std::exp(-0.01/0.8);
                in_phase += beta*(gyro[host_index]*std::sin(last_host_phase)-in_phase);
                quadrature += beta*(gyro[host_index]*std::cos(last_host_phase)-quadrature);
                if (tick >= 2600) {
                    // Negative gyro phase above resonance; increase f for positive phase.
                    const double error = std::atan2(quadrature,in_phase)+0.05;
                    frequency = std::clamp(frequency+0.015*error*0.01,1.4,2.4);
                }
                last_host_phase = phase;
                current_input = pulse_amplitude*std::sin(phase);
            }
            input[host_index] = current_input;
            frequencies[host_index] = mode == 0 ? 0 : frequency;
        }
        last_tick = tick;
    }
    if (sensor_index != sensor_count-1 || host_index != host_count-1)
        throw std::runtime_error("Muestreo incorrecto");
}
}  // namespace

extern "C" int simulate_closed_loop(
        double rho, double mu, int mode, const double* noise, const double* biases,
        const double* disturbance,
        double* angles, double* gyro, double* input, double* frequencies, int* clips) {
    try {
        simulate(rho,mu,mode,noise,biases,nullptr,disturbance,
                 angles,gyro,input,frequencies,clips);
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "simulate_closed_loop: " << e.what() << '\n';
        return 1;
    }
}

extern "C" int predict_closed_loop(
        double rho, double mu, const double* input, double* angles) {
    try {
        double noise[3*sensor_count]{}, biases[3]{};
        double gyro[host_count], copied_input[host_count], frequencies[host_count];
        int clips;
        simulate(rho,mu,0,noise,biases,input,nullptr,
                 angles,gyro,copied_input,frequencies,&clips);
        return clips ? 2 : 0;
    } catch (const std::exception& e) {
        std::cerr << "predict_closed_loop: " << e.what() << '\n';
        return 1;
    }
}
