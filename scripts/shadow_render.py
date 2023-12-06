import bpy
import os
import numpy as np
import argparse

'''
This blender scrip automatically renders the shadow of the object in the scene.
'''

def set_environment_map(hdri_image_path):
    # Load the HDRI image file
    hdri_image = bpy.data.images.load(hdri_image_path)

    # Get the current world and its node tree
    world = bpy.context.scene.world
    node_tree = world.node_tree

    # Clear existing nodes
    for node in node_tree.nodes:
        node_tree.nodes.remove(node)

    # Create new nodes: Environment Texture, Background, and World Output
    env_texture_node = node_tree.nodes.new('ShaderNodeTexEnvironment')
    env_texture_node.image = hdri_image  # Assign the loaded HDRI image to the node
    background_node = node_tree.nodes.new('ShaderNodeBackground')
    output_node = node_tree.nodes.new('ShaderNodeOutputWorld')

    # Link the nodes together
    node_tree.links.new(background_node.inputs['Color'], env_texture_node.outputs['Color'])
    node_tree.links.new(output_node.inputs['Surface'], background_node.outputs['Background'])

    # Set the environment texture to influence different ray types, if desired
    world.cycles_visibility.glossy = True
    world.cycles_visibility.transmission = True
    world.cycles_visibility.scatter = True

def set_render_basic():
    bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "CUDA"
    bpy.context.scene.cycles.device = "GPU"

    render = bpy.context.scene.render
    render.film_transparent = True
    render.engine = 'CYCLES' 

if __name__ == "__main__":
    blender_file_path = '/projects/bbjv/leoxie/Project/CS445/FieldFusion/data/blender/indoor_02.blend'
    env_map_path = '/projects/bbjv/leoxie/Project/CS445/FieldFusion/render/background/indoor_002/eq/00000.jpg'

    bpy.ops.wm.open_mainfile(filepath=blender_file_path)
    
    start_frame = 72
    end_frame = bpy.context.scene.frame_end
    bpy.context.scene.frame_start = start_frame
    set_render_basic()
    set_environment_map(env_map_path) 

    for frame in range(start_frame, end_frame + 1):
        bpy.context.scene.frame_set(frame)
        bpy.context.scene.render.filepath = f'./render/shadow/seq_03/{frame:04d}'
        bpy.ops.render.render(write_still=True)
