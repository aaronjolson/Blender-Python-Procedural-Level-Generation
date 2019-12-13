'''
Author: Aaron J. Olson
https://aaronjolson.io

Implementation of a random walk algorithm to generate levels in Blender.
The process is via extrusion to preserve the mesh’s interior faces.
The interior walls property needs to be viewed with Xray view.

Example of 3D model output
https://sketchfab.com/models/a04f59e37966449c98c2839999800c8a
'''

import random
import bpy
import bmesh

ITERATIONS = 1000

current = None
next_face = None

# Position in space
y_pos = 1.0
x_pos = 1.0

# Controls the distances that are moved
# MUST BE AT LEAST 2
x_move_distance = 2.0
y_move_distance = 2.0

# For keeping track of all of the moves that have been made
visited_list = []

# make sure an object called 'Cube' is present in the scene, else add one
if bpy.data.objects.get('Cube'):
    ob = bpy.data.objects['Cube']
    bpy.ops.object.mode_set(mode='EDIT')
    mesh = bmesh.from_edit_mesh(bpy.context.object.data)
else:
    bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, location=(0, 0, 0))
    ob = bpy.data.objects['Cube']
    bpy.ops.object.mode_set(mode='EDIT')
    mesh = bmesh.from_edit_mesh(bpy.context.object.data)


def main():
    # Ensure that no faces are currently selected
    for f in mesh.faces:
        f.select = False

    for i in range(ITERATIONS):
        direction = get_random_direction()
        next_mesh_move(direction)
        visited_list.append((x_pos, y_pos))
    cleanup()


def get_random_direction():
    direction = {0: 'up', 1: 'right', 2: 'down', 3: 'left'}
    random_num = random.randint(0, 3)
    return direction[random_num]


def next_mesh_move(direction):
    global next_face
    global y_pos
    global x_pos
    for f in mesh.faces:
        f.select = False

    if direction == 'up':
        if (x_pos, y_pos + y_move_distance) not in visited_list:
            for f in mesh.faces:
                # Using face.calc_center_median and a walking through an array of x,y moves
                # we can calculate roughly which square we should appear on.
                # We can then select and set the right face to start the extrusion process from
                if f.normal.y == 1.0 and \
                        round(f.calc_center_median()[1]) == y_pos and \
                        round(f.calc_center_median()[0]) == x_pos - 1:
                    f.select = True
                    next_face = f
                    y_pos += y_move_distance
            extrude_up()
        else:
            y_pos += y_move_distance

    if direction == 'right':
        if (x_pos + x_move_distance, y_pos) not in visited_list:
            for f in mesh.faces:
                if f.normal.x == 1.0 and \
                        round(f.calc_center_median()[0]) == x_pos and \
                        round(f.calc_center_median()[1]) == y_pos - 1:
                    f.select = True
                    next_face = f
                    x_pos += x_move_distance
            extrude_right()
        else:
            x_pos += x_move_distance

    if direction == 'down':
        if (x_pos, y_pos - y_move_distance) not in visited_list:
            for f in mesh.faces:
                if f.normal.y == -1.0 and \
                        round(f.calc_center_median()[1]) == y_pos - y_move_distance and \
                        round(f.calc_center_median()[0]) == x_pos - 1:
                    f.select = True
                    next_face = f
                    y_pos -= y_move_distance
            extrude_down()
        else:
            y_pos -= y_move_distance

    if direction == 'left':
        if (x_pos - x_move_distance, y_pos) not in visited_list:
            for f in mesh.faces:
                if f.normal.x == -1.0 and \
                        round(f.calc_center_median()[0]) == x_pos - x_move_distance and \
                        round(f.calc_center_median()[1]) == y_pos - 1:
                    f.select = True
                    next_face = f
                    x_pos -= x_move_distance
            extrude_left()
        else:
            x_pos -= x_move_distance


def extrude_up():
    extrude(0, y_move_distance, 0)


def extrude_right():
    extrude(x_move_distance, 0.0, 0)


def extrude_down():
    extrude(0, -y_move_distance, 0)


def extrude_left():
    extrude(-x_move_distance, 0, 0)


def extrude(x, y, z):
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.transform.translate(value=(x, y, z),
                                orient_type='GLOBAL',
                                orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                                orient_matrix_type='GLOBAL',
                                constraint_axis=(False, False, True),
                                mirror=True,
                                use_proportional_edit=False,
                                proportional_edit_falloff='SMOOTH',
                                proportional_size=1,
                                use_proportional_connected=False,
                                use_proportional_projected=False
                                )



def cleanup():
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.object.mode_set(mode='OBJECT')


if __name__ == "__main__":
    main()
