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
