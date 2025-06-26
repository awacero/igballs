# igballs

Visualize fault geometry and slip motion using Plotly. The scripts in this repository generate an interactive 3D view of the 2016 Pedernales (Ecuador) earthquake model.

## Requirements

- Python 3
- [Plotly](https://pypi.org/project/plotly/)
- [NumPy](https://pypi.org/project/numpy/)

Install the packages with:

```bash
pip install plotly numpy
```

## Running

The main entry point is `igballs.py`. It expects a configuration file with the fault parameters. A minimal example is shown below:

```ini
[FAULT]
strike_angle_deg = 183
dip_angle_deg = 75
rake_angle_deg = 84

[CUBE]
width = 10
height = 5

[ANIMATION]
steps = 25
eye_dict = {"x": -1, "y": -3, "z": 2}
```

Run the visualisation with:

```bash
python igballs.py --config igballs.cfg
```

Use `--log-level DEBUG` for verbose output. When executed successfully, a Plotly window will open showing the animated fault model.

## Example

Running the configuration above will produce an interactive 3D scene with the fault plane, beachball and moving block. (A screenshot can be added here in the future.)
