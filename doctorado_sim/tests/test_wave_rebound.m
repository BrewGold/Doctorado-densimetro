function test_wave_rebound()
sim_root = fileparts(fileparts(mfilename('fullpath')));
addpath(fullfile(sim_root, 'sim', 'core'));
addpath(fullfile(sim_root, 'sim', 'scenarios'));
cfg = wave_rebound_config();
out = dynamics_wave_rebound(cfg);
e0 = out.total_energy_j(1);
assert(all(isfinite(out.theta_rad)));
assert(numel(out.t_s) == 8001);
assert(max(diff(out.total_energy_j)) < 1e-8*e0);
assert(max(abs(out.balance_error_j)) < 1e-6*e0);
assert(all(out.dissipation_w >= 0));
assert(out.total_energy_j(end) < 0.1*e0);
assert(all(diff(out.dissipated_energy_j) >= -1e-10*e0));
assert(abs(out.undamped_modal_hz(1)-1.9) < 1e-10);
assert(diff(out.undamped_modal_hz) > 0.04);
% La capsula recupera amplitud tras transferir energia al agua.
x = abs(out.theta_rad-cfg.theta_eq_rad);
minimum_window = max(x(out.t_s >= 9 & out.t_s <= 12));
return_window = max(x(out.t_s >= 19 & out.t_s <= 23));
assert(return_window > 1.5*minimum_window);

isolated_cfg = cfg;
isolated_cfg.k_coupling_nm_rad = 0;
isolated = dynamics_wave_rebound(isolated_cfg);
alpha = cfg.c_capsule_nms_rad/(2*cfg.I_capsule_kgm2);
wd = sqrt(cfg.k_capsule_nm_rad/cfg.I_capsule_kgm2-alpha^2);
a = cfg.theta_init_rad-cfg.theta_eq_rad;
expected = cfg.theta_eq_rad + a*exp(-alpha*isolated.t_s).* ...
    (cos(wd*isolated.t_s)+alpha/wd*sin(wd*isolated.t_s));
assert(max(abs(isolated.theta_rad-expected)) < 1e-7);
assert(max(abs(isolated.wave_rad)) == 0);

conservative_cfg = cfg;
conservative_cfg.c_capsule_nms_rad = 0;
conservative_cfg.c_wave_nms_rad = 0;
conservative = dynamics_wave_rebound(conservative_cfg);
assert(max(abs(conservative.total_energy_j-e0)) < 1e-6*e0);
assert(max(abs(conservative.dissipated_energy_j)) == 0);

rest_cfg = cfg;
rest_cfg.theta_init_rad = rest_cfg.theta_eq_rad;
rest = dynamics_wave_rebound(rest_cfg);
assert(max(abs(rest.theta_rad-rest_cfg.theta_eq_rad)) == 0);
assert(max(abs(rest.total_energy_j)) == 0);

invalid_cfg = cfg;
invalid_cfg.c_wave_nms_rad = -1;
caught = false;
try
    dynamics_wave_rebound(invalid_cfg);
catch err
    caught = strcmp(err.identifier, 'wave_rebound:InvalidConfig');
end
assert(caught, 'Debe rechazarse el amortiguamiento negativo.');
disp('OK: solucion analitica, rebote, disipacion, conservacion y validacion.');
end
