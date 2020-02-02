'''
Author: Aaron J. Olson
https://aaronjolson.io

Implementation of a simple cellular automata / game of life algorithm to generate cave like levels in Blender.

Example of 3D model output
https://sketchfab.com/3d-models/low-poly-procedural-cave-maze-environment-2b0ad5a175b5419ea560fa595e53e9f4
'''

import math
from random import random

import bpy
import bmesh

CHANCE_TO_START_ALIVE = 0.38 # lower the number, tbe smaller the "gaps"3r
DEATH_LIMIT = 3
BIRTH_LIMIT = 4
NUMBER_OF_ITERATIONS = 6  # number of times the game of life algorithm is run, consolidates mesh
WIDTH = 40  # overall size of the maze to be generated, the higher, the bigger, but increases run time
HEIGHT = WIDTH


def initialize_map():
    initial_map = [[alive_calc() for i in range(WIDTH)] for j in range(HEIGHT)]
    return initial_map


def alive_calc():
    if random() < CHANCE_TO_START_ALIVE:
        return True
    else:
        return False


def perform_game_of_life_iteration(old_map):
    new_map = [[False for i in range(WIDTH)] for j in range(HEIGHT)]
    # Loop over each row and column of the level_map
    for x in range(len(old_map)):
        for y in range(len(old_map[0])):
            live_neighbor_count = count_alive_neighbors(old_map, x, y)

            if old_map[x][y] is True:
                # See if it should die and become open
                if live_neighbor_count < DEATH_LIMIT:
                    new_map[x][y] = False
                # Otherwise keep it as a wall
                else:
                    new_map[x][y] = True
            # If the tile is currently empty
            else:
                # See if it should become a wall
                if live_neighbor_count > BIRTH_LIMIT:
                    new_map[x][y] = True
                else:
                    new_map[x][y] = False
    return new_map


# Returns the number of cells in a ring around (x,y) that are alive.
def count_alive_neighbors(live_map, x, y):
    count = 0
    i = -1
    while i < 2:
        j = -1
        while j < 2:
            neighbor_x = x + i
            neighbor_y = y + j
            # If we're looking at the middle point
            if i == 0 and j == 0:
                pass
                # Do nothing, we don't want to add ourselves in!
            # In case the index we're looking at it off the edge of the live_map
            elif neighbor_x < 0 or neighbor_y < 0 or neighbor_x >= len(live_map) or neighbor_y >= len(live_map[0]):
                count += 1
            # Otherwise, a normal check of the neighbour
            elif live_map[neighbor_x][neighbor_y] is True:
                count += 1
            j += 1
        i += 1
    return count


# adds cubes to the map based on the level_map matrix
def add_cubes(cell_map):
    matrix_size = WIDTH
    for i in range(matrix_size**2):
        y = math.floor(i / matrix_size)
        x = i - y * matrix_size
        if y > 1 and x == 0:
            cleanup_mesh()
        if cell_map[y][x] is False:  # cells with value True get cubes placed on them
            bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, location=(x*2, y*2, 0))


# # joins all separate objects into a single object,
# # deletes inner faces to make the object hollow
# joins all separate objects into a single object,
# deletes inner faces to make the object hollow
def cleanup_mesh():
    # get all the cubes selected
    bpy.ops.object.select_all(action='TOGGLE')
    bpy.ops.object.select_all(action='TOGGLE')
    # join all of the separate cube objects into one
    bpy.ops.object.join()
    # jump into edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    # get save the mesh data into a variable
    mesh = bmesh.from_edit_mesh(bpy.context.object.data)
    # select the entire mesh
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
    # get back out of edit mode
    bpy.ops.object.mode_set(mode='OBJECT')


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


# delete everything in the scene
def clear_scene():
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)


def generate_map():
    # Create a new level_map
    # Set up the level_map with random values
    cellmap = initialize_map()
    # run the simulation for a set number of steps
    for i in range(NUMBER_OF_ITERATIONS):
        cellmap = perform_game_of_life_iteration(cellmap)
    return cellmap


if __name__ == '__main__':
    clear_scene()
    level_map = generate_map()
    add_cubes(level_map)
    cleanup_mesh()
    cavify()
