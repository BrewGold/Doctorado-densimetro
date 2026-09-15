function summary = compare_truth_vs_estimate(truth, meas, cfg)
% Filtro complementario igual filosofía TFM
N = height(meas);
theta_est = zeros(N,1);

for k = 2:N
    theta_gyro = theta_est(k-1) + meas.gyro_rads(k)*cfg.dt;
    theta_est(k) = cfg.alpha_cf*theta_gyro + (1-cfg.alpha_cf)*meas.theta_acc_proxy_rad(k);
end

fit = fit_thetaeq_tau(meas.t_s, theta_est);

err = theta_est - truth.theta_true_rad;
summary = struct();
summary.mae_theta = mean(abs(err));
summary.rmse_theta = sqrt(mean(err.^2));
summary.thetaeq_est_rad = fit.theta_eq_rad;
summary.tau_est_s = fit.tau_s;
summary.fit_rmse_rad = fit.rmse_rad;
summary.theta_est = theta_est;
summary.theta_fit = fit.theta_fit_rad;
end
