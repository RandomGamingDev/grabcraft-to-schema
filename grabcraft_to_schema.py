import csv, requests, json, re
from collections import defaultdict
from litemapy import Schematic, Region, BlockState

class BlockMap:
    def __init__(self, file="blockmap.csv"):
        self.updated = 0
        # Load the block map of known blocks
        self.block_map = {}
        self.block_list = []
        with open(file, 'r', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                key = (int(row[0]), row[1].strip())
                self.block_map[key] = row[2:]
                self.block_list.append(key)

    def __call__(self, block_id, block_name):
        key = (block_id, block_name)
        val = self.block_map.get(key)
        if val is None:
            key1 = (-1, block_name)
            val = self.block_map.pop(key1, None)
            if val is not None:
                idx = self.block_list.index(key1)
                self.block_list[idx] = key
            else:
                val = [BlockMap.guess(block_name)]
                self.block_list.append(key)

            self.block_map[key] = val
            self.updated += 1

        props = dict(zip(val[1::2], val[2::2]))
        return val[0], props

    def save(self, filename):
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            for key in self.block_list:
                val =  self.block_map[key]
                writer.writerow([key[0], key[1]] + val)

    # Automatically map grabcraft blocks to schema blocks
    @staticmethod
    def guess(grabcraft_block):
        def drop_state(b):
            parenthesis_loc = b.find(" (")
            if parenthesis_loc != -1:
                b = b[:parenthesis_loc]
            return b

        # Set the schema_block to grabcraft_block so that it's ready for later transformations
        schema_block = grabcraft_block
        # Remove the parenthesis
        schema_block = drop_state(schema_block)
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


def get_renderobject_old(page):
    # The index for the renderObject's info
    render_object_i = page.find("myRenderObject")
    # The end index for getting the renderObject's string
    render_object_e = page.find('"', render_object_i)
    # Store the url to the render object
    render_object_url = "https://www.grabcraft.com/js/RenderObject/" + page[render_object_i:render_object_e]
    # Download render object's javascript
    ro_js = requests.get(render_object_url).text
#     with open("dump_RenderObject.txt", "w", encoding="utf8") as f:
#         f.write(ro_js)
    # Get the part of the javascript containing the JSON
    ro_text = ro_js[ro_js.find('{'):]
    # Convert it to a json
    return json.loads(ro_text)


def get_renderobject(page):
    fetch_list = re.findall(r'fetch\("(.+)"\)', page)
    if not fetch_list:
        print("RenderObject's fetch URL not found")
        exit()
    render_object_url = fetch_list[0]
    # print(render_object_url)

    # Download render object's data
    res = requests.get(render_object_url)

    if not res.ok:
        print(res.status_code)
#         print(res.encoding, res.apparent_encoding)
#         print(res.headers)
        exit()

    # Convert it to a json
    return json.loads(res.text)


class RenderObject:
    def __init__(self, url, north='north', block_map=None, dump=False):
        self.block_map = block_map or BlockMap()
        self.url = url[:url.find('#')] + "#general"
        self.north = north.lower()

        # Getting the webpage itself
        page = requests.get(self.url).text
        if (dump):
            with open("dump_page.html", "w", encoding='utf-8') as f:
                f.write(page)

        # Get the index for the name
        name_i = page.find("content-title")
        name_i = page.find(">", name_i) + 1
        # Get the end index for the name
        name_e = page.find("<", name_i)
        # Get the name
        self.name = page[name_i:name_e].strip()

        # Get the author
        author_list = re.findall(r'Author:&nbsp;(.+)<br', page)
        self.author = author_list[0] if author_list else "n/a"

        # Get the index for the table containing the dimensions and tags
        table_i = page.find("object_properties")
        # Get the metadata
        rows = ("Width", "Height", "Depth", "Tags")
        meta = []
        for row in rows:
            # Get the row
            row_i = page.find(row, table_i)
            # Get the index for the value
            value_i = page.find('>', page.find("value", row_i)) + 1
            # Get the end index for the value
            value_e = page.find('<', value_i)
            # Get the value
            val = page[value_i:value_e]
            # If the value is a list split it to represent it as such
            if val.isdigit():
                val = int(val)
            elif val.find(", ") != -1:
                val = val.split(", ")
            # Add the values to the values list
            meta.append(val)
        self.tags = tuple(meta.pop())
        self.dims = tuple(meta)

#         ro_json = get_renderobject_old(page)
        ro_json = get_renderobject(page)
        if dump:
            with open("dump_RenderObject.json", "w") as f:
                json.dump(ro_json, f, sort_keys=True, indent=4)

        # Unpack json into a flat list of blocks
        def json_iter(tree):
            for x, yz in tree.items():
                for y, z in yz.items():
                    for _, data in z.items():
                        yield data
        self.blocks = [(int(d['mat_id']), d["name"].strip(), int(d['x']), int(d['y']), int(d['z'])) for d in json_iter(ro_json)]

        # verify build's dimensions
        max_x = max(d[2] for d in self.blocks)
        max_y = max(d[3] for d in self.blocks)
        max_z = max(d[4] for d in self.blocks)
        max_dims = max_x, max_y, max_z
        if self.dims != max_dims:
            print("Dimensions updated:", self.dims, "->", max_dims)
            self.dims = max_dims

    def map_xz(self, x, z):
        match self.north:
            case "north":
                return x - 1, z - 1
            case "south":
                return self.dims[0] - x, self.dims[2] - z
            case "east":
                return self.dims[2] - z, x - 1
            case "west":
                return z - 1, self.dims[0] - x
            case _:
                exit(f"invalid north: '{north}'")

    def map_dims(self):
        match self.north:
            case "north" | "south":
                return self.dims
            case "east" | "west":
                return self.dims[::-1]
            case _:
                exit(f"invalid north: '{north}'")

    def to_schema(self):
        # Store the dimensions
        dims = self.map_dims()
        # Create the schema
        reg = Region(0, 0, 0, dims[0], dims[1], dims[2])
        schem = reg.as_schematic(name=self.name, author=self.author, description=self.url)

        mat_list = defaultdict(int)

        # Fill the region with blocks
        for gc_id, gc_name, gc_x, gc_y, gc_z in self.blocks:
            schema_y = gc_y - 1
            schema_x, schema_z = self.map_xz(gc_x, gc_z)

            schema_block, schema_props = self.block_map(gc_id, gc_name)
            block = BlockState(schema_block, **schema_props)
            reg.setblock(schema_x, schema_y, schema_z, block)

            mat_list[schema_block[schema_block.find(":")+1:]] += 1

        # Fix for 2-tall blocks
        for x, y, z in reg.block_positions():
            b = reg.getblock(x, y, z)

            # propagate properties of each door's half to its other half
            if re.match("^minecraft:.+_door$", b.id):
                props = dict(b.properties())
                half = props.pop("half")
                y_pair = y + 1 if half == "lower" else y - 1
                b_pair = reg.getblock(x, y_pair, z)
                if b.id == b_pair.id:
                    reg.setblock(x, y_pair, z, b_pair.with_properties(**props))
                else:
                    print(f"Door block mismatch: {b.id} -> {b_pair.id}")

            # upper half of 2-tall plants is mostly wrong; overwrite it with lower half
            plant_id = ["minecraft:large_fern",
                        "minecraft:tall_grass",
                        "minecraft:lilac",
                        "minecraft:peony",
                        "minecraft:pitcher_plant",
                        "minecraft:rose_bush",
                        "minecraft:sunflower"]
            if b.id in plant_id:
                props = dict(b.properties())
                if props["half"] == "lower":
                    reg.setblock(x, y + 1, z, b.with_properties(half="upper"))

        return schem, mat_list

