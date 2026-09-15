function out = dynamics_1d(cfg)
% Integración Euler explícita para MVP
% Estados: theta, omega

N  = cfg.N;
dt = cfg.dt;

theta = zeros(N,1);
omega = zeros(N,1);
alpha = zeros(N,1);
t     = (0:N-1)' * dt;

theta(1) = cfg.theta_init_rad;
omega(1) = cfg.omega_init_rads;

for k = 1:N-1
    tau = torque_model_1d(theta(k), omega(k), cfg.p);
    alpha(k) = tau / cfg.p.I_kgm2;

    omega(k+1) = omega(k) + dt * alpha(k);
    theta(k+1) = theta(k) + dt * omega(k+1);
end

alpha(N) = alpha(N-1);

out = table(t, theta, omega, alpha, ...
    'VariableNames', {'t_s','theta_true_rad','omega_true_rads','alpha_true_rads2'});
end
