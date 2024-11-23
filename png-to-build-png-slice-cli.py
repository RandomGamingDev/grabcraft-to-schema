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
png_slice = Image.open(png_slice_loc)
pixels = png_slice.load()

print("Processing...")
for i in range(png_slice.size[0]): # for every pixel:
	for j in range(png_slice.size[1]):
		pixels[i, j] = tuple(int(n) for n in bam.get_block_avg_color(bam.get_closest_colored_block(pixels[i, j])[0]))
print("Done processing!")

png_slice.save(f"{ input('Enter what you want to name the build png slice: ') }.png")