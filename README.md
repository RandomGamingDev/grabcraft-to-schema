# grabcraft-to-schema
A Python library and its cli for converting grabcraft to schema (more specifically litematica schematic) files

To use the CLI run `cli.py` (The CLI can be used as an example for how to build your own application using this) <br/>
The library itself is `grabcraft_to_schema.py` <br/>

Certain blocks can't be easily converted with `auto_block_map()` which is why I used `raw-blockmap.csv` which is the file from https://github.com/gbl/GrabcraftLitematic/blob/master/blockmap.csv, but renamed, and which you can now convert into a form that can be usable by the library but running `clean_blockmap.py` which I got `blockmap.csv` from.

## Documentation:
- `block_map`: The loaded custom blockmap overloads from `blockmap.csv`
- `load_block_map(file_name)`: The function that's used for loading the blockmap csv
- `auto_block_map(grabcraft_block) -> schema_block`: The function that's used for automatically mapping blocks over when they aren't in the `block_map`
- `RenderObject`: A class for storing all relevant `RenderObject` data
- `render_object_to_schema(render_object) -> litematic`: This converts a `RenderObject` to a litematic schema
- `url_to_render_object_data(url) -> RenderObject`: This converts a url to a grabcraft build to a `RenderObject`
- `url_to_schema(url) -> litematic`: This converts a url to a litematic schema
