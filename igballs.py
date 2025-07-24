"""Run an igballs fault visualisation from CLI or configuration file."""

import argparse
import configparser
import logging

import igballs_fault
import json

logger = logging.getLogger(__name__)


def load_config(cfg_path: str) -> dict:
    """Load configuration parameters from a cfg file."""
    config = configparser.ConfigParser()
    config.read(cfg_path)

    import pprint
    pprint.pprint({s: dict(config.items(s)) for s in config.sections()})
    eye_dict_raw = json.loads( config["ANIMATION"]["eye_dict"])
    eye_dict = {k: float(v) for k, v in eye_dict_raw.items()}


    params = {
        "strike_angle_deg": config.getfloat("FAULT", "strike_angle_deg", fallback=183),
        "dip_angle_deg": config.getfloat("FAULT", "dip_angle_deg", fallback=75),
        "rake_angle_deg": config.getfloat("FAULT", "rake_angle_deg", fallback=84),
        "latitude" : config.getfloat("FAULT","latitude"),
        "longitude" : config.getfloat("FAULT","longitude"),
        "depth" : config.getfloat("FAULT","depth"),        
        "width": config.getfloat("CUBE", "width", fallback=10),
        "height": config.getfloat("CUBE", "height", fallback=5),
        "radius": config.getfloat("BALL","radius",fallback=3.3),
        "resolution": config.getint("BALL","resolution",fallback=333),
        "invert_colors": config.getboolean("BALL","invert_colors",fallback=False),
        "move_block" : config.get("ANIMATION","move_block", fallback="east"),        
        "steps": config.getint("ANIMATION", "steps", fallback=25),
        "eye_dict":eye_dict,
        "output_html":config.get("ANIMATION","output_html",fallback="./moving_blocks.html")
        
    }

    logger.info("Configuration loaded from %s", cfg_path)
    logger.debug("Parameters: %s", params)
    return params


def main() -> None:
    """Parse command line arguments and show the figure."""
    parser = argparse.ArgumentParser(
        description="Visualize fault geometry using igballs",
    )
    parser.add_argument(
        "--config",
        default="igballs.cfg",
        help="Path to configuration file with fault parameters",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )


    args = parser.parse_args()

    logging.basicConfig(level=args.log_level.upper(), format="%(levelname)s:%(message)s")

    logger.info("Using configuration file %s", args.config)
    params = load_config(args.config)

    fig = igballs_fault.create_figure(
        params["strike_angle_deg"],
        params["dip_angle_deg"],
        params["rake_angle_deg"],
        params["latitude"],
        params["longitude"],
        params["depth"],
        params["move_block"],
        params["width"],
        params["height"],
        params["steps"],
        params["eye_dict"],
        params["radius"],
        params["resolution"],
        params["invert_colors"]
        
    )
    logger.info("Showing figure")


    # Exportar HTML completo
    fig.write_html(params["output_html"], include_plotlyjs="cdn", full_html=True, config={"responsive": True}   )

    
    # Insertar el CSS justo antes de </head>
    with open(params["output_html"], "r") as f:
        html = f.read()

        mobile_style = """
        <style>
        html, body {
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            overflow: hidden;
        }

    .plotly-graph-div {
        height: 100% !important;
        width: 100% !important;
        position: absolute !important;
        top: 0;
        left: 0;
    }

        .modebar-btn {
            transform: scale(1.8);
            margin: 8px;
        }
        </style>
        """


        html = html.replace("<head>", f"<head>{mobile_style}", 1)

    with open(params["output_html"], "w") as f:
        f.write(html)

    print(f"HTML exportado a: {params['output_html']}")   
    
    fig.show()



if __name__ == "__main__":
    main()


