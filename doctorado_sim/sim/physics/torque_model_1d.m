function tau = torque_model_1d(theta, omega, p)
% Modelo 1DoF simplificado:
% I*theta_ddot = tau_rest + tau_damp + tau_drag_nl + tau_noise

dtheta = theta - p.theta0_rad;

% Restaurador: lineal + seno (elige uno con weight)
tau_lin  = -p.k_lin * dtheta;
tau_sin  = -p.k_sin * sin(dtheta);
tau_rest = p.w_lin * tau_lin + (1-p.w_lin) * tau_sin;

% Amortiguamiento viscoso efectivo (mu influye)
c_eff = p.c0 + p.c_mu_gain * p.mu_pas;
tau_damp = -c_eff * omega;

% Arrastre no lineal
tau_drag = -p.c_quad * abs(omega) * omega;

% Ruido de perturbación (torque ambiental)
tau_noise = p.tau_noise_std * randn();

tau = tau_rest + tau_damp + tau_drag + tau_noise;
end
