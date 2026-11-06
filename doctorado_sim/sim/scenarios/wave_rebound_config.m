function cfg = wave_rebound_config()
% Parametros ilustrativos: no son estimaciones de los ensayos.
cfg.duration_s = 80;
cfg.fs_hz = 100;
cfg.theta_eq_rad = 65*pi/180;
cfg.theta_init_rad = cfg.theta_eq_rad + 2*pi/180;
cfg.omega_init_rads = 0;
cfg.wave_init_rad = 0;
cfg.wave_rate_init_rads = 0;
cfg.I_capsule_kgm2 = 1.2e-4;
cfg.I_wave_kgm2 = cfg.I_capsule_kgm2;
cfg.k_capsule_nm_rad = cfg.I_capsule_kgm2*(2*pi*1.9)^2;
cfg.k_wave_nm_rad = cfg.I_wave_kgm2*(2*pi*1.9)^2;
cfg.k_coupling_nm_rad = 0.025*cfg.k_capsule_nm_rad;
cfg.c_capsule_nms_rad = 2*cfg.I_capsule_kgm2*0.035;
cfg.c_wave_nms_rad = 2*cfg.I_wave_kgm2*0.020;
end
