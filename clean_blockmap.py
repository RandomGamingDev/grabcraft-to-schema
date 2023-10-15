import math
import pandas as pd

csv_loc = input("Enter the location to the csv that you want to clean: ")

# The header to mark the different sections
header = "from,to,state1,state2,state3,state4,state5,state6\n"

# Add the header to the file
with open(csv_loc, "r+") as f:
    # Get the data
    data = f.read()
    # Make sure that you write over instead of appending to the data
    f.seek(0)
    # Write the data
    f.write(header + data)
    f.truncate()

# Get the data
blockmap = pd.read_csv(csv_loc)
# Remove the parts that don't have a from
blockmap = blockmap[~blockmap["from"].isnull()]
# Save the file
blockmap.to_csv(csv_loc)
