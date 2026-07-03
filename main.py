from __future__ import annotations

import argparse
import json
from pathlib import Path

from config.settings import load_settings
from src.core.pipeline import FalseBreakoutPipeline
from src.utils.logger import configure_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect support, resistance, trendlines, and false breakouts from OHLCV data.")
    parser.add_argument("--config", default="config/config.yaml", help="Path to YAML configuration file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = Path(__file__).resolve().parent / config_path
    settings = load_settings(config_path)
    configure_logging(settings.logging.level, settings.resolve(settings.logging.file))
    result = FalseBreakoutPipeline(settings).run()
    print(json.dumps({"dashboard": str(result.dashboard_path), "metrics": result.metrics}, indent=2))


if __name__ == "__main__":
    main()
