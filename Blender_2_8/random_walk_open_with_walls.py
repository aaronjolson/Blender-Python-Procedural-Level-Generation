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

ITERATIONS = 1000

# Controls the distances that are moved
# MUST BE AT LEAST 2
X_MOVE_DISTANCE = 2.0
Y_MOVE_DISTANCE = 2.0

# Position in space
y_pos = 0
x_pos = 0

visited = []  # walkable tile
walls = []


def generate_maze():
    for i in range(ITERATIONS):
        direction = get_random_direction()
        next_move(direction)
    build_walls()
    cleanup_mesh()


def get_random_direction():
    direction = {0: 'up', 1: 'right', 2: 'down', 3: 'left'}
    random_num = random.randint(0, 3)
    return direction[random_num]


def next_move(direction):
    global y_pos
    global x_pos

    if direction == 'up':
        y_pos += Y_MOVE_DISTANCE

    if direction == 'right':
        x_pos += X_MOVE_DISTANCE

    if direction == 'down':
        y_pos -= Y_MOVE_DISTANCE

    if direction == 'left':
        x_pos -= X_MOVE_DISTANCE
    place_tile(x_pos, y_pos)
    visited.append((x_pos, y_pos))


def place_cube(x, y):
    bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, location=(x, y, 0))


def place_tile(x, y):
    bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, location=(x, y, -1))


def check_neighbors_and_place_wall(pos):
    offset_map = [(pos[0] - 2.0, pos[1]),
                  (pos[0] + 2.0, pos[1]),
                  (pos[0], pos[1] - 2.0),
                  (pos[0], pos[1] + 2.0)]
    for offset_tuple in offset_map:
        if offset_tuple not in visited and offset_map not in walls:
            place_cube(offset_tuple[0], offset_tuple[1])
            walls.append((offset_tuple[0], offset_tuple[1]))


def build_walls():
    for position in visited:
        check_neighbors_and_place_wall(position)


# joins all separate objects into a single object and delete duplicate verts
def cleanup_mesh():
    # get all the cubes selected
    bpy.ops.object.select_all(action='SELECT')
    # join all of the separate cube objects into one
    bpy.ops.object.join()
    # jump into edit mode
    bpy.ops.object.editmode_toggle()
    # select all verts
    bpy.ops.mesh.select_all(action='SELECT')
    # remove overlapping verts
    bpy.ops.mesh.remove_doubles()
    # get back out of edit mode
    bpy.ops.object.editmode_toggle()


if __name__ == "__main__":
    generate_maze()
