function test_internal_mass()
sim_root = fileparts(fileparts(mfilename('fullpath')));
addpath(fullfile(sim_root, 'sim', 'core'));
addpath(fullfile(sim_root, 'sim', 'scenarios'));
cfg = internal_mass_config();
axial = dynamics_internal_mass(cfg, [1; 0]);
vertical = dynamics_internal_mass(cfg, [sin(cfg.beta_eq_rad); cos(cfg.beta_eq_rad)]);
assert(all(isfinite(axial.angle_rad)));
assert(all(isfinite(vertical.angle_rad)));
assert(max(abs(vertical.angle_rad-axial.angle_rad)) > 1e-4);
assert(max(abs(axial.mass_displacement_m-vertical.mass_displacement_m)) < 1e-12);
assert(max(abs(axial.mass_displacement_m(axial.t_s >= cfg.stroke_duration_s))) == 0);
comparison = compare_internal_mass(cfg, cfg.stroke_duration_s, 2);
window = axial.t_s >= cfg.stroke_duration_s & ...
    axial.t_s <= cfg.stroke_duration_s + 2;
assert(abs(comparison(1,2)-max(abs(axial.angle_rad(window)))*180/pi) < 1e-5);
assert(abs(comparison(1,3)-max(abs(vertical.angle_rad(window)))*180/pi) < 1e-5);
energy = internal_mass_kinetic_energy(cfg, axial);
assert(all(energy.total_j >= 0));
assert(all(energy.relative_j >= 0));
assert(max(abs(energy.total_j-energy.com_translation_j-energy.relative_j)) < 1e-14);
post_energy = axial.t_s >= cfg.stroke_duration_s;
reduced_mass = cfg.shell_mass_kg*cfg.moving_mass_kg/(cfg.shell_mass_kg+cfg.moving_mass_kg);
inertia_com = cfg.shell_inertia_kgm2 + reduced_mass*sum(cfg.mass_position_body_m.^2);
assert(max(abs(energy.relative_j(post_energy) - ...
    0.5*inertia_com*axial.omega_rads(post_energy).^2)) < 1e-14);

rest_cfg = cfg;
rest_cfg.stroke_m = 0;
rest = dynamics_internal_mass(rest_cfg, [1; 0]);
assert(max(abs(rest.angle_rad)) < 1e-12);
assert(max(abs(rest.position_m(:))) < 1e-12);
rest_energy = internal_mass_kinetic_energy(rest_cfg, rest);
assert(max(abs(rest_energy.total_j)) < 1e-20);

free_cfg = cfg;
free_cfg.gravity_ms2 = 0;
free_cfg.oscillation_hz = 0;
free_cfg.angular_decay_s = 0;
free_cfg.translation_stiffness_n_m = [0; 0];
free_cfg.translation_damping_ns_m = [0; 0];
free = dynamics_internal_mass(free_cfg, [0; 1]);
m = free_cfg.moving_mass_kg;
M = free_cfg.shell_mass_kg;
momentum = zeros(numel(free.t_s), 2);
angular_momentum = zeros(size(free.t_s));
for i = 1:numel(free.t_s)
    a = free_cfg.beta_eq_rad + free.angle_rad(i);
    R = [cos(a), -sin(a); sin(a), cos(a)];
    r = R*(free_cfg.mass_position_body_m + [0; free.mass_displacement_m(i)]);
    mass_velocity = free.velocity_ms(i,:)' + free.omega_rads(i)*[-r(2); r(1)] ...
        + R*[0; free.mass_velocity_ms(i)];
    shell_p = M*free.velocity_ms(i,:)';
    mass_p = m*mass_velocity;
    momentum(i,:) = (shell_p + mass_p)';
    pos = free.position_m(i,:)';
    angular_momentum(i) = free_cfg.shell_inertia_kgm2*free.omega_rads(i) ...
        + pos(1)*shell_p(2)-pos(2)*shell_p(1) ...
        + (pos(1)+r(1))*mass_p(2)-(pos(2)+r(2))*mass_p(1);
end
assert(max(abs(momentum(:))) < 1e-8);
assert(max(abs(angular_momentum)) < 1e-9);

centered = free_cfg;
centered.mass_position_body_m = [0; 0];
central = dynamics_internal_mass(centered, [1; 0]);
assert(max(abs(central.angle_rad)) < 1e-10);
assert(max(abs(central.position_m(:,1))) > 1e-6);

caught = false;
try
    dynamics_internal_mass(cfg, [2; 0]);
catch err
    caught = strcmp(err.identifier, 'internal_mass:InvalidDirection');
end
assert(caught);
disp('OK: respuesta, reposo, conservacion y reaccion sin torque.');
end
