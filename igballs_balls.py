import numpy as np
import plotly.graph_objects as go

def create_beach_ball(center, strike_vec, dip_vec, normal_vec,
                      rake_deg, radius=2.5, resolution=300,
                      invert_colors=False):

    # -- 1. Unit vectors of the local basis -------------------------------
    v1 = strike_vec / np.linalg.norm(strike_vec)   # strike axis  (x)
    v2 = dip_vec    / np.linalg.norm(dip_vec)      # down‑dip     (y)
    v3 = normal_vec / np.linalg.norm(normal_vec)   # fault normal (z)

    # -- 2. Slip vector from rake -----------------------------------------
    rake = np.deg2rad(rake_deg)
    slip_vec = np.cos(rake)*v1 + np.sin(rake)*v2
    slip_vec /= np.linalg.norm(slip_vec)

    # -- 3. Moment tensor for a sheer double couple -----------------------
    #   M_ij = s_i n_j + s_j n_i   (Aki & Richards, eq. 4.89)
    M = np.outer(slip_vec, v3) + np.outer(v3, slip_vec)   # 3×3

    # -- 4. Points on a unit sphere ---------------------------------------
    u = np.linspace(0, 2*np.pi, resolution)
    v = np.linspace(0,     np.pi, resolution)
    u, v = np.meshgrid(u, v)
    x = np.sin(v)*np.cos(u)
    y = np.sin(v)*np.sin(u)
    z = np.cos(v)
    xyz = np.stack([x, y, z], axis=-1).reshape(-1, 3)

    # -- 5. Radial displacement sign --------------------------------------
    #     sign > 0  → compression,  sign < 0 → dilatation
    ur = np.einsum('...i,ij,...j->...', xyz, M, xyz)
    colors = (ur < 0).astype(int)                   # 0 = blue (C), 1 = white (T)
    if invert_colors:
        colors = 1 - colors

    # -- 6. Scale and translate to the desired centre ---------------------
    x_final = x*radius + center[0]
    y_final = y*radius + center[1]
    z_final = z*radius + center[2]
    color_final = colors.reshape(u.shape)

    return go.Surface(
        x=x_final, y=y_final, z=z_final,
        surfacecolor=color_final,
        colorscale=[[0, 'blue'], [1, 'white']],
        cmin=0, cmax=1,
        showscale=False,
        name='Beachball'
    )

'''

fig = go.Figure()

# Right‑lateral, vertical fault (strike 0°, dip 90°, rake 180°)
strike = np.array([1, 0, 0])
dip    = np.array([0, 0, -1])
normal = np.cross(strike, dip)          # [0, 1, 0]

fig.add_trace(create_beach_ball(center=[0,0,0],
                                strike_vec=strike,
                                dip_vec=dip,
                                normal_vec=normal,
                                rake_deg=180,
                                radius=2.5))

fig.update_layout(scene_aspectmode='data'); fig.show()

'''