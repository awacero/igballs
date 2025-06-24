import numpy as np
import plotly.graph_objects as go








def create_beach_ball(center, strike_vec, dip_vec, normal_vec,
                                             radius=2.5, resolution=300):


    # Malla esférica
    u = np.linspace(0, 2 * np.pi, resolution)
    v = np.linspace(0, np.pi, resolution)
    u, v = np.meshgrid(u, v)

    x = np.sin(v) * np.cos(u)
    y = np.sin(v) * np.sin(u)
    z = np.cos(v)
    xyz = np.stack([x, y, z], axis=-1).reshape(-1, 3)

    # Sistema local (X = strike, Y = dip, Z = normal)
    v1 = strike_vec / np.linalg.norm(strike_vec)
    v2 = dip_vec / np.linalg.norm(dip_vec)
    v3 = normal_vec / np.linalg.norm(normal_vec)

    local_basis = np.vstack([v1, v2, v3]).T  # 3x3

    # Rotar cada punto al sistema local del plano
    xyz_local = xyz @ local_basis  # N x 3

    # Ahora clasificamos los cuadrantes:
    # Signo de Y_local y Z_local define los cuadrantes
    y_l = xyz_local[:, 1]
    z_l = xyz_local[:, 2]

    # Colorear según cuadrante
    # (Compresión = azul, Dilatación = blanco)
    colors = np.where((y_l * z_l) > 0, 0, 1)  # Mismo signo → compresión

    # Redimensionar y trasladar
    x_final = x.reshape(v.shape) * radius + center[0]
    y_final = y.reshape(v.shape) * radius + center[1]
    z_final = z.reshape(v.shape) * radius + center[2]
    color_final = colors.reshape(v.shape)

    # Superficie
    return go.Surface(
        x=x_final, y=y_final, z=z_final,
        surfacecolor=color_final,
        colorscale=[[0, 'blue'], [1, 'white']],
        cmin=0, cmax=1,
        showscale=False,
        opacity=1.0,
        name='Beachball'
    )

