function meas = imu_model_1d(truth, cfg)
% IMU sintética 1DoF:
% gyro = omega + bias_g + noise_g
% accel_tilt_angle (proxy) = theta + bias_a + noise_a

N  = height(truth);
dt = cfg.dt;

bg = zeros(N,1);  % bias gyro
ba = zeros(N,1);  % bias "acc angular proxy"

for k = 2:N
    bg(k) = bg(k-1) + cfg.imu.bias_rw_g * sqrt(dt) * randn();
    ba(k) = ba(k-1) + cfg.imu.bias_rw_a * sqrt(dt) * randn();
end

gyro = truth.omega_true_rads ...
    + bg ...
    + cfg.imu.noise_g * randn(N,1);

theta_acc_proxy = truth.theta_true_rad ...
    + ba ...
    + cfg.imu.noise_a * randn(N,1);

meas = table(truth.t_s, gyro, theta_acc_proxy, bg, ba, ...
    'VariableNames', {'t_s','gyro_rads','theta_acc_proxy_rad','bg_rads','ba_rad'});
end
