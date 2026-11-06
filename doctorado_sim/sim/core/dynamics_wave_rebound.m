function out = dynamics_wave_rebound(cfg)
% Dos osciladores pasivos; q es una coordenada modal equivalente en radianes.
positive = {'duration_s', 'fs_hz', 'I_capsule_kgm2', 'I_wave_kgm2', ...
    'k_capsule_nm_rad', 'k_wave_nm_rad'};
nonnegative = {'k_coupling_nm_rad', 'c_capsule_nms_rad', 'c_wave_nms_rad'};
initial = {'theta_eq_rad', 'theta_init_rad', 'omega_init_rads', ...
    'wave_init_rad', 'wave_rate_init_rads'};
names = [positive, nonnegative, initial];
for i = 1:numel(names)
    name = names{i};
    if ~isfield(cfg, name) || ~isnumeric(cfg.(name)) || ...
            ~isreal(cfg.(name)) || ~isscalar(cfg.(name)) || ~isfinite(cfg.(name))
        error('wave_rebound:InvalidConfig', 'Parametro finito escalar requerido: %s', name);
    end
end
for i = 1:numel(positive)
    if cfg.(positive{i}) <= 0
        error('wave_rebound:InvalidConfig', '%s debe ser positivo.', positive{i});
    end
end
for i = 1:numel(nonnegative)
    if cfg.(nonnegative{i}) < 0
        error('wave_rebound:InvalidConfig', '%s no puede ser negativo.', nonnegative{i});
    end
end
if cfg.duration_s*cfg.fs_hz < 1
    error('wave_rebound:InvalidConfig', 'La duracion debe cubrir al menos un intervalo.');
end

M = diag([cfg.I_capsule_kgm2, cfg.I_wave_kgm2]);
C = diag([cfg.c_capsule_nms_rad, cfg.c_wave_nms_rad]);
kc = cfg.k_coupling_nm_rad;
K = [cfg.k_capsule_nm_rad + kc, -kc; -kc, cfg.k_wave_nm_rad + kc];
% Estado: [x; q; velocidad_x; velocidad_q; energia_disipada].
rhs = @(t, y) [y(3:4); -M\(C*y(3:4) + K*y(1:2)); ...
    y(3:4)'*C*y(3:4)];
y0 = [cfg.theta_init_rad - cfg.theta_eq_rad; cfg.wave_init_rad; ...
    cfg.omega_init_rads; cfg.wave_rate_init_rads; 0];
t = (0:1/cfg.fs_hz:cfg.duration_s)';
if t(end) < cfg.duration_s
    t(end+1) = cfg.duration_s;
end
options = odeset('RelTol', 1e-9, 'AbsTol', 1e-12);
[out.t_s, y] = ode45(rhs, t, y0, options);
out.theta_rad = cfg.theta_eq_rad + y(:, 1);
out.omega_rads = y(:, 3);
out.wave_rad = y(:, 2);
out.wave_rate_rads = y(:, 4);
out.return_torque_nm = kc*(y(:, 2) - y(:, 1));
out.capsule_energy_j = 0.5*cfg.I_capsule_kgm2*y(:, 3).^2 + ...
    0.5*cfg.k_capsule_nm_rad*y(:, 1).^2;
out.wave_energy_j = 0.5*cfg.I_wave_kgm2*y(:, 4).^2 + ...
    0.5*cfg.k_wave_nm_rad*y(:, 2).^2;
out.coupling_energy_j = 0.5*kc*(y(:, 1) - y(:, 2)).^2;
out.total_energy_j = out.capsule_energy_j + out.wave_energy_j + out.coupling_energy_j;
out.dissipated_energy_j = y(:, 5);
out.dissipation_w = cfg.c_capsule_nms_rad*y(:, 3).^2 + ...
    cfg.c_wave_nms_rad*y(:, 4).^2;
out.balance_error_j = out.total_energy_j + y(:, 5) - out.total_energy_j(1);
out.undamped_modal_hz = sort(sqrt(eig(K, M)))/(2*pi);
end
