'''
Author: Aaron J. Olson
https://aaronjolson.io

Implementation of a random walk algorithm to generate levels in Blender.
The process is via extrusion to preserve the mesh’s interior faces.
The interior walls property needs to be viewed with Xray view.

Example of 3D model output
https://sketchfab.com/models/97ef663c8f6040b8aecdaca2aa87989e
'''

import random
import bpy
import bmesh

ITERATIONS = 1000

# Controls the distances that are moved
# MUST BE AT LEAST 2
X_MOVE_DISTANCE = 2.0
Y_MOVE_DISTANCE = 2.0

# Position in space
y_pos = 0
x_pos = 0


def generate_maze():
    for i in range(ITERATIONS):
        direction = get_random_direction()
        next_move(direction)
    cleanup_mesh()
    cavify()


def get_random_direction():
    direction = {0: 'up', 1: 'right', 2: 'down', 3: 'left'}
    random_num = random.randint(0, 3)
    return direction[random_num]


def next_move(direction):
    global y_pos
    global x_pos

    if direction == 'up':
        y_pos += Y_MOVE_DISTANCE
        place_cube()

    if direction == 'right':
        x_pos += X_MOVE_DISTANCE
        place_cube()

    if direction == 'down':
        y_pos -= Y_MOVE_DISTANCE
        place_cube()

    if direction == 'left':
        x_pos -= X_MOVE_DISTANCE
        place_cube()


def place_cube():
    bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, location=(x_pos, y_pos, 0))


# combines the cubes into one object and removes interior faces
def cleanup_mesh():
    # select all of the cubes
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    # join all of the separate cube objects into one
    bpy.ops.object.join()
    # jump into edit mode
    bpy.ops.object.editmode_toggle()
    # get save the mesh data into a variable
    mesh = bmesh.from_edit_mesh(bpy.context.object.data)
    bpy.ops.mesh.select_all(action='SELECT')
    # remove overlapping verts
    bpy.ops.mesh.remove_doubles()
    # de-select everything in edit mode
    bpy.ops.mesh.select_all(action='DESELECT')
    # select the "interior faces"
    bpy.ops.mesh.select_interior_faces()
    # loop through and de-select all of the "floor" and "ceiling" faces by checking normals
    for f in mesh.faces:
        if f.normal[2] == 1.0 or f.normal[2] == -1.0:
            f.select = False
    # delete all still selected faces, leaving a hollow mesh behind
    bpy.ops.mesh.delete(type='FACE')


def cavify():
    win = bpy.context.window
    scr = win.screen
    areas3d = [area for area in scr.areas if area.type == 'VIEW_3D']
    region = [region for region in areas3d[0].regions if region.type == 'WINDOW']

    override = {'window': win,
                'screen': scr,
                'area': areas3d[0],
                'region': region[0],
                'scene': bpy.context.scene,
                }

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.loopcut_slide(
        override,
        MESH_OT_loopcut={
            "number_cuts": 1,
            "smoothness": 0,
            "falloff": 'INVERSE_SQUARE',
            "edge_index": 1,
            "mesh_select_mode_init": (False, False, True)
        },
        TRANSFORM_OT_edge_slide={
            "value": 0.637373,
            "single_side": False,
            "use_even": False,
            "flipped": False,
            "use_clamp": True,
            "mirror": False,
            "snap": False,
            "snap_target": 'CLOSEST',
            "snap_point": (0, 0, 0),
            "snap_align": False,
            "snap_normal": (0, 0, 0),
            "correct_uv": False,
            "release_confirm": False,
            "use_accurate": False
        }
    )

    # space and search for flip normals
    bpy.ops.mesh.select_all(action='TOGGLE')
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.modifier_add(type='SUBSURF')
    bpy.context.object.modifiers["Subdivision"].levels = 4

    # add the displacement modifiers
    bpy.ops.object.modifier_add(type='DISPLACE')
    bpy.ops.texture.new()
    bpy.data.textures["Texture"].type = 'STUCCI'
    bpy.data.textures["Texture"].noise_scale = 0.75
    bpy.context.object.modifiers["Displace"].direction = 'X'
    bpy.data.textures["Texture"].turbulence = 10
    bpy.context.object.modifiers["Displace"].texture = bpy.data.textures["Texture"]

    bpy.ops.object.modifier_add(type='DISPLACE')
    bpy.ops.texture.new()
    bpy.data.textures["Texture.001"].type = 'STUCCI'
    bpy.data.textures["Texture.001"].noise_scale = 0.75
    bpy.context.object.modifiers["Displace.001"].direction = 'Y'
    bpy.context.object.modifiers["Displace.001"].texture = bpy.data.textures["Texture.001"]

    bpy.ops.object.modifier_add(type='DISPLACE')
    bpy.ops.texture.new()
    bpy.data.textures["Texture.002"].type = 'CLOUDS'
    bpy.data.textures["Texture.002"].noise_scale = 0.65
    bpy.context.object.modifiers["Displace.002"].strength = 0.20
    bpy.context.object.modifiers["Displace.002"].texture = bpy.data.textures["Texture.002"]

    bpy.context.object.modifiers["Displace"].strength = 0.7
    bpy.context.object.modifiers["Displace.001"].strength = 0.6

    bpy.ops.object.mode_set(mode='OBJECT')


if __name__ == "__main__":
    generate_maze()
