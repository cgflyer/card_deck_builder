import os
import pandas as pd
import glob
import logging
from card_face_builder import plugin
from card_face_builder.helper import CardDeckConfig
from card_face_builder.utils import IndentedLogger

logger = IndentedLogger(logging.getLogger(__name__))

import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Card Face Builder")

    # Define CLI arguments
    parser.add_argument("--filter", type=str, default=None,
                        help="A prefix match pattern to restrict which cards are generated")
    parser.add_argument("--verbose", action="count", default=0,
                        help="For controlling log output verbosity, repeat for more detail")
    parser.add_argument("--output-dir", default="output", help="Output file path")
    parser.add_argument("card_defs", type=str, help="A csv file defining the cards and faces")

    args = parser.parse_args()
    return args


# Define file paths
base_image_path = "images/wizard-cards"
mask_path = "layer-builder/mask-layer.xcf"
info_path = "layer-builder/info-layer.xcf"
icon_dir = "images/dice-icons"

# Define parameters
number_text = "7"
icon_codes = ["oc", "cc"]
output_path = "output/final_image.png"

def main(card_defs, filter_spec, output_dir):
    card_deck = CardDeckConfig(card_defs)
    logger.info(f"card deck loaded with {card_deck.num_cards()}")
    
    image = plugin.load_base_image(base_image_path)
    info_layer = plugin.build_info_layer(image, mask_path, info_path)

    plugin.add_text(info_layer, number_text, x=64, y=500, font_size=128)
    plugin.add_icons(info_layer, icon_codes, icon_dir, grid_position=(image.width - 256 - 64, 64))

    plugin.save_image(image, output_path)
    print(f"Dice image saved to: {output_path}")

if __name__ == "__main__":
    args = parse_args()
    log_levels = {0: logging.ERROR, 1: logging.INFO, 2:logging.DEBUG}
    verbose_level = log_levels.get(args.verbosity, logging.ERROR)
    logging.basicConfig(level=verbose_level)
    main(args.card_defs, args.filter, args.output_dir)