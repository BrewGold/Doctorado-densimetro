function cfg = circular_wall_config()
% Geometria aportada; densidad del TFM y mu/sigma orientativas de agua a 20 C.
cfg.diameter_m = 0.22;
cfg.depth_m = 0.08;
cfg.capsule_length_m = 0.15;
cfg.equilibrium_rad = -0.959728; % Referencia del TFM para rho = 0.9973 g/cm3.
cfg.initial_delta_rad = 30*pi/180; % Desviacion aportada, no angulo de equilibrio.
cfg.end_lift_m = 0.05;
cfg.rho_kgm3 = 997.3;
cfg.mu_pas = 1.002e-3;
cfg.sigma_npm = 0.0728;
cfg.g_ms2 = 9.81;
cfg.n_modes = 8;
cfg.duration_s = 80;
cfg.fs_hz = 100;
% Valores exploratorios, no medidos en esta capsula.
cfg.I_kgm2 = 1.2e-4;
cfg.capsule_frequency_hz = 1.9;
cfg.capsule_decay_s_inv = 0.035;
cfg.wave_extra_decay_s_inv = 0.04;
cfg.coupling_fraction = 0.01;
end
