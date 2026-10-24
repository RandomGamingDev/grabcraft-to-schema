
def render_object_to_png_slice(render_object):
        width, height, length = render_object.dims
        # Create an image of the proper size (each slice is x & z which each slice having a different y)
        # The slices are stored on one image and are stored horizontally from one another
        image = Image.new(mode="RGBA", size=(width * height, length))
        pixel_map = image.load()

        # Get the part of the javascript containing the JSON
        ro_text = render_object.obj[render_object.obj.find('{'):]
        # Convert it to a json
        ro_json = json.loads(ro_text)

        for x, yz in ro_json.items():
            for y, z in yz.items():
                for _, data in z.items():
                    block_loc = (int(data['x']) - 1, int(data['y']) - 1, int(data['z']) - 1)
                    grabcraft_block = data["name"]
                    block = grabcraft_block_to_block(grabcraft_block)
                    block = block[block.find(':') + 1:]
                    block_color = bam.get_block_avg_color(block)

                    if isinstance(block_color, np.ndarray) and block_loc[0] < width and block_loc[1] < height and block_loc[2] < length:
                        block_color = tuple(block_color.astype(dtype=np.int64))
                        pixel_map[block_loc[1] * width + block_loc[0], block_loc[2]] = block_color

        return image

# A SIGNIFICANT AMOUNT OF DATA IS LOST AND SOME BLOCKS MIGHT BE SUBSTITUED FOR OTHER BLOCKS WITH THE SAME COLOR
def png_slice_to_schema(png_slice, dims):
    reg = Region(0, 0, 0, dims[0], dims[1], dims[2])
    schem = reg.as_schematic(name="idk", author="rgd", description="test")
    width, height = png_slice.size
    for x in range(width):
        for y in range(height):
            block_loc = (x % dims[0], x // dims[0], y)
            block = BlockState(f"minecraft:{ bam.get_closest_colored_block(png_slice.getpixel((x, y)))[0] }")

            reg.setblock(block_loc[0], block_loc[1], block_loc[2], block)
    return schem

# Convert the url to a png slice
def url_to_png_slice(url):
    # Get the render object, its dimensions, the tags, the name, and the data itself from the url
    render_object = url_to_render_object_data(url)

    return render_object_to_png_slice(render_object) # Generate the png slice with the data we gathered

