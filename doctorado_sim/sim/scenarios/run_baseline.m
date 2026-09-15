clear; clc; close all;

% ---------- Config ----------
cfg.fs = 100;
cfg.dt = 1/cfg.fs;
T = 60;
cfg.N = round(T*cfg.fs);

cfg.theta_init_rad = deg2rad(20);
cfg.omega_init_rads = 0;
cfg.alpha_cf = 0.98;

% Parámetros físicos (MVP)
p = struct();
p.I_kgm2      = 1.2e-4;
p.theta0_rad  = deg2rad(-55);   % equilibrio
p.k_lin       = 2.5e-3;
p.k_sin       = 2.0e-3;
p.w_lin       = 0.7;

p.mu_pas      = 0.010;          % viscosidad efectiva
p.sigma_npm   = 0.050;          % reservado para siguiente iteración
p.c0          = 6e-4;
p.c_mu_gain   = 2e-2;
p.c_quad      = 1.2e-4;

p.tau_noise_std = 2e-6;
cfg.p = p;

% IMU
imu = struct();
imu.noise_g   = deg2rad(0.15);   % rad/s std
imu.noise_a   = deg2rad(0.40);   % rad std (proxy inclinación)
imu.bias_rw_g = deg2rad(0.01);   % rad/s/sqrt(s)
imu.bias_rw_a = deg2rad(0.02);   % rad/sqrt(s)
cfg.imu = imu;

% ---------- Sim ----------
truth = dynamics_1d(cfg);
meas  = imu_model_1d(truth, cfg);
S     = compare_truth_vs_estimate(truth, meas, cfg);

% ---------- Guardado ----------
outdir_data = 'doctorado_sim/data/synthetic';
outdir_fig  = 'doctorado_sim/results/figures';
outdir_tab  = 'doctorado_sim/results/tables';
if ~exist(outdir_data,'dir'), mkdir(outdir_data); end
if ~exist(outdir_fig,'dir'), mkdir(outdir_fig); end
if ~exist(outdir_tab,'dir'), mkdir(outdir_tab); end

stamp = string(datetime('now','Format','yyyyMMdd_HHmmss'));

Ttruth = truth;
Tmeas = meas;
Tmeas.theta_est_rad = S.theta_est;
writetable(Ttruth, fullfile(outdir_data, "truth_" + stamp + ".csv"));
writetable(Tmeas,  fullfile(outdir_data, "meas_"  + stamp + ".csv"));

% ---------- Figuras ----------
f1 = figure('Name','Truth vs Estimate'); hold on; grid on;
plot(truth.t_s, truth.theta_true_rad, 'k', 'LineWidth',1.6);
plot(meas.t_s, S.theta_est, 'b');
plot(meas.t_s, S.theta_fit, 'r--','LineWidth',1.2);
legend('theta true','theta est','fit 1er orden','Location','best');
xlabel('t [s]'); ylabel('\theta [rad]');
title('Baseline 1DoF + IMU');
saveas(f1, fullfile(outdir_fig, "baseline_theta_" + stamp + ".png"));

% ---------- Tabla resumen ----------
Summary = table(S.mae_theta, S.rmse_theta, S.thetaeq_est_rad, S.tau_est_s, S.fit_rmse_rad, ...
    'VariableNames', {'mae_theta','rmse_theta','thetaeq_est_rad','tau_est_s','fit_rmse_rad'});
writetable(Summary, fullfile(outdir_tab, "baseline_summary_" + stamp + ".csv"));

disp(Summary);
disp("OK baseline ejecutado.");
