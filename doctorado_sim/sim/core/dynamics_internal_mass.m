function out = dynamics_internal_mass(cfg, direction_body)
% Movimiento plano de carcasa y masa interna con trayectoria prescrita.
if numel(direction_body) ~= 2 || any(~isfinite(direction_body(:))) || ...
        abs(norm(direction_body)-1) > 1e-10
    error('internal_mass:InvalidDirection', 'La direccion debe ser un vector unitario 2D.');
end
if cfg.shell_mass_kg <= 0 || cfg.moving_mass_kg <= 0 || ...
        cfg.shell_inertia_kgm2 <= 0 || cfg.stroke_duration_s <= 0 || ...
        cfg.duration_s <= 0 || cfg.sample_rate_hz <= 0 || ...
        cfg.oscillation_hz < 0 || cfg.angular_decay_s < 0 || ...
        any(cfg.translation_stiffness_n_m < 0) || ...
        any(cfg.translation_damping_ns_m < 0)
    error('internal_mass:InvalidConfig', 'Los parametros fisicos no son validos.');
end
direction_body = direction_body(:);
t = (0:round(cfg.duration_s*cfg.sample_rate_hz))'/cfg.sample_rate_hz;
opts = odeset('RelTol', 1e-9, 'AbsTol', 1e-11, ...
    'MaxStep', min(0.005, cfg.stroke_duration_s/50));
[~, y] = ode45(@rhs, t, zeros(6,1), opts);
q = zeros(size(t));
qd = q;
qdd = q;
for i = 1:numel(t)
    [q(i), qd(i), qdd(i)] = trajectory(t(i));
end
out.t_s = t;
out.position_m = y(:, 1:2);
out.angle_rad = y(:, 3);
out.velocity_ms = y(:, 4:5);
out.omega_rads = y(:, 6);
out.mass_displacement_m = q;
out.mass_velocity_ms = qd;
out.mass_acceleration_ms2 = qdd;
out.direction_body = direction_body;

    function [s, sd, sdd] = trajectory(time)
        if time >= 0 && time < cfg.stroke_duration_s
            w = 2*pi/cfg.stroke_duration_s;
            s = cfg.stroke_m*(1-cos(w*time))/2;
            sd = cfg.stroke_m*w*sin(w*time)/2;
            sdd = cfg.stroke_m*w^2*cos(w*time)/2;
        else
            s = 0;
            sd = 0;
            sdd = 0;
        end
    end

    function dy = rhs(time, state)
        [s, sd, sdd] = trajectory(time);
        angle = cfg.beta_eq_rad + state(3);
        R = [cos(angle), -sin(angle); sin(angle), cos(angle)];
        J = [0, -1; 1, 0];
        r = R*(cfg.mass_position_body_m(:) + s*direction_body);
        direction_world = R*direction_body;
        omega = state(6);
        a_relative = -omega^2*r + 2*omega*sd*J*direction_world + ...
            sdd*direction_world;
        m = cfg.moving_mass_kg;
        total_mass = cfg.shell_mass_kg + m;
        mass_matrix = [total_mass, 0, -m*r(2); ...
                       0, total_mass, m*r(1); ...
                       -m*r(2), m*r(1), cfg.shell_inertia_kgm2 + m*(r'*r)];
        r_eq = [cos(cfg.beta_eq_rad), -sin(cfg.beta_eq_rad); ...
                sin(cfg.beta_eq_rad), cos(cfg.beta_eq_rad)]*cfg.mass_position_body_m(:);
        initial_inertia = cfg.shell_inertia_kgm2 + m*(r_eq'*r_eq);
        stiffness = initial_inertia*(2*pi*cfg.oscillation_hz)^2;
        damping = 2*initial_inertia*cfg.angular_decay_s;
        external_force = -cfg.translation_stiffness_n_m(:).*state(1:2) ...
            - cfg.translation_damping_ns_m(:).*state(4:5);
        gravity_torque = -m*cfg.gravity_ms2*(r(1)-r_eq(1));
        torque = gravity_torque - stiffness*state(3) - damping*omega;
        moment_relative = r(1)*a_relative(2)-r(2)*a_relative(1);
        acceleration = mass_matrix\[external_force - m*a_relative; ...
            torque - m*moment_relative];
        dy = [state(4:6); acceleration];
    end
end
