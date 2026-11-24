function run_internal_mass(output_dir)
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
% Direccion vertical en reposo, fija en la estructura durante el movimiento.
vertical = dynamics_internal_mass(cfg, [sin(cfg.beta_eq_rad); cos(cfg.beta_eq_rad)]);
t = axial.t_s;
data = [t, axial.mass_displacement_m, axial.angle_rad, axial.omega_rads, ...
    axial.position_m, vertical.angle_rad, vertical.omega_rads, vertical.position_m];
path = fullfile(output_dir, 'internal_mass.csv');
fid = fopen(path, 'w');
if fid < 0
    error('internal_mass:OutputError', 'No se puede escribir %s', path);
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, ['t_s,mass_displacement_m,axial_angle_rad,axial_omega_rads,' ...
    'axial_x_m,axial_z_m,vertical_angle_rad,vertical_omega_rads,' ...
    'vertical_x_m,vertical_z_m\n']);
fprintf(fid, [repmat('%.12g,', 1, size(data, 2)-1), '%.12g\n'], data');
clear cleanup;

fig = figure('Visible', 'off', 'Position', [100, 100, 1100, 900]);
cleanup_fig = onCleanup(@() close(fig));
set(fig, 'PaperUnits', 'inches', 'PaperPosition', [0, 0, 11, 9], ...
    'PaperSize', [11, 9]);
subplot(3, 1, 1);
plot(t, axial.mass_displacement_m*1000, 'k', 'LineWidth', 1.2);
grid on; ylabel('Recorrido [mm]');
title('Masa interna: salida y retorno, misma trayectoria');
subplot(3, 1, 2);
plot(t, axial.angle_rad*180/pi, 'b', t, vertical.angle_rad*180/pi, 'r', 'LineWidth', 1.1);
grid on; ylabel('Delta theta [grados]');
legend('Longitudinal', 'Vertical en reposo', 'Location', 'northeast');
title('Respuesta angular respecto al equilibrio supuesto');
subplot(3, 1, 3);
plot(t, axial.position_m(:,1)*1000, 'b', t, axial.position_m(:,2)*1000, 'b--', ...
    t, vertical.position_m(:,1)*1000, 'r', t, vertical.position_m(:,2)*1000, 'r--');
grid on; xlabel('Tiempo [s]'); ylabel('Desplazamiento [mm]');
legend('Axial x', 'Axial z', 'Vertical x', 'Vertical z', 'Location', 'northeast');
title('Traslacion de la carcasa: modelo efectivo del fluido');
print(fig, fullfile(output_dir, 'internal_mass.png'), '-dpng', '-r130');
print(fig, fullfile(output_dir, 'internal_mass.pdf'), '-dpdf');
geometry = figure('Visible', 'off', 'Position', [100, 100, 900, 600]);
cleanup_geometry = onCleanup(@() close(geometry));
beta = cfg.beta_eq_rad;
R = [cos(beta), -sin(beta); sin(beta), cos(beta)];
angle = linspace(0, 2*pi, 200);
shape = R*[0.075*cos(angle); 0.020*sin(angle)];
plot(shape(1,:)*1000, shape(2,:)*1000, 'k', 'LineWidth', 2);
hold on;
tip = R*cfg.mass_position_body_m;
plot(tip(1)*1000, tip(2)*1000, 'ko', 'MarkerFaceColor', 'k');
longitudinal = R*[1; 0];
quiver(tip(1)*1000, tip(2)*1000, 25*longitudinal(1), 25*longitudinal(2), ...
    0, 'b', 'LineWidth', 2);
quiver(tip(1)*1000, tip(2)*1000, 0, 25, 0, 'r', 'LineWidth', 2);
quiver(60, 45, 0, -20, 0, 'k', 'LineWidth', 1.5);
text(60, 47, 'gravedad');
text(tip(1)*1000-35, tip(2)*1000-12, 'masa movil cerca de la punta');
axis equal; grid on; xlabel('Horizontal [mm]'); ylabel('Vertical [mm]');
title('Geometria esquematica: 34.91 grados sobre horizontal (hipotesis)');
legend('Capsula esquematica', 'Masa movil en reposo', ...
    'Recorrido longitudinal', 'Recorrido vertical en reposo', 'Location', 'southoutside');
print(geometry, fullfile(output_dir, 'geometry.png'), '-dpng', '-r130');
fprintf('Maximo angular axial: %.4f grados\n', max(abs(axial.angle_rad))*180/pi);
fprintf('Maximo angular vertical: %.4f grados\n', max(abs(vertical.angle_rad))*180/pi);
fprintf('Resultados ilustrativos no ajustados: %s\n', output_dir);
end
