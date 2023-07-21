# Stability.AI Model Metadata Standard Specification

The Stability.AI Model Metadata Standard, or "SAI Model Spec", is a standard specification for the format and data of metadata keys in the header of `.safetensors` AI model files.
It seeks to make the content of an AI model file quickly and easily identifiable, such that downstream users (inference engines and UIs) can understand the content of a file without the need for any tricky processing or analysis.
The data within should identify clearly (A) the type and function of a model, clearly enough that an inference engine can determine how to load it correctly, and (B) user-relevant information that a UI with model-selection capability should display to the end-user.

## Version

This is specification version 1.0 - `sai_model_spec_1.0`. **NOT YET FINAL. PENDING REVIEW.**

## Technical Placement

Modern AI models are distributed via `.safetensors` files (no longer 'pickle' files `.ckpt`/`.bin`/etc), and as such this format is specified to fit within the `.safetensors` specification in such a way as to prevent any breakage on older implementations. You can [read about the safetensors format here](https://github.com/huggingface/safetensors/tree/main/safetensors). Safetensors files have a standard JSON header on all files, with a `__metadata__` key reserved for dynamic user-specified data. It is the perfect place for helpful metadata that prior to now has been underutilized. This Model Metadata Specification defines a set of keys to put within the `__metadata__` header, all prefixed with `modelspec.`.

### JSON Example

The following is an example of what the header of a compliant file might look like:

```js
{
    "__metadata__": {
        "modelspec.version": "sai_model_spec_1.0",
        "modelspec.architecture": "stable-diffusion-xl-v1-base",
        "modelspec.title": "Example Model Version 1.0",
        "other_keys": "..."
    },
    "some.tensor.key": { ... }
}
```

## Tool Recommendations

### Trainers

Trainers should copy pre-existing keys from the source file where relevant (architecture, etc.), auto-generate keys (version, hash, data, etc.) where relevant, and make it easy for the user to specify any user-modifiable keys (title, description, etc.).

### Inferencing Tools and UIs

Tools that enable a user to use/browse/search/select models should:
- Use architecture and other technical keys to determine how to load and process the model, and warn the user if there is a failure (eg architecture is incorrectly specified)
    - Having a mapping of architecture IDs to code paths is a good option. In the case of image generation models, there is often a python codepath `.yaml` config that can be associated with the ID.
- Apply relevant keys where logical (eg `resolution` in image models should be applied as the default resolution for images made with that model)
- Display keys to user where relevant (eg `title` and `thumbnail` shown in model listings, `description` should be accessible easily, `usage_hint` should be readily visible, ...)
- Allow the user to modify metadata when appropriate (if a user is running the model at home, they may wish to edit in their own description or usage hints, or replace the thumbnail with one more meaningful to them)
- If searching is possible within the relevant tool, this metadata should be provided as searchable content

## Specification

**Quick facts:**
- All keys added per this spec must have the prefix `modelspec.` prepended to them, for example the `title` key is written within the actual data-file as `modelspec.title`.
- Keys not part of this spec may exist or not at end-users discretion, eg. to meet other standards or apply other data useful to more specific cases.
- Some keys are specific to the category of model, and are listed separately below.

This specification defines 3 categories of key: **MUST**, **SHOULD**, **CAN**
- "**MUST**" indicates that a key is required for a model to obey this format specification. If the key is not present, the model does not include this metadata. Downstream consumers (inferencers) are encouraged in such a case to assume the model predates this spec (eg Stable Diffusion v1 model). (Nothing technically prevents an inferencer from supporting a subset of keys, eg reading just the `title`, without obeying full spec beyond that if they so choose).
- "**SHOULD**" indicates that a key is considered valuable and should be used, but if it is missing, that’s okay, and a downstream consumer should fill in a default or ignore it.
- "**CAN**" indicates a key is defined by the spec but is not expected in most models.

| Name | Type | Description | Examples |
| --- | --- | --- | --- |
| `version` | **MUST** | Mandatory identifier key, indicates the presence and version of this specification. Trainer tools that support the spec should automatically emit this key, set to the version they support. | `sai_model_spec_1.0` |
| `architecture` | **MUST** | The specific classifier of the model's architecture, must be unique between models that have different inferencing requirements (*so for example SDV2-512 and SDv2-768-v are different enough that the distinction must be marked here, as the code must behave different to support it*). Simple finetunes of a model do not require a unique class, as the inference code does not have to change to support it. See architecture ID listing below this table for specific examples. | `stable-diffusion-v1`, `stable-diffusion-xl-v1-base`, `stable-diffusion-xl-v1-refiner`, `stable-diffusion-v1-lora`, `stable-diffusion-v1-textual-inversion`, `gpt-neo-x` |
| `title` | **MUST** | A title unique to the specific model. Generally for end-user training software, the user should provide this. If they do not, one can be provided as just eg the original file name or training run name. Inference UIs are encouraged to display this title to users in any model selector tools. | `Stable Diffusion XL 1.0 Base`, `My Example LoRA` |
| `description` | **SHOULD** | A user-friendly textual description of the model. This may describe what the model is trained on, what its capabilities are, or specific data like trigger words for a small SD finetunes. This field is permitted to contain very long sections of text, with paragraphs and etc. Inference UIs are encouraged to make this description visible-but-not-in-the-way to end users. Usage of markdown formatting is encouraged, and UIs are encouraged to format the markdown properly (displaying as plaintext is also acceptable where markdown is not possible). | `Stable Diffusion XL is the next generation of Stable Diffusion, a 6.5B parameter model-ensemble that generates etc. etc.` |
| `author` | **SHOULD** | The name or identity of the company or individual that created a model. Can even be a username or personal profile link. | `Stability.AI`, `MyCorp`, `John Doe`, `github.com/example` |
| `date` | **SHOULD** | The precise date that a model was created or published, in any ISO-8601-compliant format. | `2023-07-16`, `2023‐07‐16T18:13:38Z` |
| `hash_sha256` | **SHOULD** | A hash of all tensor content (ie excluding the header section), with `0x` prefix and no byte-separator symbols. Other keys with the `hash_` prefix followed by a different hash algorithm (eg `hash_md5`) are expected to obey the same format rules and implement the hash algorithm named within. Future versions of the spec may change which algorithm is encouraged as `SHOULD`. Inferencing engines are encouraged to validate that the hash matches after loading a file and warn the user if it does not match (ie possible file corruption). Model trainers/modifiers are strongly encouraged to calculate the hash and emit it correctly automatically whenever saving a model. This is not a `MUST` because hash algorithms may change with time, and the format should not be locked in to just one. | `0x123abc...` |
| `license` | **CAN** | If the model is under any form of license terms or restrictions, they should be clearly identified here. The model creator may at their own discretion (A) provide the name of the license, (B) provide a link to the license terms, or (C) emit the license terms in full in this slot. | `CC-BY-SA-4.0`, `CreativeML Open RAIL-M` |
| `usage_hint` | **CAN** | Usage hint(s) for the model, where applicable. This field should be short, and just quickly describe bits of information a user might need while operating the model. Inference UIs are encouraged to make this information readily visible to the user when it is present. For example, a small SD finetune model would use this to list trigger words. | `Trigger word: mypetcat`, `Always use <user> and <assistant> prefixes!` |
| `thumbnail` | **CAN** | A (very small!) thumbnail icon in data-image format to be provided as a preview in inference UIs. Note that safetensors headers usually occupy a few hundreds of kilobytes, and don't get officially limited until 100 megabytes, so a small jpeg in data-image format does not significantly increase the size. `256x256` is a recommended size and aspect ratio (square). | `data:image/jpg;base64,abc123…` |

### Category-Specific Keys

#### Image Generation Models

| Name | Type | Description | Examples |
| --- | --- | --- | --- |
| `resolution` | **SHOULD** | The base resolution an image generator is intended to work at, in `(width)x(height)` format. This does not need to account for aspect ratios. Future image generator models of a class that are able to handle any resolution may omit this key. Current generation Stable Diffusion models should always have this key. | `512x512`, `1024x1024` |
| `trigger_phrase` | **CAN** | For image generation adapter models (eg LoRA) especially, if a model is trained to heavily require a phrase, it should be placed here. Inference UIs are welcomed to auto-emit this phrase into the prompt if it is present (encouraged to make this behavior optional to the user where possible). | `mypetcat`, `mymodelnamehere` |
| `prediction_type` | **CAN** | In Stable Diffusion, `v` or `epsilon`. Other model classes may have their own concepts that apply. | `v`, `epsilon` |
| `timestep_range` | **CAN** | If a model is tuned on a sub-section of possible timesteps (Timestep-Expert Models), identify it here, in the format `<min>,<max>`. | `500,999`, `0,499` |
|  |  |  |  |

#### Text-Prediction Models

| Name | Type | Description | Examples |
| --- | --- | --- | --- |
| `data_format` | **MUST** | The format the data is in - needed due to the variety of specialty formats and quantization methods (often not accurately reflected in tensor data type, as eg there are different definitions of 4bit data). | `fp16`, `gptq-4bit`, `gptq-4bit-gr128`, `bnb-nf4` |
| `format_type` | **SHOULD** | What `type of format` the model is intended to work in (writing stories vs question-and-answer chat vs coding). Should constrain to the enumerated examples unless a new format type has been created that is not yet listed. | `general` (other), `writing` (stories), `chat` (Q&A), `code`, `technical` (emits special logical behavior, eg CoT) |
| `language` | **CAN** | The primary human language(s) the model is trained to understand, in standard language code format, as a comma-separated list. | `en/US`, `en/US, en/UK`, `jp/JP, en/US` |
| `format_template` | **CAN** | For formats where a specific template is trained in, it should be given here, as a string that identifies `%%SYSTEM%%`, `%%USER%%`, and `%%AI%%`. Some templates may exclude 'system' or add additional keys. Inferencing tools are encouraged to be lenient if the format does not match expectations. | `<system>%%SYSTEM%%<user>%%USER%%<assistant>%%AI%%`, `### System:\n%%SYSTEM%%\n### Human:\n%%USER%%\n### Assistant:\n%%AI%%` |

### Architecture ID Listing

The following is a list of common Architecture ID values, both to serve as a reference for implementation, and as an example for other architecture IDs to be chosen by. This is not a complete list, just several examples.

- **Stable Diffusion:** `stable-diffusion-v1`, `stable-diffusion-v2-512`, `stable-diffusion-v2-768-v`, `stable-diffusion-xl-v1-base`, `stable-diffusion-xl-v1-refiner`
- **Stable Diffusion Adapters:** `stable-diffusion-v1-lora`, `stable-diffusion-v1-textual-inversion` (change `v1` to `v2-512`, `v2-768-v`, `xl-v1-base`, `xl-v1-refiner` according to target)
- **Language Models:** `gpt-neo-x`

(Note: relevant project leads for well-known model formats are welcomed to PR additions to this list)

## Notice

This model metadata standard is published by Stability.AI freely to the public in the interest of creating a shared standard format for the benefit of the community as a whole.
