function energy = internal_mass_kinetic_energy(cfg, out)
% Energia en el marco del laboratorio, referida a la carcasa y masa puntual.
n = numel(out.t_s);
energy.total_j = zeros(n, 1);
energy.com_translation_j = zeros(n, 1);
energy.relative_j = zeros(n, 1);
energy.shell_rotation_j = zeros(n, 1);
M = cfg.shell_mass_kg;
m = cfg.moving_mass_kg;
for i = 1:n
    a = cfg.beta_eq_rad + out.angle_rad(i);
    R = [cos(a), -sin(a); sin(a), cos(a)];
    r = R*(cfg.mass_position_body_m(:) + out.mass_displacement_m(i)*out.direction_body);
    relative_velocity = out.omega_rads(i)*[-r(2); r(1)] ...
        + out.mass_velocity_ms(i)*R*out.direction_body;
    shell_velocity = out.velocity_ms(i,:)';
    mass_velocity = shell_velocity + relative_velocity;
    com_velocity = (M*shell_velocity + m*mass_velocity)/(M+m);
    energy.shell_rotation_j(i) = 0.5*cfg.shell_inertia_kgm2*out.omega_rads(i)^2;
    energy.total_j(i) = 0.5*M*(shell_velocity'*shell_velocity) ...
        + energy.shell_rotation_j(i) + 0.5*m*(mass_velocity'*mass_velocity);
    energy.com_translation_j(i) = 0.5*(M+m)*(com_velocity'*com_velocity);
    energy.relative_j(i) = energy.shell_rotation_j(i) ...
        + 0.5*(M*m/(M+m))*(relative_velocity'*relative_velocity);
end
end
