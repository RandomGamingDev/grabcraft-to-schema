import grabcraft_to_schema as gts
import blockmodel_avg_mapper as bam
import json
import PIL
from PIL import Image
import numpy as np

# Load the block map
gts.load_block_map("blockmap.csv")

# Get the data from the user
png_slice_loc = input("Enter the location to the png slice: ")
dims = [int(n) for n in input("Enter the dimensions: ")[1:-1].split(',')]
png_slice = Image.open(png_slice_loc)

# Result

# 19 16 19
# medieval-puritan-traders-house.png
res = gts.png_slice_to_schema(png_slice, dims)
res.save(f"{ input('Enter what you want to name the litematic: ') }.litematic")