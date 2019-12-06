Provides data on renderings done via blender.

See `scripts/blender_render.py` for blender details.

# Creating Renderings
* `scripts/render_cat.py` creates renderings for a given render configuration (shape, number of images at even rotations about `z` axis)
* `scripts/create_archive.py` zips renderings associated with the provided category, or adds specific `example_id`s to an existing archive
* `scripts/check_archive.py` checks which examples have renderings associated with them in the given archive.

Some `obj` files in the original dataset cannot be opened by blender. These models are extracted, imported into meshlab and re-exported as `obj`s, and the resulting files compressed in `_fixed_meshes/CAT_ID.zip`. These renderings can be created using `scripts/render_cat.py CAT_ID -f`

# Accessing Image Data
Data (either from compressed archives or raw files) can be accessed via `RenderConfig` methods. A `RenderConfig` specifies an image shape and the number of images rendered at linearly spaced angles.
