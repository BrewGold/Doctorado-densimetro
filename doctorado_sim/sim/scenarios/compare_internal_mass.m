function comparison = compare_internal_mass(cfg, durations_s, window_s)
% Maximo absoluto de giro durante la ventana posterior al retorno de la masa.
if isempty(durations_s) || any(~isfinite(durations_s(:))) || ...
        any(durations_s(:) <= 0) || ~isscalar(window_s) || ...
        ~isfinite(window_s) || window_s <= 0
    error('internal_mass:InvalidComparison', 'Duraciones y ventana deben ser positivas.');
end
comparison = zeros(numel(durations_s), 3);
for k = 1:numel(durations_s)
    trial = cfg;
    trial.stroke_duration_s = durations_s(k);
    trial.duration_s = durations_s(k) + window_s;
    axial = dynamics_internal_mass(trial, [1; 0]);
    vertical = dynamics_internal_mass(trial, ...
        [sin(trial.beta_eq_rad); cos(trial.beta_eq_rad)]);
    indices = axial.t_s >= trial.stroke_duration_s & ...
        axial.t_s <= trial.stroke_duration_s + window_s;
    if ~any(indices)
        error('internal_mass:InvalidComparison', 'La ventana no contiene muestras.');
    end
    comparison(k,:) = [durations_s(k), ...
        max(abs(axial.angle_rad(indices)))*180/pi, ...
        max(abs(vertical.angle_rad(indices)))*180/pi];
end
end
