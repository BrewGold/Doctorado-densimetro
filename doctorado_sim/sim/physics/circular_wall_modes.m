function modes = circular_wall_modes(cfg)
positive = {'diameter_m', 'depth_m', 'capsule_length_m', 'rho_kgm3', ...
    'g_ms2', 'I_kgm2', 'capsule_frequency_hz', 'duration_s', 'fs_hz'};
nonnegative = {'end_lift_m', 'mu_pas', 'sigma_npm', ...
    'capsule_decay_s_inv', 'wave_extra_decay_s_inv', 'coupling_fraction'};
names = [positive, nonnegative, {'equilibrium_rad', 'initial_delta_rad', 'n_modes'}];
for i = 1:numel(names)
    name = names{i};
    if ~isfield(cfg, name) || ~isnumeric(cfg.(name)) || ~isreal(cfg.(name)) || ...
            ~isscalar(cfg.(name)) || ~isfinite(cfg.(name))
        error('circular_walls:InvalidConfig', 'Parametro finito escalar requerido: %s', name);
    end
end
for i = 1:numel(positive)
    if cfg.(positive{i}) <= 0
        error('circular_walls:InvalidConfig', '%s debe ser positivo.', positive{i});
    end
end
for i = 1:numel(nonnegative)
    if cfg.(nonnegative{i}) < 0
        error('circular_walls:InvalidConfig', '%s no puede ser negativo.', nonnegative{i});
    end
end
if cfg.n_modes < 1 || cfg.n_modes ~= fix(cfg.n_modes) || cfg.n_modes > 32
    error('circular_walls:InvalidConfig', 'n_modes debe ser un entero entre 1 y 32.');
end
if cfg.capsule_length_m >= cfg.diameter_m || cfg.initial_delta_rad <= 0 || ...
        cfg.initial_delta_rad >= pi/2 || cfg.duration_s*cfg.fs_hz < 1
    error('circular_walls:InvalidConfig', 'Geometria, inclinacion o muestreo incompatibles.');
end
lift_ratio = cfg.end_lift_m/(2*cfg.capsule_length_m*sin(cfg.initial_delta_rad/2));
if lift_ratio <= 0 || lift_ratio >= 1
    error('circular_walls:InvalidConfig', ...
        'Elevacion y perturbacion incompatibles con la hipotesis de extremo lastrado fijo.');
end
% Postura geometrica inferida del levantamiento, no calibracion del angulo IMU.
beta = acos(lift_ratio)-cfg.initial_delta_rad/2;
if beta < 0 || beta+cfg.initial_delta_rad >= pi/2
    error('circular_walls:InvalidConfig', ...
        'El levantamiento debe permanecer en la rama geometrica entre 0 y 90 grados.');
end
R = cfg.diameter_m/2;
derivative = @(z) (besselj(0, z)-besselj(2, z))/2;
roots = zeros(cfg.n_modes, 1);
for n = 1:cfg.n_modes
    roots(n) = fzero(derivative, [(n-0.5)*pi, n*pi]);
end
k = roots/R;
area_norm = pi*R^2/2*(1-1./roots.^2);
mass = cfg.rho_kgm3*area_norm./(k.*tanh(k*cfg.depth_m));
stiffness = (cfg.rho_kgm3*cfg.g_ms2 + cfg.sigma_npm*k.^2).*area_norm;
frequency = sqrt(stiffness./mass)/(2*pi);
if cfg.fs_hz < 10*max(frequency)
    error('circular_walls:InvalidConfig', ...
        'fs_hz debe cubrir al menos 10 muestras por periodo del modo mas rapido.');
end
width = cfg.capsule_length_m*cos(beta)/4;
% Fuente dipolar suavizada; fuerza de acoplamiento aun no identificada.
overlap = k./(2*besselj(1, roots)).*exp(-0.5*(k*width).^2);
capsule_k = cfg.I_kgm2*(2*pi*cfg.capsule_frequency_hz)^2;
gain = sqrt(cfg.coupling_fraction*capsule_k/sum(overlap.^2./stiffness));
a = gain*overlap./stiffness;
decay = cfg.wave_extra_decay_s_inv + 2*(cfg.mu_pas/cfg.rho_kgm3)*k.^2;
modes.roots = roots;
modes.k_m_inv = k;
modes.mass_kg = mass;
modes.stiffness_n_m = stiffness;
modes.frequency_hz = frequency;
modes.decay_s_inv = decay;
modes.damping_kg_s = 2*mass.*decay;
modes.coupling_m = a;
modes.capsule_k_nm = capsule_k;
modes.initial_delta_rad = cfg.initial_delta_rad;
modes.geometric_equilibrium_rad = beta;

dispersion = @(z) (cfg.g_ms2*z + cfg.sigma_npm/cfg.rho_kgm3*z.^3).* ...
    tanh(z*cfg.depth_m);
omega = 2*pi*cfg.capsule_frequency_hz;
upper = max(k(1), omega^2/cfg.g_ms2);
while dispersion(upper) < omega^2
    upper = 2*upper;
end
reference_k = fzero(@(z) dispersion(z)-omega^2, [0, upper]);
kh = reference_k*cfg.depth_m;
cg = ((cfg.g_ms2+3*cfg.sigma_npm/cfg.rho_kgm3*reference_k^2)*tanh(kh) + ...
    (cfg.g_ms2*reference_k+cfg.sigma_npm/cfg.rho_kgm3*reference_k^3)* ...
    cfg.depth_m*(1-tanh(kh)^2))/(2*omega);
modes.reference_k_m_inv = reference_k;
modes.reference_group_ms = cg;
modes.center_roundtrip_s = 2*R/cg;
modes.edge_roundtrip_s = 2*(R-cfg.capsule_length_m*cos(beta)/2)/cg;
end
