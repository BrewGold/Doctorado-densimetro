function cfg = internal_mass_config()
% Parametros ilustrativos; no identificados experimentalmente.
cfg.beta_eq_rad = 34.91*pi/180;
cfg.shell_mass_kg = 0.045;
cfg.moving_mass_kg = 0.005;
cfg.shell_inertia_kgm2 = 1.2e-4;
cfg.mass_position_body_m = [-0.060; 0];
cfg.stroke_m = 0.004;
cfg.stroke_duration_s = 0.25;
cfg.oscillation_hz = 1.9;
cfg.angular_decay_s = 0.15;
cfg.translation_stiffness_n_m = [0; 8];
cfg.translation_damping_ns_m = [0.08; 0.08];
cfg.gravity_ms2 = 9.81;
cfg.duration_s = 8;
cfg.sample_rate_hz = 200;
end
