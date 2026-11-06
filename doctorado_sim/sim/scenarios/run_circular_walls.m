function run_circular_walls(output_dir)
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(fullfile(root, 'sim', 'core'), fullfile(root, 'sim', 'physics'), ...
    fullfile(root, 'sim', 'scenarios'));
if nargin < 1
    output_dir = fullfile(root, 'results', 'circular_walls');
end
if ~exist(output_dir, 'dir')
    mkdir(output_dir);
end
cfg = circular_wall_config();
walls = dynamics_circular_walls(cfg);
isolated_cfg = cfg;
isolated_cfg.coupling_fraction = 0;
isolated = dynamics_circular_walls(isolated_cfg);
lossy_cfg = cfg;
lossy_cfg.wave_extra_decay_s_inv = 1.5;
lossy = dynamics_circular_walls(lossy_cfg);
R = cfg.diameter_m/2;
diameter = linspace(-R, R, 201);
eta = circular_wall_surface(walls, abs(diameter), pi*(diameter < 0));
t = walls.t_s;
initial_energy = walls.total_energy_j(1);

write_csv(fullfile(output_dir, 'capsule_walls.csv'), ...
    ['t_s,theta_model_walls_rad,theta_model_isolated_rad,theta_model_lossy_water_rad,' ...
    'omega_rads,eta_right_wall_m,feedback_torque_nm,capsule_energy_j,' ...
    'water_energy_j,interaction_energy_j,total_energy_j,dissipated_energy_j,balance_error_j'], ...
    [t, walls.theta_rad, isolated.theta_rad, lossy.theta_rad, walls.omega_rads, ...
    eta(:, end), walls.feedback_torque_nm, walls.capsule_energy_j, ...
    walls.water_energy_j, walls.interaction_energy_j, walls.total_energy_j, ...
    walls.dissipated_energy_j, walls.balance_error_j]);
m = walls.modes;
write_csv(fullfile(output_dir, 'water_modes.csv'), ...
    'mode,k_m_inv,frequency_hz,decay_s_inv,mass_kg,stiffness_n_m,coupling_m', ...
    [(1:cfg.n_modes)', m.k_m_inv, m.frequency_hz, m.decay_s_inv, ...
    m.mass_kg, m.stiffness_n_m, m.coupling_m]);
write_csv(fullfile(output_dir, 'water_surface.csv'), ...
    't_s,x_m,eta_m', [repmat(t, numel(diameter), 1), ...
    kron(diameter', ones(numel(t), 1)), eta(:)]);

fig = figure('Visible', 'off', 'Position', [100, 100, 1200, 1000]);
clean_fig = onCleanup(@() close(fig));
set(fig, 'PaperUnits', 'inches', 'PaperPosition', [0, 0, 12, 10], 'PaperSize', [12, 10]);
subplot(4, 1, 1);
plot(t, (walls.theta_rad-cfg.equilibrium_rad)*180/pi, 'b', ...
    t, (isolated.theta_rad-cfg.equilibrium_rad)*180/pi, 'r--');
grid on; ylabel('x [deg]');
title('Capsula: pared circular frente a ausencia de acoplamiento');
legend('Agua con paredes', 'Capsula aislada');
subplot(4, 1, 2);
plot(t, (walls.theta_rad-cfg.equilibrium_rad)*180/pi, 'b', ...
    t, (lossy.theta_rad-cfg.equilibrium_rad)*180/pi, 'g');
grid on; ylabel('x [deg]');
title('Sensibilidad a perdidas del agua (no es una frontera absorbente)');
legend('Perdidas bajas', 'Perdidas altas');
subplot(4, 1, 3);
imagesc(diameter*100, t(t <= 3), 1000*eta(t <= 3, :));
axis xy; colorbar; xlabel('Posicion sobre el diametro [cm]'); ylabel('t [s]');
title('Elevacion del agua [mm]: modos que satisfacen la pared reflectante');
subplot(4, 1, 4);
plot(t, walls.total_energy_j/initial_energy, 'k', ...
    t, walls.dissipated_energy_j/initial_energy, 'r--', ...
    t, (walls.total_energy_j+walls.dissipated_energy_j)/initial_energy, 'b:');
grid on; xlabel('t [s]'); ylabel('E / E inicial');
legend('Mecanica total', 'Disipada', 'Suma');
print(fig, fullfile(output_dir, 'circular_walls.png'), '-dpng', '-r130');
print(fig, fullfile(output_dir, 'circular_walls.pdf'), '-dpdf');
clear clean_fig;

% Corte geometrico: solamente ilustra la conversion de elevacion a angulo.
fig = figure('Visible', 'off', 'Position', [100, 100, 1000, 700]);
clean_fig = onCleanup(@() close(fig));
set(fig, 'PaperUnits', 'inches', 'PaperPosition', [0, 0, 10, 7], 'PaperSize', [10, 7]);
subplot(2, 1, 1); hold on;
plot(100*[-R, -R, R, R], 100*[0.11, -cfg.depth_m, -cfg.depth_m, 0.11], 'k');
plot(100*[-R, R], [0, 0], 'c--');
beta = m.geometric_equilibrium_rad;
weighted = -cfg.capsule_length_m/2*[cos(beta), sin(beta)];
tip_eq = weighted + cfg.capsule_length_m*[cos(beta), sin(beta)];
angle = beta+m.initial_delta_rad;
tip_lifted = weighted + cfg.capsule_length_m*[cos(angle), sin(angle)];
plot(100*[weighted(1), tip_eq(1)], 100*[weighted(2), tip_eq(2)], 'b-', 'LineWidth', 3);
plot(100*[weighted(1), tip_lifted(1)], 100*[weighted(2), tip_lifted(2)], 'r-', 'LineWidth', 3);
plot(100*weighted(1), 100*weighted(2), 'ko', 'MarkerFaceColor', 'k');
axis equal; grid on; xlabel('x [cm]'); ylabel('z [cm]');
title('Geometria inferida de 5 cm y 30 deg; no es una postura medida');
legend('Recipiente ideal', 'Agua', 'Reposo geometrico inferido', 'Elevado', 'Lastre');
subplot(2, 1, 2); hold on;
depths = [0.03, 0.05, 0.08, 0.12];
for j = 1:numel(depths)
    alternative = cfg;
    alternative.depth_m = depths(j);
    md = circular_wall_modes(alternative);
    plot(1:min(4, cfg.n_modes), md.frequency_hz(1:min(4, cfg.n_modes)), 'o-');
end
grid on; xlabel('Modo radial m=1'); ylabel('Frecuencia del agua [Hz]');
title('Sensibilidad a profundidad; fondo plano y pared vertical idealizados');
legend('3 cm', '5 cm', '8 cm', '12 cm', 'Location', 'northwest');
print(fig, fullfile(output_dir, 'geometry_and_modes.png'), '-dpng', '-r130');
clear clean_fig;

max_eta = max(abs(eta(:)));
% Cota conservadora de pendiente radial usando las derivadas de la base.
radial = linspace(0, R, 201);
derivatives = repmat(m.k_m_inv./besselj(1, m.roots), 1, numel(radial)).* ...
    (besselj(0, m.k_m_inv*radial)-besselj(2, m.k_m_inv*radial))/2;
max_radial_slope = max(max(abs(walls.wave_modes_m*derivatives)));
radial_surface = circular_wall_surface(walls, radial, zeros(size(radial)));
azimuthal_slope = radial_surface(:, 2:end)./repmat(radial(2:end), numel(t), 1);
max_surface_slope = max(max_radial_slope, max(abs(azimuthal_slope(:))));
report = sprintf(['SIMULACION EXPLORATORIA, NO AJUSTADA A LOS REGISTROS\n' ...
    'Diametro interior: %.3f m; profundidad: %.3f m; longitud capsula: %.3f m\n' ...
    'Referencia angular TFM (no postura geometrica calibrada): %.6f rad\n' ...
    'Perturbacion angular inicial aportada: %.2f deg; elevacion aproximada: %.1f cm\n' ...
    'Postura horizontal inferida con extremo lastrado fijo: %.2f deg; elevada: %.2f deg\n' ...
    'Primer modo del agua, sin capsula: %.4f Hz\n' ...
    'Velocidad de grupo a %.2f Hz: %.4f m/s\n' ...
    'Ida-vuelta desde el centro: %.3f s; desde borde proyectado de capsula: %.3f s\n' ...
    'Estos tiempos son escalas de propagacion, no retardos impuestos ni batidos.\n' ...
    'Maxima elevacion simulada: %.3f mm; eta/h: %.4f; pendiente superficial maxima: %.4f\n' ...
    'Error relativo maximo del balance energetico: %.3g\n' ...
    'Acoplamiento, inercia, rigidez y perdidas no estan medidos.\n'], ...
    cfg.diameter_m, cfg.depth_m, cfg.capsule_length_m, cfg.equilibrium_rad, ...
    m.initial_delta_rad*180/pi, cfg.end_lift_m*100, beta*180/pi, angle*180/pi, m.frequency_hz(1), ...
    cfg.capsule_frequency_hz, m.reference_group_ms, m.center_roundtrip_s, ...
    m.edge_roundtrip_s, max_eta*1000, max_eta/cfg.depth_m, max_surface_slope, ...
    max(abs(walls.balance_error_j))/initial_energy);
filename = fullfile(output_dir, 'summary.txt');
fid = fopen(filename, 'w');
if fid < 0
    error('circular_walls:OutputError', 'No se puede escribir %s', filename);
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, '%s', report);
fprintf('%s', report);
if max_eta/cfg.depth_m > 0.1 || max_surface_slope > 0.1
    warning('circular_walls:LinearWaveLimit', ...
        'La elevacion o pendiente supera el umbral orientativo 0.1: revisar la aproximacion lineal.');
end
end

function write_csv(filename, header, data)
fid = fopen(filename, 'w');
if fid < 0
    error('circular_walls:OutputError', 'No se puede escribir %s', filename);
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, '%s\n', header);
fprintf(fid, [repmat('%.12g,', 1, size(data, 2)-1), '%.12g\n'], data');
end
