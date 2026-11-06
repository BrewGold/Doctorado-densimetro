function test_circular_walls()
root = fileparts(fileparts(mfilename('fullpath')));
addpath(fullfile(root, 'sim', 'core'), fullfile(root, 'sim', 'physics'), ...
    fullfile(root, 'sim', 'scenarios'));
cfg = circular_wall_config();
m = circular_wall_modes(cfg);
assert(abs(m.roots(1)-1.841183781340659) < 1e-10);
assert(max(abs((besselj(0, m.roots)-besselj(2, m.roots))/2)) < 1e-12);
beta = m.geometric_equilibrium_rad;
assert(abs(cfg.capsule_length_m*(sin(beta+m.initial_delta_rad)-sin(beta))-0.05) < 1e-14);
assert(abs(m.initial_delta_rad*180/pi-30) < 1e-12);
assert(beta*180/pi > 34 && beta*180/pi < 36);
assert(m.frequency_hz(1) > 1.90 && m.frequency_hz(1) < 1.92);
assert(m.center_roundtrip_s > 0.4 && m.center_roundtrip_s < 0.5);
assert(m.edge_roundtrip_s < m.center_roundtrip_s);
R = cfg.diameter_m/2;
normalization = pi*integral(@(r) r.*(besselj(1, m.k_m_inv(1)*r)/besselj(1, m.roots(1))).^2, 0, R);
assert(abs(m.mass_kg(1)-cfg.rho_kgm3*normalization/ ...
    (m.k_m_inv(1)*tanh(m.k_m_inv(1)*cfg.depth_m))) < 1e-10);
omega = @(k) sqrt((cfg.g_ms2*k+cfg.sigma_npm/cfg.rho_kgm3*k.^3).*tanh(k*cfg.depth_m));
k = m.reference_k_m_inv;
numeric_group = (omega(k+1e-4)-omega(k-1e-4))/2e-4;
assert(abs(m.reference_group_ms-numeric_group) < 1e-8);

cfg.duration_s = 8;
out = dynamics_circular_walls(cfg);
e0 = out.total_energy_j(1);
assert(all(isfinite(out.theta_rad)));
assert(max(abs(out.balance_error_j))/e0 < 1e-6);
assert(max(diff(out.total_energy_j))/e0 < 1e-7);
assert(all(out.dissipation_w >= 0));
assert(max(abs(out.capsule_energy_j+out.water_energy_j+out.interaction_energy_j - ...
    out.total_energy_j))/e0 < 1e-12);
surface = circular_wall_surface(out, [0, R, R], [0, 0, pi]);
assert(max(abs(surface(:, 1))) == 0);
assert(max(abs(surface(:, 2)+surface(:, 3))) < 1e-14);
% Un dipolo m=1 conserva el volumen de agua y cumple la condicion de pared.
dr = 1e-6;
near_wall = circular_wall_surface(out, [R, R-dr], [0, 0]);
assert(max(abs(diff(near_wall, 1, 2)/dr)) < 1e-5);

isolated_cfg = cfg;
isolated_cfg.coupling_fraction = 0;
isolated = dynamics_circular_walls(isolated_cfg);
assert(max(abs(isolated.wave_modes_m(:))) == 0);
assert(max(abs(out.theta_rad-isolated.theta_rad)) > 1e-3);

conservative_cfg = cfg;
conservative_cfg.capsule_decay_s_inv = 0;
conservative_cfg.wave_extra_decay_s_inv = 0;
conservative_cfg.mu_pas = 0;
conservative = dynamics_circular_walls(conservative_cfg);
assert(max(abs(conservative.total_energy_j-conservative.total_energy_j(1)))/ ...
    conservative.total_energy_j(1) < 1e-6);
assert(max(abs(conservative.dissipated_energy_j)) == 0);

shifted_cfg = cfg;
shifted_cfg.equilibrium_rad = cfg.equilibrium_rad+0.5;
shifted = dynamics_circular_walls(shifted_cfg);
assert(max(abs(shifted.theta_rad-out.theta_rad-0.5)) < 1e-12);

more_modes = cfg;
more_modes.n_modes = 12;
more_modes.fs_hz = 200;
fine = dynamics_circular_walls(more_modes);
assert(max(abs(fine.theta_rad(1:2:end)-out.theta_rad)) < 1e-6);
for depth = [0.03, 0.05, 0.12]
    changed = cfg;
    changed.depth_m = depth;
    md = circular_wall_modes(changed);
    if depth < cfg.depth_m
        assert(md.frequency_hz(1) < m.frequency_hz(1));
    else
        assert(md.frequency_hz(1) > m.frequency_hz(1));
    end
end
for name = {'end_lift_m', 'depth_m', 'mu_pas', 'fs_hz'}
    invalid = cfg;
    if strcmp(name{1}, 'end_lift_m')
        invalid.(name{1}) = 0.15;
    else
        invalid.(name{1}) = -1;
    end
    caught = false;
    try
        circular_wall_modes(invalid);
    catch err
        caught = strcmp(err.identifier, 'circular_walls:InvalidConfig');
    end
    assert(caught, ['Configuracion invalida no rechazada: ', name{1}]);
end
disp('OK: geometria, dispersion, paredes, energia, desacoplamiento y convergencia modal.');
end
