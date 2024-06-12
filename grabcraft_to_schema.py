import requests
import shutil
import os
from litemapy import Schematic, Region, BlockState
import json
import csv
import PIL
from PIL import Image
import blockmodel_avg_mapper as bam
import numpy as np

block_map = {}

# Load the block map of predefined blocks
def load_block_map(file_name):
    global block_map

    with open(file_name, 'r') as f:
        reader = csv.reader(f)
        i = 0
        for row in reader:
            i += 1
            if i == 0:
                continue
            block_map[row[1]] = row[2:]

# Automatically map grabcraft blocks to schema blocks
def auto_block_map(grabcraft_block):
    # Set the schema_block to grabcraft_block so that it's ready for later transformations
    schema_block = grabcraft_block
    # Remove the parenthesis
    parenthesis_loc = schema_block.find(" (")
    if parenthesis_loc != -1:
        schema_block = schema_block[:parenthesis_loc]
    # Make all of the characters lowercase like in vanilla Minecraft block codes
    schema_block = schema_block.lower()
    # Removed all prepended spaces
    schema_block = schema_block.strip()
    # Replace all spaces with _ like in vanilla Minecraft block codes
    schema_block = schema_block.replace(' ', '_')
    # Replace some weird formatting regarding wood items
    schema_block = schema_block.replace("_wood_", '_')
    # Replace some weird formatting regarding wall mounted items
    schema_block = schema_block.replace("wall-mounted_", '')

    return f"minecraft:{ schema_block }"

def grabcraft_block_to_block(grabcraft_block):
    global block_map

    return block_map[grabcraft_block][0] if grabcraft_block in block_map else auto_block_map(grabcraft_block)

class RenderObject:
    def __init__(self, obj, name, dims, tags):
        self.obj = obj 
        self.name = name
        self.dims = dims
        self.tags = tags

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

def render_object_to_schema(render_object):
    # Get the part of the javascript containing the JSON
    ro_text = render_object.obj[render_object.obj.find('{'):]
    # Convert it to a json
    ro_json = json.loads(ro_text)

    # Store the dimensions
    dims = render_object.dims
    # Create the schema
    reg = Region(0, 0, 0, dims[0], dims[1], dims[2])
    schem = reg.as_schematic(name="idk", author="rgd", description="test")
    # Move the blocks from the render object to the region
    for x, yz in ro_json.items():
        for y, z in yz.items():
            for _, data in z.items():
                block_loc = (int(data['x']) - 1, int(data['y']) - 1, int(data['z']) - 1)
                grabcraft_block = data["name"]
                schema_block = grabcraft_block_to_block(grabcraft_block)
                block = BlockState(schema_block)  # get the attributes
                reg.setblock(block_loc[0], block_loc[1], block_loc[2], block)
    return schem

# Get the url to the render object from the webpage for the build
def url_to_render_object_data(url):
    # Getting the webpage itself
    res = requests.get(url[:url.find('#')] + "#general").text

    # The index for the renderObject's info
    render_object_i = res.find("myRenderObject")
    # The end index for getting the renderObject's string
    render_object_e = res.find('"', render_object_i)
    # Store the url to the render object
    render_object_url = "https://www.grabcraft.com/js/RenderObject/" + res[render_object_i:render_object_e]

    # Get the index for the name
    name_i = res.find("content-title")
    name_i = res.find(">", name_i) + 1
    # Get the end index for the name
    name_e = res.find("<", name_i)
    # Get the name
    name = res[name_i:name_e]

    # Get the index for the table containing the dimensions and tags
    table_i = res.find("object_properties")
    # Get the metadata
    rows = ("Width", "Height", "Depth", "Tags")
    meta = []
    for row in rows:
        # Get the row
        row_i = res.find(row, table_i)
        # Get the index for the value
        value_i = res.find('>', res.find("value", row_i)) + 1
        # Get the end index for the value
        value_e = res.find('<', value_i)
        # Get the value
        val = res[value_i:value_e]
        # If the value is a list split it to represent it as such
        if val.isdigit():
            val = int(val)
        elif val.find(", ") != -1:
            val = val.split(", ")
        # Add the values to the values list
        meta.append(val)
    tags = tuple(meta.pop())
    dims = tuple(meta)

    return RenderObject(requests.get(render_object_url).text, name, dims, tags)

# Convert the url to a png slice
def url_to_png_slice(url):
    # Get the render object, its dimensions, the tags, the name, and the data itself from the url
    render_object = url_to_render_object_data(url)

    return render_object_to_png_slice(render_object) # Generate the png slice with the data we gathered

# Convert the url to a schema file
def url_to_schema(url):
    # Get the render object, its dimensions, the tags, the name, and the data itself from the url
    render_object = url_to_render_object_data(url)

    return render_object_to_schema(render_object) # Generate the litematica schematica with the data we gathered

#load_block_map("blockmap.csv")
#schem = url_to_schema("https://www.grabcraft.com/minecraft/gothic-medieval-church/churches#model3d")
# Save the schema
#schem.save("test.litematic")
