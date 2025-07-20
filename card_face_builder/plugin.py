#!/usr/bin/env python3

from gi.repository import Gimp, GimpUi, Gio, GLib
from typing import Any
from pathlib import Path
import os
import sys
from utils import IndentedLogger
import logging


logger = IndentedLogger(logging.getLogger(__name__))


def paste_icons_to_layer(image: Any, info_layer: Gimp.Layer, card_config: CardFaceConfig, icon_dir="images/dice-icons", 
                 icon_size=128, grid_border=8, inset=64, project_home="card-face-builder"):
    
    icon_path = Path(project_home) / icon_dir
    # Calculate starting position (top-right corner inset)
    img_width = image.get_width()
    row_codes = card_config.cost.split(",")
    start_x = inset
    start_y = inset

    # Map codes to filenames
    code_to_file = {
        "o": "4-orb_128.png",
        "c": "5-crystal_128.png",
        "h": "6-hat_128.png",
        "s": "1-staff_128.png"
        # Add more mappings as needed
    }
    font = "Sans"
    for idx, row_code in enumerate(row_codes):
        x_pos = img_width - (inset + len(row_code) * (icon_size + grid_border) - grid_border)
        y_pos = inset + idx * (icon_size + grid_border)
        for icon_col_idx, code in enumerate(row_code):
            if code.isdigit():
                # this is a count followed by number of icon required
                staff_count = code
                text_layer = Gimp.TextLayer.new(image, staff_count, font, 64.0, Gimp.Unit.PIXEL)
                Gimp.edit_copy(text_layer)

            elif code not in code_to_file:
                continue  # Skip unknown codes
            else:
                icon_path = os.path.join(str(icon_path), code_to_file[code])
                icon_file = Gio.File.new_for_path(icon_path)
                icon_image = Gimp.file_load(icon_file, icon_file, Gimp.RunMode.NONINTERACTIVE)
                icon_layer = icon_image.get_active_layer()
                Gimp.edit_copy(icon_layer)

            # Copy and insert into main image
            floating_sel = Gimp.edit_paste(info_layer, False)
            floating_sel.set_offsets(x_pos, y_pos)
            Gimp.floating_sel_anchor(floating_sel)

def build_info_layer(base_image, info_layer_filename, run_mode ):

    # Add info layer
    info_file = Gio.File.new_for_path(info_layer_filename)
    info_image = Gimp.file_load(info_file, info_file, run_mode)
    info_layer = info_image.get_active_layer()
    base_image.insert_layer(info_layer.copy(), None, -1)
    return info_layer

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

Gimp.main(CardFrontLayerBuilder.__gtype__, sys.argv)