"""
A simple script that uses blender to render views of a single object by
rotation the camera around it.

Also produces depth map at the same time.

Example:
blender --background --python blender_render.py -- \
    --manager_dir=/path/to/manager

Original source:
https://github.com/panmari/stanford-shapenet-renderer
"""
import bpy


def setup(depth_scale):
    # Set up rendering of depth map:
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    links = tree.links

    # Add passes for additionally dumping albed and normals.
    bpy.context.scene.render.layers["RenderLayer"].use_pass_normal = True
    bpy.context.scene.render.layers["RenderLayer"].use_pass_color = True

    # clear default nodes
    for n in tree.nodes:
        tree.nodes.remove(n)

    # create input render layer node
    rl = tree.nodes.new('CompositorNodeRLayers')

    map = tree.nodes.new(type="CompositorNodeMapValue")
    # Size is chosen kind of arbitrarily, try out until you're satisfied with
    # resulting depth map.
    map.offset = [-0.7]
    map.size = [depth_scale]
    map.use_min = True
    map.min = [0]
    map.use_max = True
    map.max = [255]
    try:
        links.new(rl.outputs['Z'], map.inputs[0])
    except KeyError:
        # some versions of blender don't like this?
        pass

    invert = tree.nodes.new(type="CompositorNodeInvert")
    links.new(map.outputs[0], invert.inputs[1])

    # create a file output node and set the path
    depthFileOutput = tree.nodes.new(type="CompositorNodeOutputFile")
    depthFileOutput.label = 'Depth Output'
    links.new(invert.outputs[0], depthFileOutput.inputs[0])

    scale_normal = tree.nodes.new(type="CompositorNodeMixRGB")
    scale_normal.blend_type = 'MULTIPLY'
    # scale_normal.use_alpha = True
    scale_normal.inputs[2].default_value = (0.5, 0.5, 0.5, 1)
    links.new(rl.outputs['Normal'], scale_normal.inputs[1])

    bias_normal = tree.nodes.new(type="CompositorNodeMixRGB")
    bias_normal.blend_type = 'ADD'
    # bias_normal.use_alpha = True
    bias_normal.inputs[2].default_value = (0.5, 0.5, 0.5, 0)
    links.new(scale_normal.outputs[0], bias_normal.inputs[1])

    normalFileOutput = tree.nodes.new(type="CompositorNodeOutputFile")
    normalFileOutput.label = 'Normal Output'
    links.new(bias_normal.outputs[0], normalFileOutput.inputs[0])

    albedoFileOutput = tree.nodes.new(type="CompositorNodeOutputFile")
    albedoFileOutput.label = 'Albedo Output'
    # For some reason,
    links.new(rl.outputs['Color'], albedoFileOutput.inputs[0])

    # Delete default cube
    bpy.data.objects['Cube'].select = True
    bpy.ops.object.delete()

    # Make light just directional, disable shadows.
    lamp = bpy.data.lamps['Lamp']
    lamp.type = 'SUN'
    lamp.shadow_method = 'NOSHADOW'
    # Possibly disable specular shading:
    lamp.use_specular = False

    # Add another light source so stuff facing away from light is not
    # completely dark
    bpy.ops.object.lamp_add(type='SUN')
    lamp2 = bpy.data.lamps['Sun']
    lamp2.shadow_method = 'NOSHADOW'
    lamp2.use_specular = False
    lamp2.energy = 0.015
    sun = bpy.data.objects['Sun']
    sun.rotation_euler = bpy.data.objects['Lamp'].rotation_euler
    sun.rotation_euler[0] += 180

    invariants = set(bpy.context.scene.objects)
    return invariants, depthFileOutput, normalFileOutput, albedoFileOutput


def load_obj(path, scale, remove_doubles, edge_split, invariants):
    bpy.ops.import_scene.obj(filepath=path)
    if scale != 1:
        bpy.ops.transform.resize(value=(scale, scale, scale))

    objs = [obj for obj in bpy.context.scene.objects if obj not in invariants]

    for object in objs:
        bpy.context.scene.objects.active = object
        if scale != 1:
            bpy.ops.object.transform_apply(scale=True)
        if remove_doubles:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.remove_doubles()
            bpy.ops.object.mode_set(mode='OBJECT')
        if edge_split:
            bpy.ops.object.modifier_add(type='EDGE_SPLIT')
            bpy.context.object.modifiers["EdgeSplit"].split_angle = 1.32645
            bpy.ops.object.modifier_apply(
                apply_as='DATA', modifier="EdgeSplit")

    return objs


def remove_obj(objs):
    for object in objs:
        object.select = True
        bpy.ops.object.delete()


# def parent_obj_to_camera(b_camera):
#     origin = (0, 0, 0)
#     b_empty = bpy.data.objects.new("Empty", None)
#     b_empty.location = origin
#     b_camera.parent = b_empty  # setup parenting
#
#     scn = bpy.context.scene
#     scn.objects.link(b_empty)
#     scn.objects.active = b_empty
#     return b_empty


def main(manager_dir, cat_id, example_ids):
    from shapenet.core.renderings.manager import RenderableManagerBase
    manager = RenderableManagerBase(manager_dir, [cat_id])

    keys = tuple(manager.needs_rendering_keys())
    n = len(keys)

    if n == 0:
        print('No renderable keys - skipping.')
        return
    params = manager.get_render_params()

    shape = params.get('shape', [128, 128])
    scale = params.get('scale', 1)
    remove_doubles = params.get('remove_doubles', False)
    edge_split = params.get('edge_split', False)

    invariants, depthFileOutput, normalFileOutput, albedoFileOutput = setup(
        params.get('depth_scale', 1.4))
    empty = bpy.data.objects.new("Empty", None)
    empty.location = (0, 0, 0)
    invariants.add(empty)

    scene = bpy.context.scene
    scene.render.resolution_x = shape[1]
    scene.render.resolution_y = shape[0]
    scene.render.resolution_percentage = 100
    scene.render.alpha_mode = 'TRANSPARENT'
    cam = scene.objects['Camera']
    # b_empty = parent_obj_to_camera(cam)

    # invariants.add(b_empty)
    outputs = {
        'depth': depthFileOutput,
        'normal': normalFileOutput,
        'albedo': albedoFileOutput
    }

    def set_camera(eye):
        cam.location = eye
        cam_constraint = cam.constraints.new(type='TRACK_TO')
        cam_constraint.track_axis = 'TRACK_NEGATIVE_Z'
        cam_constraint.up_axis = 'UP_Y'
        cam_constraint.target = empty

    def render(key):
        obj_path = manager.get_obj_path(key)
        eyes = manager.get_camera_positions(key)
        obj = load_obj(obj_path, scale, remove_doubles, edge_split, invariants)
        # set output format to png
        scene.render.image_settings.file_format = 'PNG'

        for output_node in [
                depthFileOutput, normalFileOutput, albedoFileOutput]:
            output_node.base_path = ''

        for i, eye in enumerate(eyes):
            set_camera(eye)
            base_path = manager.get_rendering_path(key, i)
            if base_path.endswith('.png'):
                base_path = base_path[:-4]
            scene.render.filepath = base_path
            for k, v in outputs.items():
                v.file_slots[0].path = \
                    manager.get_rendering_path(key, i, k)
            bpy.ops.render.render(write_still=True)  # render still

        remove_obj(obj)

    print('Rendering %d examples for manager at %s' % (n, manager_dir))
    for example_id in example_ids:
        render((cat_id, example_id))


def get_args():
    import argparse
    import sys
    parser = argparse.ArgumentParser(
        description='Renders given obj file by rotation a camera around it.')
    parser.add_argument('--manager_dir', type=str, help='directory of manager')
    parser.add_argument('--cat_id', type=str)
    parser.add_argument('--example_ids', type=str, nargs='+')

    argv = sys.argv[sys.argv.index("--") + 1:]
    args = parser.parse_args(argv)

    return args


args = get_args()
main(args.manager_dir, args.cat_id, args.example_ids)
