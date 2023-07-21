##################################################
#
# This example shows how to read and write modelspec headers in python without any dependencies (torch/safetensors)
# (Except 'pillow' for image loading, but even that is optional and can be removed)
#
##################################################

# Imports
import os, sys, base64, struct, json, hashlib
from io import BytesIO
from PIL import Image

# Metadata Example
metadata = {
    # === Must ===
    "modelspec.sai_model_spec": "1.0.0", # Required version ID for the spec
    "modelspec.architecture": "stable-diffusion-xl-v1-base", # Architecture, reference the ID of the original model of the arch to match the ID
    "modelspec.title": "Example Model Version 1.0", # Clean, human-readable title. May use your own phrasing/language/etc
    # === Should ===
    "modelspec.author": "Example Corp", # Your name or company name
    "modelspec.description": "This is my example model to show you how to do it!", # Describe the model in your own words/language/etc. Focus on what users need to know
    "modelspec.date": "2023-07-20", # ISO-8601 compliant date of when the model was created
    # === Can ===
    "modelspec.license": "ExampleLicense-1.0", # eg CreativeML Open RAIL, etc.
    "modelspec.usage_hint": "Use keyword 'example'" # In your own language, very short hints about how the user should use the model
}

# set to "" to disable
image_path = "../images/example.jpg"

# Inputs
if len(sys.argv) < 3:
    print("Usage: python example_no_reqs.py <in_file> <out_file>")
    sys.exit(1)

file_name_in = sys.argv[1]
file_name_out = sys.argv[2]

# Actual processing
def process():
    if image_path != "":
        print("Loading image...")
        img = Image.open(image_path)
        image_ext = os.path.splitext(image_path)[1]
            # ===== Update the thumbnail for modelspec from an image =====
        metadata["modelspec.thumbnail"] = f"data:image/{image_ext};base64,{convert_to_b64(img)}"

    print("Loading model...")
    header = None
    content = None
        # ===== Safetensors files are very easy to load by hand =====
    with open(file_name_in, mode='rb') as file_data:
        file_hash = hashlib.sha256()
        head_len = struct.unpack('Q', file_data.read(8)) # int64 header length prefix
        header = json.loads(file_data.read(head_len[0])) # header itself, json string
        content = file_data.read() # All other content is tightly packed tensors. Copy to RAM for simplicity, but you can avoid this read with a more careful FS-dependent impl.
        file_hash.update(content)
        # ===== Update the hash for modelspec =====
        metadata["modelspec.hash_sha256"] = f"0x{file_hash.hexdigest()}"

    # ===== Simple reading of existing ModelSpec metadata. You can read this without reading the actual file content. =====
    if "__metadata__" not in header:
        print("File does not have metadata")
        orig_metadata = {}
    else:
        orig_metadata = header["__metadata__"]
        
        # ===== Check hash =====
        if "modelspec.hash_sha256" in orig_metadata:
            hash = orig_metadata["modelspec.hash_sha256"]
            actual_hash = metadata["modelspec.hash_sha256"]
            matches = hash == actual_hash
            result = "MATCH" if matches else f"FAIL, DID NOT MATCH {hash} != {actual_hash}"
            print(f"Comparing original hash to computed hash: {result}")

        print("File has metadata! Content:")
        for key,val in list(orig_metadata.items()):
            if key.startswith("modelspec."):
                print(f'    "{key}": "{val[:200] + "..." if len(val) > 200 else val}"')
                # ===== Delete prior modelspec data for replacement. Alternately just wipe metadata head entirely. =====
                del orig_metadata[key]
    
    # ===== Apply our new metadata =====
    orig_metadata.update(metadata)
    header["__metadata__"] = orig_metadata

    print("Loaded! Saving...")
    with open(file_name_out, mode='wb') as file_data:
        # ===== Write the header =====
        header = json.dumps(header)
        file_data.write(struct.pack('Q', len(header)))
        file_data.write(header.encode('utf-8'))
        # ===== Write the content =====
        file_data.write(content)

# Util Functions
def convert_to_b64(image: Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_b64

# Go
process()
