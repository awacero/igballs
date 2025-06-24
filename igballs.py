# Reimportar librerías tras el reset del entorno
import numpy as np
import plotly.graph_objects as go
from scipy.spatial.transform import Rotation as R
import configparser

import igballs_fault 


# Parámetros
strike_angle_deg = 183
dip_angle_deg = 75
rake_angle_deg = 84
width = 10 ##increase size in N-S
height = 5
depth_z = 5
steps = 25
slip_cuña_width = 10
slip_cuña_height = 5
slip_cuña_depth = 5
eye_dict = dict(x=-1, y=-3, z=2) ###x: este - oest, y: norte-sur, z: altura


fig = igballs_fault.create_figure(strike_angle_deg, dip_angle_deg, rake_angle_deg)
fig.show()