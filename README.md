# grabcraft-to-schema
A Python library and its cli for converting grabcraft to schema (more specifically litematica schematic) files

To use the CLI run `cli.py` (The CLI can be used as an example for how to build your own application using this) <br/>
The library itself is `grabcraft_to_schema.py` <br/>

Certain blocks can't be easily converted with `auto_block_map()` which is why I used `raw-blockmap.csv` which is the file from https://github.com/gbl/GrabcraftLitematic/blob/master/blockmap.csv, but renamed, and which you can now convert into a form that can be usable by the library but running `clean_blockmap.py` which I got `blockmap.csv` from.

## RenderObjects?
GrabCraft, instead of using things like .schematic or .litematic uses its own custom format called RenderObjects. If you're for instance, scraping the web and don't know what data you need to keep or generally want to be able to do stuff without having to worry about certain stuff breaking when dealing with GrabCraft's custom format, I recommend that you guys try to save `RenderObject`'s and their data. The `RenderObject.obj` field is what contains most of the data, which can easily be converted to a json as seen in the library itself since it's just a variable being set to a javascript dictionary which means that it's a json as soon as the javascript variable setting part is removed.

## Some Current Limitations:
Due to me not having the time to sort through all the weird naming used by grabcraft and due to the weird formatting schemes for both grabcraft and Minecraft the nbt (block rotation, whether or not things are lit, etc.) data isn't currently preserved and of course there's no guarantee that all grabcraft builds will work. 99% will work, however it's possible that some weird formatting on grabcraft's part will cause certain builds to not work.

## Documentation:
- `block_map`: The loaded custom blockmap overloads from `blockmap.csv`
- `load_block_map(file_name)`: The function that's used for loading the blockmap csv
- `auto_block_map(grabcraft_block) -> schema_block`: The function that's used for automatically mapping blocks over when they aren't in the `block_map`
- `RenderObject`: A class for storing all relevant `RenderObject` data
- `render_object_to_schema(render_object) -> litematic`: This converts a `RenderObject` to a litematic schema
- `url_to_render_object_data(url) -> RenderObject`: This converts a url to a grabcraft build to a `RenderObject`
- `url_to_schema(url) -> litematic`: This converts a url to a litematic schema
