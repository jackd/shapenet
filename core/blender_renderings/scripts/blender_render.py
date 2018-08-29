"""
A simple script that uses blender to render views of a single object by
rotation the camera around it.

Also produces depth map at the same time.

Example:
blender --background --python mytest.py -- --views 10 /path/to/my.obj

Original source:
https://github.com/panmari/stanford-shapenet-renderer
"""


def main(
        depth_scale, obj, scale, remove_doubles, edge_split, output_folder,
        views, shape):
    import os
    from math import radians
    import bpy

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

    bpy.ops.import_scene.obj(filepath=obj)

    if scale != 1:
        bpy.ops.transform.resize(value=(scale, scale, scale))

    for object in bpy.context.scene.objects:
        if object.name in ['Camera', 'Lamp']:
            continue
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

    def parent_obj_to_camera(b_camera):
        origin = (0, 0, 0)
        b_empty = bpy.data.objects.new("Empty", None)
        b_empty.location = origin
        b_camera.parent = b_empty  # setup parenting

        scn = bpy.context.scene
        scn.objects.link(b_empty)
        scn.objects.active = b_empty
        return b_empty

    scene = bpy.context.scene
    scene.render.resolution_x = shape[1]
    scene.render.resolution_y = shape[0]
    scene.render.resolution_percentage = 100
    scene.render.alpha_mode = 'TRANSPARENT'
    cam = scene.objects['Camera']
    cam.location = (0, 1, 0.6)
    cam_constraint = cam.constraints.new(type='TRACK_TO')
    cam_constraint.track_axis = 'TRACK_NEGATIVE_Z'
    cam_constraint.up_axis = 'UP_Y'
    b_empty = parent_obj_to_camera(cam)
    cam_constraint.target = b_empty

    model_identifier = os.path.split(os.path.split(obj)[0])[1]
    fp = os.path.join(output_folder, model_identifier, model_identifier)
    scene.render.image_settings.file_format = 'PNG'  # set output format to png

    stepsize = 360.0 / views
    # rotation_mode = 'XYZ'

    for output_node in [depthFileOutput, normalFileOutput, albedoFileOutput]:
        output_node.base_path = ''

    for i in range(0, views):
        print("Rotation {}, {}".format((stepsize * i), radians(stepsize * i)))

        scene.render.filepath = fp + '_r_{0:03d}'.format(int(i * stepsize))
        depthFileOutput.file_slots[0].path = \
            scene.render.filepath + "_depth.png"
        normalFileOutput.file_slots[0].path = \
            scene.render.filepath + "_normal.png"
        albedoFileOutput.file_slots[0].path = \
            scene.render.filepath + "_albedo.png"

        bpy.ops.render.render(write_still=True)  # render still

        b_empty.rotation_euler[2] += radians(stepsize)


def get_args():
    import argparse
    import sys
    parser = argparse.ArgumentParser(
        description='Renders given obj file by rotation a camera around it.')
    parser.add_argument('--views', type=int, default=30,
                        help='number of views to be rendered')
    parser.add_argument('obj', type=str,
                        help='Path to the obj file to be rendered.')
    parser.add_argument('--output_folder', type=str, default='/tmp',
                        help='The path the output will be dumped to.')
    parser.add_argument('--scale', type=float, default=1,
                        help='Scaling factor applied to model. '
                             'Depends on size of mesh.')
    parser.add_argument('--remove_doubles', action='store_true',
                        help='Remove double vertices to improve mesh quality.')
    parser.add_argument('--edge_split', action='store_true',
                        help='Adds edge split filter.')
    parser.add_argument('--depth_scale', type=float, default=1.4,
                        help='Scaling that is applied to depth. '
                             'Depends on size of mesh. '
                             'Try out various values until you get a good '
                             'result.')
    parser.add_argument('--shape', type=int, default=[192, 256], nargs=2,
                        help='2D shape of rendered images.')

    argv = sys.argv[sys.argv.index("--") + 1:]
    args = parser.parse_args(argv)
    return args


args = get_args()
main(
    args.depth_scale, args.obj, args.scale, args.remove_doubles,
    args.edge_split, args.output_folder, args.views, args.shape)
