function eta = circular_wall_surface(out, radius_m, azimuth_rad)
% Una fila por instante y una columna por punto (r, phi).
if ~isnumeric(radius_m) || ~isnumeric(azimuth_rad) || ...
        ~isreal(radius_m) || ~isreal(azimuth_rad) || ...
        numel(radius_m) ~= numel(azimuth_rad) || isempty(radius_m) || ...
        any(~isfinite(radius_m(:))) || any(~isfinite(azimuth_rad(:)))
    error('circular_walls:InvalidPoints', 'Se requieren pares finitos de radio y azimut.');
end
R = out.modes.roots(1)/out.modes.k_m_inv(1);
if any(radius_m(:) < 0 | radius_m(:) > R*(1+1e-12))
    error('circular_walls:InvalidPoints', 'Los puntos deben estar dentro del recipiente.');
end
shape = besselj(1, out.modes.k_m_inv*radius_m(:)')./ ...
    repmat(besselj(1, out.modes.roots), 1, numel(radius_m));
shape = shape.*repmat(cos(azimuth_rad(:)'), numel(out.modes.roots), 1);
eta = out.wave_modes_m*shape;
end
