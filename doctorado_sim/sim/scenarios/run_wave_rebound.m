function run_wave_rebound(output_dir)
% Ejecutar desde cualquier directorio, sin cambiar el baseline existente.
sim_root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(fullfile(sim_root, 'sim', 'core'));
addpath(fullfile(sim_root, 'sim', 'scenarios'));
if nargin < 1
    output_dir = fullfile(sim_root, 'results', 'wave_rebound');
end
if ~exist(output_dir, 'dir')
    mkdir(output_dir);
end
cfg = wave_rebound_config();
coupled = dynamics_wave_rebound(cfg);
isolated_cfg = cfg;
isolated_cfg.k_coupling_nm_rad = 0;
isolated = dynamics_wave_rebound(isolated_cfg);
t = coupled.t_s;
x = (coupled.theta_rad - cfg.theta_eq_rad)*180/pi;
x0 = (isolated.theta_rad - cfg.theta_eq_rad)*180/pi;
alpha = cfg.c_capsule_nms_rad/(2*cfg.I_capsule_kgm2);
wd = sqrt(cfg.k_capsule_nm_rad/cfg.I_capsule_kgm2 - alpha^2);
a = cfg.theta_init_rad - cfg.theta_eq_rad;
b = (cfg.omega_init_rads + alpha*a)/wd;
envelope = sqrt(a^2+b^2)*exp(-alpha*t)*180/pi;

data = [t, coupled.theta_rad, isolated.theta_rad, coupled.omega_rads, ...
    coupled.wave_rad, coupled.wave_rate_rads, coupled.return_torque_nm, ...
    coupled.capsule_energy_j, coupled.wave_energy_j, coupled.coupling_energy_j, ...
    coupled.total_energy_j, coupled.dissipated_energy_j, coupled.balance_error_j];
filename = fullfile(output_dir, 'wave_rebound.csv');
fid = fopen(filename, 'w');
if fid < 0
    error('wave_rebound:OutputError', 'No se puede escribir %s', filename);
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, ['t_s,theta_coupled_rad,theta_isolated_rad,omega_rads,' ...
    'wave_equivalent_rad,wave_rate_rads,return_torque_nm,capsule_energy_j,' ...
    'wave_energy_j,coupling_energy_j,total_energy_j,dissipated_energy_j,balance_error_j\n']);
fprintf(fid, [repmat('%.12g,', 1, size(data, 2)-1), '%.12g\n'], data');
clear cleanup;

fig = figure('Visible', 'off', 'Position', [100, 100, 1100, 1000]);
fig_cleanup = onCleanup(@() close(fig));
set(fig, 'PaperUnits', 'inches', 'PaperPosition', [0, 0, 11, 10], ...
    'PaperSize', [11, 10]);
subplot(4, 1, 1);
plot(t, x0, 'b', t, envelope, 'r--', t, -envelope, 'r--');
grid on; ylabel('x [deg]'); title('Sin acoplamiento: decaimiento de un modo');
subplot(4, 1, 2);
plot(t, x, 'b'); grid on; ylabel('x [deg]');
title('Con modo del agua: recuperaciones de amplitud, sin aporte externo');
subplot(4, 1, 3);
plot(t, coupled.wave_rad*180/pi, 'c');
grid on; ylabel('q [deg equivalentes]');
title('Coordenada del agua: no es altura de ola ni angulo medido');
subplot(4, 1, 4);
plot(t, coupled.capsule_energy_j, t, coupled.wave_energy_j, ...
    t, coupled.total_energy_j, 'k', t, coupled.dissipated_energy_j, '--');
grid on; xlabel('t [s]'); ylabel('Energia [J]');
legend('Capsula', 'Agua', 'Total mecanica', 'Disipada', 'Location', 'northeast');
print(fig, fullfile(output_dir, 'wave_rebound.png'), '-dpng', '-r130');
print(fig, fullfile(output_dir, 'wave_rebound.pdf'), '-dpdf');
fprintf('Frecuencias modales sin amortiguamiento: %.4f, %.4f Hz\n', ...
    coupled.undamped_modal_hz);
fprintf('Escala de batido sin amortiguamiento: %.2f s\n', ...
    1/diff(coupled.undamped_modal_hz));
fprintf('Error relativo maximo de balance energetico: %.3g\n', ...
    max(abs(coupled.balance_error_j))/coupled.total_energy_j(1));
fprintf('Resultados exploratorios, no ajustados a los datos: %s\n', output_dir);
end
