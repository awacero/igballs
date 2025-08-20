import numpy as np
import plotly.graph_objects as go
import igballs_balls 

import pandas as pd
import plotly.graph_objects as go

def add_coastlines_from_csv(fig, csv_path):
    """
    Agrega líneas costeras desde un archivo CSV (latitud, longitud) a la figura 3D.

    Args:
        fig: objeto plotly.graph_objects.Figure
        csv_path: ruta al archivo CSV con columnas latitud, longitud
    """
    try:
        df = pd.read_csv(csv_path)
        if df.empty:
            print("El archivo CSV está vacío.")
            return

        # Agrupar por NaNs para separar segmentos
        mask = df['latitud'].isna()
        segments = []
        current = []

        for i, row in df.iterrows():
            if mask[i]:
                if current:
                    segments.append(current)
                    current = []
            else:
                current.append((row['latitud'], row['longitud']))
        if current:
            segments.append(current)

        # Dibujar segmentos
        for segment in segments:
            lats, lons = zip(*segment)
            fig.add_trace(go.Scatter3d(
                x=lons,
                y=lats,
                z=[0] * len(lats),  # z=0 para proyectar en superficie
                mode='lines',
                line=dict(color='black', width=4),
                name='Coastline'
            ))

    except Exception as e:
        print(f"Error al cargar el archivo de líneas costeras: {e}")

def crear_cruz_direcciones(latitude, longitude, depth, cross_shift=10, cross_lat=5, cross_lon=5):
    """
    Crea las líneas NS, EW y la flecha del norte para visualización 3D.
    Devuelve: (ns_line, ew_line, norte_flecha)
    """
    import numpy as np
    import plotly.graph_objects as go

    origin = np.array([latitude, longitude, depth])
    origin_axes = origin + cross_shift

    # Línea Norte-Sur
    ns_line = go.Scatter3d(
        x=[origin_axes[0], origin_axes[0]],
        y=[origin_axes[1] - cross_lat, origin_axes[1] + cross_lat],
        z=[origin_axes[2] + 4, origin_axes[2] + 4],
        mode="lines+text",
        line=dict(color="black", width=4),
        text=["S", "N"],
        textposition="top center",
        name="",
    )

    # Línea Este-Oeste
    ew_line = go.Scatter3d(
        x=[origin_axes[0] - cross_lon, origin_axes[0] + cross_lon],
        y=[origin_axes[1], origin_axes[1]],
        z=[origin_axes[2] + 4, origin_axes[2] + 4],
        mode="lines+text",
        line=dict(color="black", width=4),
        text=["O", "E"],
        textposition="top center",
        name="",
    )

    # Flecha del norte
    norte_flecha = go.Cone(
        x=[origin_axes[0]],
        y=[origin_axes[1] + cross_lat],
        z=[origin_axes[2] + 4],
        u=[0],
        v=[1],
        w=[0],
        sizemode="absolute",
        sizeref=2.2,
        anchor="tail",
        colorscale=[[0, "red"], [1, "red"]],
        showscale=False,
        name="Norte",
    )

    return ns_line, ew_line, norte_flecha

    '''
    strike_deg: float,
    dip_deg: float,
    rake_deg: float,
    latitude: float,
    longitude: float,
    depth: float,
    plate_a: str,
    plate_b: str,
    '''

def create_figure(
    event: dict,
    plane: str,
    move_block: str,
    block_width: float,
    height: float,
    steps: int,
    speed: float,
    eye_dict : dict,
    radius: float,
    resolution: int,
    invert_colors : float
    ) -> go.Figure:

    """Load parameters"""
    event_title = event["title"]
    event_datetime = event["datetime"]
    event_magnitude = event["magnitude"]
    latitude,longitude,depth = event['latitude'],event['longitude'],event['depth']
    strike_deg,dip_deg,rake_deg = event['nodal_planes'][plane]['strike'], event['nodal_planes'][plane]['dip'],\
                                    event['nodal_planes'][plane]['rake']
    plate_a = event["plate_a"]
    plate_b = event["plate_b"]
    origin = np.array([latitude,longitude,depth])  
    strike_rad = np.radians(strike_deg)
    dip_rad = np.radians(dip_deg)
    rake_rad = np.radians(rake_deg)

    strike_unit = np.array([np.sin(strike_rad), np.cos(strike_rad), 0])
    dip_unit = np.array([
        np.cos(strike_rad) * np.cos(dip_rad),
        -np.sin(strike_rad) * np.cos(dip_rad),
        -np.sin(dip_rad),
    ])
    strike_vector = block_width * strike_unit
    dip_vector = height * dip_unit
    normal_vector = np.cross(strike_unit, dip_unit)
    normal_unit = normal_vector / np.linalg.norm(normal_vector)

    slip_vector = np.cos(rake_rad) * strike_unit + np.sin(rake_rad) * dip_unit
    slip_unit = slip_vector / np.linalg.norm(slip_vector)


    """Create static objects"""
    """Create compass rose"""
    # Escalas en grados (aprox. 1° latitud ≈ 111 km)
    cross_lat = 5  # ~5.5 km
    cross_lon = 5  # ~5.5 km en esta latitud
    cross_shift = 10

    # --- Parámetros del plano de falla ------------------------------------
    plane_factor = 3.0            # (≥1) escala respecto a la cara original
    plane_color  = "red"          # cambia a gusto
    plane_opacity = 0.35


    ns_line, ew_line, norte_flecha = crear_cruz_direcciones(latitude, longitude, depth,cross_shift, cross_lat,cross_lon)




    """Create beach ball"""
    bb1 = origin - 0.5 * strike_vector - 0.5 * dip_vector
    bb3 = origin + 0.5 * strike_vector - 0.5 * dip_vector

    center = (bb1 + bb3) / 2
    beachball_plot = igballs_balls.create_beach_ball(
        center, strike_unit, dip_unit, normal_unit, rake_deg,radius, resolution,invert_colors   )


    """Create a cool fault plane"""
    # --- Cálculo de los 4 vértices del plano (rectángulo) ------------------
    half_s   = 0.5 * plane_factor * strike_vector   # vector mitad‑long. (strike)
    half_d   = 0.5 * plane_factor * dip_vector      # vector mitad‑anch. (dip)

    # Centro del plano: p1 + p3 ya lo calculaste antes en ‘center’
    plane_p1 = center - half_s - half_d   # esquina inferior‑izquierda
    plane_p2 = center + half_s - half_d   # esquina inferior‑derecha
    plane_p3 = center + half_s + half_d   # esquina superior‑derecha
    plane_p4 = center - half_s + half_d   # esquina superior‑izquierda

    plane = go.Mesh3d(
        x=[plane_p1[0], plane_p2[0], plane_p3[0], plane_p4[0]],
        y=[plane_p1[1], plane_p2[1], plane_p3[1], plane_p4[1]],
        z=[plane_p1[2], plane_p2[2], plane_p3[2], plane_p4[2]],
        i=[0, 0], j=[1, 3], k=[2, 2],                # dos triángulos
        color=plane_color,
        opacity=plane_opacity,
        name="Plano de falla",hoverinfo="none",
        flatshading=True,
)




    # ---------- Parámetros ----------
    arrow_len     = 0.7 * radius     # km   (largura del vector)
    arrow_radius  = 0.5 * radius    # km   (grosor del cono)
    arrow_color   = "red"
    arrow_offset  = 1.3 * radius     # km   (separación del plano)

    # Posición de las colas (± normal)
    tail1 = center +  normal_vector * arrow_offset
    tail2 = center -  normal_vector * arrow_offset

    # Componentes del vector deslizamiento, escalado a arrow_len
    slip_unit = slip_vector / np.linalg.norm(slip_vector)
    u, v, w = (slip_unit * arrow_len)


    if move_block.lower() == "east":
        dir_plus, dir_minus = -slip_unit,  slip_unit
    elif move_block.lower() == "west":
        dir_plus, dir_minus =  slip_unit, -slip_unit
    else:                           # ambos fijos: muestra deslizamiento relativo
        dir_plus, dir_minus =  slip_unit, -slip_unit

    u1, v1, w1 = (dir_plus  * arrow_len)
    u2, v2, w2 = (dir_minus * arrow_len)



    # --------- Flecha bloque 1  (se mueve +slip) ----------
    arrow1 = go.Cone(
        x=[tail1[0]], y=[tail1[1]], z=[tail1[2]],
        u=[ u1], v=[ v1], w=[ w1],
        anchor="tail",              # la cola está en (x,y,z)
        sizemode="absolute",
        sizeref=arrow_len,
        showscale=False,
        colorscale=[[0, arrow_color], [1, arrow_color]],
        name="Desplazamiento 1"
    )

    # --------- Flecha bloque 2  (‑slip) ----------
    arrow2 = go.Cone(
        x=[tail2[0]], y=[tail2[1]], z=[tail2[2]],
        u=[u2], v=[v2], w=[w2],
        anchor="tail",
        sizemode="absolute",
        sizeref=arrow_len,
        showscale=False,
        colorscale=[[0, arrow_color], [1, arrow_color]],
        name="Desplazamiento 2"
    )


    static_traces = [arrow1, arrow2, beachball_plot,  plane,ns_line,ew_line,norte_flecha]
    #static_traces = []
    faces = [
            [0, 1, 2], [0, 2, 3],
            [4, 5, 6], [4, 6, 7],
            [0, 1, 5], [0, 5, 4],
            [1, 2, 6], [1, 6, 5],
            [2, 3, 7], [2, 7, 6],
            [3, 0, 4], [3, 4, 7],
        ]

    # Proyección escalar del vector normal sobre cada eje
    proj_x = np.dot(normal_unit, [1, 0, 0])
    proj_y = np.dot(normal_unit, [0, 1, 0])
    proj_z = np.dot(normal_unit, [0, 0, 1])

    normal_proj = np.array([proj_x,proj_y,0])

    dip_x = np.dot(dip_unit,[1,0,0])
    dip_y = np.dot(dip_unit,[0,1,0])
    dip_z = np.dot(dip_unit,[0,0,1])
    
    dip_proj = np.array([0,0,dip_z])
    
    frames = []
    for step in range(steps):      

        if step == 0:
            p1 = origin - 0.5 * strike_vector - 0.5 * dip_vector
            q1 = p1
        else:
            if move_block == "east":
                p1 = (origin - 0.5 * strike_vector - 0.5 * dip_vector) + slip_unit * (step * speed)
                q1 = p1 - 2*slip_unit * (step * speed)
            elif move_block == "west":
                q1 = p1 - slip_unit * (step * speed)
            else:  # "none"
                q1 = p1
        
        ##BLOCK EAST
        p2 = p1 + strike_vector
        p3 = p2 + dip_vector
        p4 = p1 + dip_vector  
        ##Here is the error 
        #p7 = p3 + normal_proj*block_width*1.5
        #p8 = p4 + normal_proj*block_width*1.5
        #alpha = np.arccos(p1[0]/)
        aux = p2 -p3 
        p7 = np.array([p3[0]+aux[0], p3[1]+aux[1],p3[2]]) + normal_proj*block_width
        p8 = np.array([p4[0]+aux[0], p4[1]+aux[1],p4[2]]) + normal_proj*block_width
        p5 = p8 - dip_proj * height
        p6 = p7 - dip_proj * height

        vertices = np.array([p1, p2, p3, p4, p5, p6, p7, p8])
        x, y, z = vertices.T
        i, j, k = zip(*faces)

        block_east = go.Mesh3d(
            x=x, y=y, z=z, i=i, j=j, k=k, color="steelblue", opacity=0.6,
            name="block_east",hoverinfo="none"
        )

        ##BLOCK EAST UPPER
        p1u = p1 - dip_vector/3
        p2u = p2 - dip_vector/3 
        p3u = p2
        p4u = p1      
        p5u = p5 - dip_proj*height/3
        p6u = p6 - dip_proj*height/3
        p7u = p6
        p8u = p5

        vertices_u = np.array([p1u, p2u, p3u, p4u, p5u, p6u, p7u, p8u])
        xu, yu, zu = vertices_u.T
        iu, ju, ku = zip(*faces)

        block_east_upper = go.Mesh3d(
            x=xu, y=yu, z=zu, i=iu, j=ju, k=ku,
            color="peru", opacity=0.7,
            name="block_east_upper"
            ,hoverinfo="none"
        )

        q2 = q1 + strike_vector
        q3 = q2 + dip_vector
        q4 = q1 + dip_vector

        q7 = q3 - normal_proj*block_width
        q8 = q4 - normal_proj*block_width
        q5 = q8 - dip_proj*height
        q6 = q7 - dip_proj*height

        vertices_q = np.array([q1,q2,q3,q4,q5,q6,q7,q8])
        xq,yq,zq = vertices_q.T
        iq, jq, kq = zip(*faces)

        block_west = go.Mesh3d(
            x=xq, y=yq, z=zq,
            i=iq, j=jq, k=kq,
            color="sandybrown", opacity=0.666,
            name="block_west",hoverinfo="none"
        )


        q1u = q1 - dip_vector/3
        q2u = q2 - dip_vector/3
        q3u = q2
        q4u = q1
        q5u = q5 - dip_proj*height/3
        q6u = q6 - dip_proj*height/3
        q7u = q6
        q8u = q5

        vertices_qu = np.array([q1u, q2u, q3u,q4u,q5u, q6u, q7u, q8u])
        xqu, yqu,zqu = vertices_qu.T

        iuq,juq,kuq = zip(*faces)
        block_west_upper = go.Mesh3d(
            x=xqu, y=yqu, z=zqu, i=iuq, j=juq, k=kuq,
            color="peru", opacity=0.7,
            name="block_west_upper",hoverinfo="none"
        )

        frames.append(
            go.Frame(data=[block_east, block_west, 
                           block_east_upper, 
                           block_west_upper
                           ], name=f"frame{step}")
        )

        # Create annotations for points p1 to p8
        annotations_p = []
        for i, point in enumerate([p1, p2, p3, p4, p5, p6, p7, p8], start=1):
            annotations_p.append(dict(
                x=point[0],
                y=point[1],
                z=point[2],
                text=f'p{i}',
                showarrow=True,
                arrowhead=1,
                ax=0,
                ay=-20,
                font=dict(color='black', size=12),
                xanchor="center",
                yanchor="middle"
            ))

        annotations_pu = []
        for i, point in enumerate([p1u, p2u, p3u, p4u, p5u, p6u, p7u, p8u], start=1):
            annotations_pu.append(dict(
                x=point[0],
                y=point[1],
                z=point[2],
                text=f'p{i}u',
                showarrow=True,
                arrowhead=1,
                ax=0,
                ay=-20,
                font=dict(color='red', size=16),
                xanchor="center",
                yanchor="middle"
            ))

        annotations_q = []
        for i, point in enumerate([q1u, q2u, q3u, q4u, q5u, q6u, q7u, q8u], start=1):
            annotations_q.append(dict(
                x=point[0],
                y=point[1],
                z=point[2],
                text=f'q{i}u',
                showarrow=True,
                arrowhead=1,
                ax=0,
                ay=-20,
                font=dict(color='black', size=12),
                xanchor="center",
                yanchor="middle"
            ))
    


    initial_block_east = frames[0].data[0]
    initial_block_west = frames[0].data[1]
    initial_block_east_upper = frames[0].data[2]
    initial_block_west_upper = frames[0].data[3]

    layout = go.Layout(
        showlegend=False,
        title=dict(
            text=f"<b>{event_title}</b>",
            x=0.5,
            font=dict(size=18),
        ),
        scene=dict(
            xaxis=dict(title="Longitud (°)", ),
            yaxis=dict(title="Latitud (°)", ),
            
            
            zaxis=dict(title="Profundidad (km)", showticklabels=False, ticks=""),
            aspectmode="data",
            camera=dict(eye=eye_dict),
            annotations= 
            #annotations_p +
            #annotations_pu +
            [   ##POSICION DE ETIQUETAS 
                dict(x=p7[0], y=p7[1], z=p7[2], text=f"{plate_a}", showarrow=False, font=dict(color="black", size=16)),
                dict(x=q7[0], y=q7[1], z=q7[2], text=f"{plate_b}", showarrow=False, font=dict(color="black", size=16)),
            ],
        ),
        annotations= 
                
                [
            dict(
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.95,
                showarrow=False,
                align="left",
                text=(
                    f"<b>Fecha:</b> {event_datetime} <br>"
                    f"<b>Ubicación:</b>{longitude},{latitude} <br>"
                    f"<b>Profundidad:</b> {depth}<br>"
                    f"<b>Magnitud:</b> {event_magnitude}<br>"
                    f"<b>Plano:</b> Strike {strike_deg}°, Dip {dip_deg}°, Rake {rake_deg}°<br>"
                ),
                font=dict(size=15),
                bordercolor="black",
                borderwidth=1,
                bgcolor="white",
                opacity=0.9,
            )
        ],
    )


    fig = go.Figure(
        data= [initial_block_east, initial_block_west, 
               initial_block_east_upper,  
               initial_block_west_upper
               ] + static_traces,
        layout=layout,
        frames=frames,
    )

    fig.update_layout(
    modebar=dict(
        orientation='v',
        bgcolor='#E9E9E9',
        color='black',
        activecolor='#9ED3CD'
    ),

    autosize=True,
    #width=800,    # o usa una proporción de la pantalla
    #height=600,   # puedes aumentar a 700 o más
    margin=dict(l=10, r=10, t=33, b=10),  # márgenes pequeños para maximizar espacio
    scene=dict(
        aspectmode="data"  # o "cube", o "manual" si quieres fijarlo
    ),

    updatemenus=[
        dict(
            type="buttons",
            direction="left",  # Botones en fila
            x=0.1,              # Posición horizontal (entre 0 y 1)
            y=0.0,              # Posición vertical (entre 0 y 1)
            xanchor="left",
            yanchor="bottom",
            pad=dict(r=10, t=10),  # Espaciado alrededor
            showactive=True,
            font=dict(size=20),   # Tamaño del texto de los botones
            buttons=[
                dict(
                    label="▶️ Play",
                    method="animate",
                    args=[
                        None,
                        
                        dict(
                            frame=dict(duration=100, redraw=True),
                            fromcurrent=True,
                            mode="immediate"
                        )
                        
                    ]
                ),
                dict(
                    label="⏸️ Pausa",
                    method="animate",
                    args=[[None], {"mode": "immediate", "frame": {"duration": 0}, "transition": {"duration": 0}}]
                ),
                dict(
                    label="🔄 Reset Camera",
                    method="relayout",
                    args=[{"scene.camera": dict(eye=eye_dict)}]
                )
            ]
        )
    ]


)


    return fig