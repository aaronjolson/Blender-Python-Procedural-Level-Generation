'''
Author: Aaron J. Olson
https://aaronjolson.io

Implementation of a recursive division algorithm to generate levels in Blender.

Example of 3D model output
https://sketchfab.com/models/8587b464b2034485886cd094c7adf14c
'''

import math
import random
import bpy
import bmesh

SIZE = 49
MIN_SIZE = SIZE / 4


def generate_level(size):
    # deletes everything in the scene, allows for a simple and clean run
    clear_scene()
    # initialize the map matrix and store it in the level_map variable
    level_map = new_map(size, 0)
    # build out the map, these two functions do all of the procedural work
    add_inner_walls(level_map, 1, 1, size - 2, size - 2)
    add_outer_walls(level_map, SIZE)
    # populate the scene with cubes according to the map matrix
    add_cubes(level_map)
    # combines the cubes into one object and removes interior faces
    cleanup_mesh()


# generate 2d array with list comprehension
def new_map(size, value):
    return [[value for i in range(size)] for j in range(size)]


# returns random number between min max inclusive
def random_number(minimum, maximum):
    return math.floor(random.random() * (maximum - minimum + 1)) + minimum


def add_outer_walls(level_map, size):
    for i in range(size):
        if i == 0 or i == size - 1:
            for j in range(size):
                level_map[i][j] = 1
        else:
            level_map[i][0] = 1
            level_map[i][size - 1] = 1


def add_inner_walls(level_map, rmin, cmin, rmax, cmax):
    width = cmax - cmin
    height = rmax - rmin

    # stop recursing once room size is reached
    if width < MIN_SIZE or height < MIN_SIZE:
        return level_map

    # determine whether to build vertical or horizontal wall
    if width > height:
        is_vertical = True
    else:
        is_vertical = False

    if is_vertical:
        # randomize location of vertical wall
        col = math.floor(random_number(cmin, cmax) / 2) * 2
        build_wall(level_map, is_vertical, rmin, rmax, col)
        # recurse to the two newly divided boxes
        add_inner_walls(level_map, rmin, cmin, rmax, col - 1)
        add_inner_walls(level_map, rmin, col + 1, rmax, cmax)
    else:
        row = math.floor(random_number(rmin, rmax) / 2) * 2
        build_wall(level_map, is_vertical, cmin, cmax, row)
        add_inner_walls(level_map, rmin, cmin, row - 1, cmax)
        add_inner_walls(level_map, row + 1, cmin, rmax, cmax)


def build_wall(level_map, is_vertical, minimum, maximum, loc):
    hole = math.floor(random_number(minimum, maximum) / 2) * 2 + 1
    for i in range(minimum, maximum + 1):
        if is_vertical:
            if i == hole:
                level_map[loc][i] = 0
            else:
                level_map[loc][i] = 1
        else:
            if i == hole:
                level_map[i][loc] = 0
            else:
                level_map[i][loc] = 1


# adds cubes to the map based on the level_map matrix
def add_cubes(level_map):
    y = 0
    for row in level_map:
        x = 0
        for value in row:
            if value == 0:  # cells with value 0 get cubes placed on them
                bpy.ops.mesh.primitive_cube_add(
                    radius=1, view_align=False, enter_editmode=False, location=(x, y, 0),
                    layers=(True, False, False, False, False, False, False, False, False,
                            False, False, False, False, False, False, False, False, False,
                            False, False))
            x += 2
        y += 2


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


# delete everything in the scene
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


if __name__ == "__main__":
    generate_level(SIZE)
