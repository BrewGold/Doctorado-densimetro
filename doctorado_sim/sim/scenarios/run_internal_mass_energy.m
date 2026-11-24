function run_internal_mass_energy(output_dir)
sim_root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(fullfile(sim_root, 'sim', 'core'));
addpath(fullfile(sim_root, 'sim', 'scenarios'));
if nargin < 1
    output_dir = fullfile(sim_root, 'results', 'internal_mass');
end
if ~exist(output_dir, 'dir')
    mkdir(output_dir);
end
cfg = internal_mass_config();
axial = dynamics_internal_mass(cfg, [1; 0]);
vertical = dynamics_internal_mass(cfg, [sin(cfg.beta_eq_rad); cos(cfg.beta_eq_rad)]);
a = internal_mass_kinetic_energy(cfg, axial);
v = internal_mass_kinetic_energy(cfg, vertical);
t = axial.t_s;
data = [t, a.total_j, v.total_j, a.com_translation_j, v.com_translation_j, ...
    a.relative_j, v.relative_j, a.shell_rotation_j, v.shell_rotation_j];
filename = fullfile(output_dir, 'kinetic_energy.csv');
fid = fopen(filename, 'w');
if fid < 0
    error('internal_mass:OutputError', 'No se puede escribir %s', filename);
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, ['t_s,axial_total_j,vertical_total_j,axial_com_translation_j,' ...
    'vertical_com_translation_j,axial_relative_j,vertical_relative_j,' ...
    'axial_shell_rotation_j,vertical_shell_rotation_j\n']);
fprintf(fid, [repmat('%.12g,', 1, size(data, 2)-1), '%.12g\n'], data');
clear cleanup;
post = t >= cfg.stroke_duration_s & t <= cfg.stroke_duration_s + 2;
fprintf('Maximo total durante el movimiento (uJ): axial %.6f, vertical %.6f\n', ...
    max(a.total_j(t < cfg.stroke_duration_s))*1e6, max(v.total_j(t < cfg.stroke_duration_s))*1e6);
fprintf('Maximo total durante los 2 s posteriores (uJ): axial %.6f, vertical %.6f\n', ...
    max(a.total_j(post))*1e6, max(v.total_j(post))*1e6);
fprintf('Maximo relativo durante los 2 s posteriores (uJ): axial %.6f, vertical %.6f\n', ...
    max(a.relative_j(post))*1e6, max(v.relative_j(post))*1e6);
fig = figure('Visible', 'off', 'Position', [100, 100, 1100, 900]);
cleanup_fig = onCleanup(@() close(fig));
set(fig, 'PaperUnits', 'inches', 'PaperPosition', [0, 0, 11, 9], ...
    'PaperSize', [11, 9]);
subplot(3, 1, 1);
plot(t, axial.mass_displacement_m*1000, 'k', 'LineWidth', 1.1);
xlim([0, 1]); grid on; ylabel('Recorrido [mm]');
title('Masa movil: mismo impulso de ida y vuelta');
subplot(3, 1, 2);
plot(t, axial.angle_rad*180/pi, 'b', t, vertical.angle_rad*180/pi, 'r', 'LineWidth', 1.1);
xlim([cfg.stroke_duration_s, cfg.stroke_duration_s+2]);
grid on; ylabel('Angulo [grados]');
title('Balanceo despues del retorno de la masa');
legend('Longitudinal', 'Vertical en reposo', 'Location', 'northeast');
subplot(3, 1, 3);
plot(t, a.relative_j*1e6, 'b', t, v.relative_j*1e6, 'r', 'LineWidth', 1.1);
xlim([cfg.stroke_duration_s, cfg.stroke_duration_s+2]);
ylim([0, 1.1e6*max([a.relative_j(post); v.relative_j(post)]) + eps]);
grid on; ylabel('Energia [microJ]'); xlabel('Tiempo [s]');
title('Energia cinetica de giro respecto al centro de masas');
print(fig, fullfile(output_dir, 'kinetic_energy.png'), '-dpng', '-r130');
end
