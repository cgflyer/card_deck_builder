#!/usr/bin/env python3

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   GIMP - The GNU Image Manipulation Program
#   Copyright (C) 1995 Spencer Kimball and Peter Mattis
#
#   gimp-tutorial-plug-in.py
#   sample plug-in to illustrate the Python plug-in writing tutorial
#   Copyright (C) 2023 Jacob Boerema
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi

from gi.repository import GLib
from gi.repository import Gio
from typing import Any
from pathlib import Path
import os
#from utils import IndentedLogger
import logging


#logger = IndentedLogger(logging.getLogger(__name__))
logger = logging.getLogger(__name__)

class CardDeckBuilderPlugin (Gimp.PlugIn):
    def do_query_procedures(self):
        return [ "cfb-add-background" ]

    def do_set_i18n (self, name):
        return False

    def do_create_procedure(self, name):
        if name == "cfb-add-background":
            return self.do_create_procedure_add_background(name)
        
    def do_create_procedure_add_background(self, name):
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            self.run_add_background, None)

        procedure.set_image_types("*")

        procedure.set_menu_label("CardFaceBuilder plug-in add background")
        procedure.add_menu_path('<Image>/Filters/CardDeck/')

        procedure.set_documentation("Card Deck image builder - add background",
                                    "Handles adding background to card face image",
                                    name)
        procedure.set_attribution("Charles Galles", "Charles Galles", "2025")

        return procedure

    def run_add_background(self, procedure, run_mode, image, drawables, config, run_data):
        Gimp.message(f"Add Background - would add to image with size {image.get_width()},{image.get_height()}")
        # do what you want to do, then, in case of success, return:
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


def add_background_layer(image, selected_layer):
    # Convert the hex color to RGB
    bg_color = Gimp.RGB()
    bg_color.r = 0xf9 / 255.0
    bg_color.g = 0xfb / 255.0
    bg_color.b = 0xef / 255.0

    # Start undo group
    Gimp.context_push()
    image.undo_group_start()

    # Create new layer
    background_layer = Gimp.Layer.new(image,
                                      "Background",
                                      image.width,
                                      image.height,
                                      Gimp.ImageBaseType.RGB_IMAGE,
                                      bg_color,
                                      100.0,
                                      Gimp.LayerMode.NORMAL)

    # Insert it below the selected layer
    selected_index = image.get_item_position(selected_layer)
    image.insert_layer(background_layer, None, selected_index)

    # End undo group
    image.undo_group_end()
    Gimp.context_pop()

# Example call within a plug-in context
# add_background_layer(image, image.get_selected_layer())
def add_text_layer_to_info_layer(image, card_value):
    font = "Sans"
    size = 128.0
    text_layer = Gimp.TextLayer.new(
        image, card_value, font, size, Gimp.Unit.PIXEL
    )
    return text_layer

def adjust_base_image(image, opacity = 60.0, bg_color = (0xf9 / 255, 0xfb / 255, 0xef / 255)):        
        # Get active layer
        base_layer = image.get_active_layer()

        # Set base layer opacity to 60%
        base_layer.set_opacity(opacity)

        # Create background layer with color #f9fbef
        bg_layer = Gimp.Layer.new(
            image, "Background", image.get_width(), image.get_height(),
            Gimp.ImageType.RGB_IMAGE, 100.0, Gimp.LayerMode.NORMAL
        )
        image.insert_layer(bg_layer, None, 0)
        bg_layer.fill(Gimp.FillType.WHITE)
        bg_layer.set_color(bg_color)

        # Reinsert base layer above background
        image.remove_layer(base_layer)
        image.insert_layer(base_layer, None, 1)

def build_mask_layer(image, mask_path, run_mode):
    mask_file = Gio.File.new_for_path(mask_path)
    mask_image = Gimp.file_load(mask_file, mask_file, run_mode)
    mask_layer = mask_image.get_active_layer()
    image.insert_layer(mask_layer.copy(), None, -1)
    return mask_layer


class CardFrontLayerBuilder(Gimp.PlugIn):
    def do_query_procedures(self):
        return ['python-fu-card-front-layer-builder']

    def do_create_procedure(self, name):
        procedure = Gimp.Procedure.new(
            self, name, Gimp.PDBProcType.PLUGIN, self.run, None
        )
        procedure.set_menu_label("Build Card Front Layers")
        procedure.set_documentation("Builds layered card front image with mask and info overlays", "Builds layered dice image with mask and info overlays", name)
        procedure.set_attribution("Charles & Copilot", "Charles & Copilot", "2025")
        procedure.set_image_types("*")
        procedure.add_menu_path("<Image>/Filters/Custom/")
        procedure.add_argument_string("number", "Card Number", "Number to display on the info layer")
        procedure.add_argument_string("cost_info", "Cost Info", "The cost of card as comma separated row codes")
        procedure.add_argument_string("name_info", "Wizard Name", "The name of card as comma separated row codes")
        return procedure

    def run(self, procedure, run_mode, image, n_drawables, drawables, args, run_data):
        with logger.log_block("run", procedure, run_mode):
            number = args.index(0) if args else "1"
            cost_code = args.index(1) if args else "s"
            wizard_name = args.index(2) if args else "Nameless Unknown"
            sect = args.index(3) if args else "S"
            layers_dir = Path("card-face-builder/layers")

            card_config = CardFaceConfig(number, cost_code, sect, wizard_name)
            logger.info(f"card config settings: {card_config}")
            adjust_base_image(image, opacity = 60.0, bg_color = (0xf9 / 255, 0xfb /255 , 0xef / 255))

            # Add mask layer
            maske_layer = build_mask_layer(image, str(layers_dir / "info-mask.png"), run_mode)

            info_layer = build_info_layer(image, str(layers_dir / "info-layer.png"), run_mode)

            # Add text layer to info layer
            text_layer = add_text_layer_to_info_layer(image, card_config.value)
            text_layer.set_offsets(64, 500)
            image.insert_layer(text_layer, info_layer, -1)

            paste_icons_to_layer(image, info_layer, card_config)


            return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

Gimp.main(CardDeckBuilderPlugin.__gtype__, sys.argv)
