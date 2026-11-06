function out = dynamics_circular_walls(cfg)
m = circular_wall_modes(cfg);
n = cfg.n_modes;
count = n+1;
x0 = m.initial_delta_rad;
% Agua en equilibrio estatico con la capsula sostenida antes de soltarla.
position0 = [x0; m.coupling_m*sin(x0)];
y0 = [position0; zeros(count, 1); 0];
times = (0:1/cfg.fs_hz:cfg.duration_s)';
if times(end) < cfg.duration_s
    times(end+1) = cfg.duration_s;
end
options = odeset('RelTol', 1e-8, 'AbsTol', 1e-11, ...
    'MaxStep', 1/(15*max(m.frequency_hz)));
[t, y] = ode45(@rhs, times, y0, options);
x = y(:, 1);
q = y(:, 2:count);
vel = y(:, count+1:2*count);
delta = q-sin(x)*m.coupling_m';
out.t_s = t;
out.theta_rad = cfg.equilibrium_rad+x;
out.omega_rads = vel(:, 1);
out.wave_modes_m = q;
out.modes = m;
out.capsule_energy_j = 0.5*cfg.I_kgm2*vel(:, 1).^2 + ...
    m.capsule_k_nm*(1-cos(x));
out.water_energy_j = 0.5*(vel(:, 2:end).^2*m.mass_kg + q.^2*m.stiffness_n_m);
out.interaction_energy_j = 0.5*((delta.^2-q.^2)*m.stiffness_n_m);
out.total_energy_j = out.capsule_energy_j + ...
    0.5*(vel(:, 2:end).^2*m.mass_kg + delta.^2*m.stiffness_n_m);
out.dissipated_energy_j = y(:, end);
out.balance_error_j = out.total_energy_j+y(:, end)-out.total_energy_j(1);
out.feedback_torque_nm = cos(x).*(delta*(m.stiffness_n_m.*m.coupling_m));
out.dissipation_w = 2*cfg.I_kgm2*cfg.capsule_decay_s_inv*vel(:, 1).^2 + ...
    vel(:, 2:end).^2*m.damping_kg_s;

    function dy = rhs(~, state)
        position = state(1:count);
        velocity = state(count+1:2*count);
        mismatch = position(2:end)-m.coupling_m*sin(position(1));
        torque = -m.capsule_k_nm*sin(position(1)) + ...
            cos(position(1))*sum(m.stiffness_n_m.*m.coupling_m.*mismatch);
        acceleration = [(torque-2*cfg.I_kgm2*cfg.capsule_decay_s_inv*velocity(1))/cfg.I_kgm2; ...
            (-m.stiffness_n_m.*mismatch-m.damping_kg_s.*velocity(2:end))./m.mass_kg];
        losses = 2*cfg.I_kgm2*cfg.capsule_decay_s_inv*velocity(1)^2 + ...
            sum(m.damping_kg_s.*velocity(2:end).^2);
        dy = [velocity; acceleration; losses];
    end
end
