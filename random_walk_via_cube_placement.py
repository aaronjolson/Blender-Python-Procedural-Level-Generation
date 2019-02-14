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

# Position in space
y_pos = 1.0
x_pos = 1.0

# Controls the distances that are moved
# MUST BE AT LEAST 2
x_move_distance = 2.0
y_move_distance = 2.0


def generate_maze():
    for i in range(ITERATIONS):
        direction = get_random_direction()
        next_move(direction)
    cleanup_mesh()


def get_random_direction():
    direction = {0: 'up', 1: 'right', 2: 'down', 3: 'left'}
    random_num = random.randint(0, 3)
    return direction[random_num]


def next_move(direction):
    global next_face
    global y_pos
    global x_pos

    if direction == 'up':
        place_cube()
        y_pos += y_move_distance

    if direction == 'right':
        place_cube()
        x_pos += x_move_distance

    if direction == 'down':
        place_cube()
        y_pos -= y_move_distance

    if direction == 'left':
        place_cube()
        x_pos -= x_move_distance


def place_cube():
    bpy.ops.mesh.primitive_cube_add(
        radius=1, view_align=False, enter_editmode=False, location=(x_pos, y_pos, 0),
        layers=(True, False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False, False,
                False, False))


# combines the cubes into one object and removes interior faces
def cleanup_mesh():
    # select all of the cubes
    bpy.ops.object.select_all(action='SELECT')
    # join all of the separate cube objects into one
    bpy.ops.object.join()
    # jump into edit mode
    bpy.ops.object.editmode_toggle()
    # get save the mesh data into a variable
    mesh = bmesh.from_edit_mesh(bpy.context.object.data)
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


if __name__ == "__main__":
    generate_maze()
