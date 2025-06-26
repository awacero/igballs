import numpy as np
import plotly.graph_objects as go

import igballs_balls 

def create_figure(
    strike_angle_deg: float,
    dip_angle_deg: float,
    rake_angle_deg: float,
    width: float,
    height: float,
    steps: int,
    eye_dict = dict

) -> go.Figure:
    """Create the 3D figure showing the fault model."""
    
    strike_rad = np.radians(strike_angle_deg)
    dip_rad = np.radians(dip_angle_deg)
    rake_rad = np.radians(rake_angle_deg)

    strike_vec = np.array([np.sin(strike_rad), np.cos(strike_rad), 0])
    dip_vec = np.array([
        np.cos(strike_rad) * np.cos(dip_rad),
        -np.sin(strike_rad) * np.cos(dip_rad),
        -np.sin(dip_rad),
    ])
    strike_vector = width * strike_vec
    dip_vector = height * dip_vec

    normal_vec = np.cross(strike_vec, dip_vec)
    normal_vec /= np.linalg.norm(normal_vec)

    origin = np.array([0, 0, 0])
    p1 = origin
    p2 = p1 + strike_vector
    p3 = p2 + dip_vector
    p4 = p1 + dip_vector

    p5 = np.array([p1[0] + width, p1[1], p1[2]])
    p6 = np.array([p2[0] + width, p2[1], p2[2]])
    p7 = np.array([p6[0], p6[1], p3[2]])
    p8 = np.array([p5[0], p5[1], p4[2]])

    vertices = np.array([p1, p2, p3, p4, p5, p6, p7, p8])
    x, y, z = vertices.T

    faces = [
        [0, 1, 2], [0, 2, 3],
        [4, 5, 6], [4, 6, 7],
        [0, 1, 5], [0, 5, 4],
        [1, 2, 6], [1, 6, 5],
        [2, 3, 7], [2, 7, 6],
        [3, 0, 4], [3, 4, 7],
    ]
    i, j, k = zip(*faces)

    center = (p1 + p3) / 2
    beachball_plot = igballs_balls.create_beach_ball(
        center, strike_vec, dip_vec, normal_vec
    )

    wedge = go.Mesh3d(
        x=x, y=y, z=z, i=i, j=j, k=k, color="sienna", opacity=0.6,
        name="Placa inferior",
    )

    plane = go.Mesh3d(
        x=[p1[0], p2[0], p3[0], p4[0]],
        y=[p1[1], p2[1], p3[1], p4[1]],
        z=[p1[2], p2[2], p3[2], p4[2]],
        i=[0, 0],
        j=[1, 3],
        k=[2, 2],
        color="gray",
        opacity=0.7,
        name="Plano de falla",
    )

    ns_line = go.Scatter3d(
        x=[0, 0], y=[-3, 2], z=[2, 2],
        mode="lines+text",
        line=dict(color="black", width=4),
        text=["S", "N"],
        textposition="top center",
        name="",
    )
    ew_line = go.Scatter3d(
        x=[-2, 2], y=[0, 0], z=[2, 2],
        mode="lines+text",
        line=dict(color="black", width=4),
        text=["O", "E"],
        textposition="top center",
        name="",
    )
    norte_flecha = go.Cone(
        x=[0], y=[2], z=[2],
        u=[0], v=[1], w=[0],
        sizemode="absolute",
        sizeref=1,
        anchor="tail",
        colorscale=[[0, "red"], [1, "red"]],
        showscale=False,
        name="Norte",
    )

    slip_vec = np.cos(rake_rad) * strike_vec + np.sin(rake_rad) * dip_vec
    slip_vec = slip_vec / np.linalg.norm(slip_vec)

    plane_normal = np.cross(strike_vec, dip_vec)
    plane_normal /= np.linalg.norm(plane_normal)
    v1 = strike_vec / np.linalg.norm(strike_vec)
    v2 = np.cross(plane_normal, v1)

    frames = []
    for step in range(steps):
        if step == 0:
            q1 = p1
        else:
            q1 = p1 * plane_normal + slip_vec * (step * 0.1)

        q2 = q1 + width * v1
        q3 = q2 + height * v2
        q4 = q1 + height * v2

        q5 = np.array([q1[0] - width, q1[1], q1[2]])
        q6 = np.array([q2[0] - width, q2[1], q2[2]])
        q7 = np.array([q6[0], q6[1], q3[2]])
        q8 = np.array([q5[0], q5[1], q4[2]])

        vx = [q1[0], q2[0], q3[0], q4[0], q5[0], q6[0], q7[0], q8[0]]
        vy = [q1[1], q2[1], q3[1], q4[1], q5[1], q6[1], q7[1], q8[1]]
        vz = [q1[2], q2[2], q3[2], q4[2], q5[2], q6[2], q7[2], q8[2]]

        faces_cuna = [
            [0, 1, 2], [0, 2, 3],
            [4, 5, 6], [4, 6, 7],
            [0, 1, 5], [0, 5, 4],
            [1, 2, 6], [1, 6, 5],
            [2, 3, 7], [2, 7, 6],
            [3, 0, 4], [3, 4, 7],
        ]
        i_c, j_c, k_c = zip(*faces_cuna)

        slip_cuna = go.Mesh3d(
            x=vx, y=vy, z=vz,
            i=i_c, j=j_c, k=k_c,
            color="seagreen", opacity=0.666,
            name="Bloque superior en movimiento",
        )
        frames.append(
            go.Frame(data=[beachball_plot, wedge, plane, ns_line, ew_line, slip_cuna], name=f"frame{step}")
        )

    initial_cuna = frames[0].data[-1]

    layout = go.Layout(
        showlegend=False,
        title=dict(
            text="<b>M 7.8 - Terremoto de Perdernales, Manabí - Ecuador (2016)</b>",
            x=0.5,
            font=dict(size=18),
        ),
        scene=dict(
            xaxis=dict(title="Longitud (°)", tickvals=[-5, 0, 5], ticktext=["-82.5°", "-81.0°", "-79.5°"]),
            yaxis=dict(title="Latitud (°)", tickvals=[-5, 0, 5], ticktext=["-2.5°", "1°", "2.5°"]),
            zaxis=dict(title="Profundidad (km)", showticklabels=False, ticks=""),
            aspectmode="data",
            camera=dict(eye=eye_dict),
            annotations=[
                dict(x=8, y=0, z=-4, text="PLACA SUDAMERICANA", showarrow=False, font=dict(color="black", size=16)),
                dict(x=q1[0] - 2, y=q1[1], z=q1[2] - 4, text="PLACA NAZCA", showarrow=False, font=dict(color="black", size=16)),
            ],
        ),
        annotations=[
            dict(
                xref="paper",
                yref="paper",
                x=0.01,
                y=1.05,
                showarrow=False,
                align="left",
                text=(
                    "<b>Fecha:</b> 2016-04-16 23:58:36 UTC<br>"
                    "<b>Ubicación:</b> 0.382°N, 79.922°W<br>"
                    "<b>Profundidad:</b> 21.5 km<br>"
                    "<b>Magnitud:</b> 7.8 Mw<br>"
                    "<b>Momento:</b> 7.054×10²⁰ N·m<br>"
                    f"<b>Plano Nodal 1:</b> Strike {strike_angle_deg}°, Dip {dip_angle_deg}°, Rake {rake_angle_deg}°<br>"
                    "<b>Plano Nodal 2:</b> Strike 26°, Dip 16°, Rake 113°<br>"
                ),
                font=dict(size=15),
                bordercolor="black",
                borderwidth=1,
                bgcolor="white",
                opacity=0.9,
            )
        ],
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(label="Play", method="animate", args=[None]),
                    dict(
                        label="Pausa",
                        method="animate",
                        args=[[None], {"mode": "immediate", "frame": {"duration": 0}, "transition": {"duration": 0}}],
                    ),
                    dict(label="Reset Camera", method="relayout", args=[{"scene.camera": dict(eye=eye_dict)}]),
                ],
            )
        ],
    )

    fig = go.Figure(
        data=[beachball_plot, wedge, plane, ns_line, ew_line, initial_cuna, norte_flecha],
        layout=layout,
        frames=frames,
    )
    return fig