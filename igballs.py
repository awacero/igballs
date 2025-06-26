"""Run an igballs fault visualisation from CLI or configuration file."""

import argparse
import configparser
import logging

import igballs_fault
import json

logger = logging.getLogger(__name__)

print("INCIOCIOOOOOO")

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
        "width": config.getfloat("CUBE", "width", fallback=10),
        "height": config.getfloat("CUBE", "height", fallback=5),
        "steps": config.getint("ANIMATION", "steps", fallback=25),
        "eye_dict":eye_dict,
        


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
        params["width"],
        params["height"],
        params["steps"],
        params["eye_dict"]
        
    )
    logger.info("Showing figure")
    fig.show()


if __name__ == "__main__":
    main()


