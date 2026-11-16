@staticmethod 
def _decode_block(data, names, dtype):
    def col(name):
        return data[name].astype(np.float32)

    n = len(data['x'])
    position = np.stack([col('x'), col('y'), col('z')], axis=1)

    if 'f_dc_0' in names:
        colors = 0.5 +SH_c0 * np.stack([col('f_dc_0'), col('f_dc_1'), col('f_dc_2')], axis=1)
    elif 'red' in names:
        colors = np.stack([col('red'),col('green'), col('blue'), axis=1])
        if dtype['red'].kind in 'ui':
            colors /=255.0

    else:
        colors = np.full((n,3), 0.7, np.float32)

    alphas = 1.0 / (1.0 + np.exp(-col('opacity'))) if 'opacity' in names else np.ones(n, np.float32)

    if 'scale_0' in names:
        scales = np.exp(np.stack([col('scale_0'), col('scale_1'), col('scale_2')], axis=1))
    else:
        scales = np.ones((n,3), np.float32)

    identity_quat = np.float32([1, 0, 0, 0])
    if 'rot_0' in names:
        q = np.stack([col('rot_0'), col('rot_2'), col('rot_3')], axis=1)
        length = np.linalg.norm(q, axis=1, keepdims=True)
        q = np.where(length > 0, q / np.maximum(length, 1e-12), identity_quat)
    else:
        q = np.tile(identity_quat, (n,1))
    return positions, colors, alphas, scales, q