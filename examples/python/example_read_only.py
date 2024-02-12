##################################################
#
# This example shows how to just read modelspec headers in python without any dependencies (torch/safetensors)
#
##################################################

# Imports
import sys, struct, json

# Inputs
if len(sys.argv) < 2:
    print("Usage: python example_read_only.py <in_file>")
    sys.exit(1)

file_name_in = sys.argv[1]

# Actual processing
def process():
    print("Loading model...")
    header = None
    # ===== Safetensors files are very easy to load by hand =====
    with open(file_name_in, mode='rb') as file_data:
        head_len = struct.unpack('Q', file_data.read(8)) # int64 header length prefix
        header = json.loads(file_data.read(head_len[0])) # header itself, json string

    # ===== Simple reading of existing ModelSpec metadata. You can read this without reading the actual file content. =====
    if "__metadata__" not in header:
        print("File does not have metadata")
    else:
        orig_metadata = header["__metadata__"]
        print("File has metadata! Content:")
        for key,val in list(orig_metadata.items()):
            if key.startswith("modelspec."):
                max_len = 200 if key == "modelspec.thumbnail" or val.startswith("data:image/") else 800
                print(f'    "{key}": "{val[:max_len] + "..." if len(val) > max_len else val}"')

# Go
process()
