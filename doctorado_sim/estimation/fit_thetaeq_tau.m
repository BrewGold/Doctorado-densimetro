function fit = fit_thetaeq_tau(t_s, theta_rad)
% Ajuste: theta(t)=theta_eq*(1-exp(-t/tau))
model = @(p,t) p(1) * (1 - exp(-t./max(p(2),1e-6)));

N = numel(theta_rad);
n_final = max(10, round(0.2*N));
p0 = [mean(theta_rad(end-n_final+1:end)), max(0.2, (t_s(end)-t_s(1))/5)];

cost = @(p) sum((theta_rad - model(p,t_s)).^2);
p = fminsearch(cost, p0);

theta_hat = model(p,t_s);
rmse = sqrt(mean((theta_rad - theta_hat).^2));

fit.theta_eq_rad = p(1);
fit.tau_s = p(2);
fit.rmse_rad = rmse;
fit.theta_fit_rad = theta_hat;
end
