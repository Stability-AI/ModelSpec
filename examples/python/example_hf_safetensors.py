##################################################
#
# This example shows how to read and write modelspec headers in python when using the HuggingFace Safetensors lib
#
##################################################

# imports
import os, sys, base64
from safetensors import safe_open
from safetensors.torch import save_file
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
    print("Usage: python example_hf_safetensors.py <in_file> <out_file>")
    sys.exit(1)

file_name_in = sys.argv[1]
file_name_out = sys.argv[2]

if file_name_in == file_name_out:
    print("Input and output files must be different, HF safetensors retains a lock on the original file")
    sys.exit(1)

# Actual processing
def process():
    if image_path != "":
        print("Loading image...")
        img = Image.open(image_path)
        image_ext = os.path.splitext(image_path)[1]
            # ===== Update the thumbnail for modelspec from an image =====
        metadata["modelspec.thumbnail"] = f"data:image/{image_ext};base64,{convert_to_b64(img)}"

    tensors = {}
    orig_metadata = None
    print("Loading...")
        # ===== Load the safetensors data via torch and HF code, and copy the metadata =====
    with safe_open(file_name_in, framework="pt", device="cpu") as f:
        orig_metadata = f.metadata()
        for key in f.keys():
            tensors[key] = f.get_tensor(key)
    # TODO: Hash the tensor data, same as in 'example_no_reqs.py'.

    # ===== Simple reading of existing ModelSpec metadata. You can read this without reading the actual file tensors. =====
    print("Reading existing keys...")
    for key,val in list(orig_metadata.items()):
        if key.startswith("modelspec."):
            print(f'    "{key}": "{val[:200] + "..." if len(val) > 200 else val}"')
            # ===== Delete prior modelspec data for replacement. Alternately just wipe metadata head entirely. =====
            del orig_metadata[key]

    # ===== Apply our new metadata =====
    orig_metadata.update(metadata)

    print("Saving...")
    # ===== The actual save operation here entirely comes down to just specifying 'metadata=' in the standard save_file function =====
    save_file(tensors, file_name_out, metadata=orig_metadata)

# Util Functions
def convert_to_b64(image: Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_b64

# Go
process()
