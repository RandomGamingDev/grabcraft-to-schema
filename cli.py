import grabcraft_to_schema as gts

gts.load_block_map("blockmap.csv")
# A demo link that you can try to use:
# "https://www.grabcraft.com/minecraft/gothic-medieval-church/churches#model3d"
schem = gts.url_to_schema(input("Enter the link to the build: "))
# Save the schema
schem.save(f"{ input('Enter what you want to name the litematic: ') }.litematic")
