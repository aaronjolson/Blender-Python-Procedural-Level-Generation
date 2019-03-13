'''
Author: Aaron J. Olson
https://aaronjolson.io

Implementation of a recursive backtracking algorithm to procedurally generate 3D levels in Blender.

Example 3D model output
https://sketchfab.com/models/7437daa03a0543d48c5eb599681d7e07
'''
import math
import random
import bpy
import bmesh

cols = 10
rows = 10

# global variables for keeping track of the grid and stack states during execution
grid = []
stack = []

current = None
next_face = None

# Position in space
y_pos = 1.0
x_pos = 1.0

# Controls the distances that are moved
x_move_distance = 2.0
y_move_distance = 2.0

# for keeping track of all of the moves that have been made
step_list = []

# make sure an object called 'Cube' is present in the scene, else add one
if bpy.data.objects.get('Cube'):
    ob = bpy.data.objects['Cube']
    bpy.ops.object.mode_set(mode='EDIT')
    mesh = bmesh.from_edit_mesh(bpy.context.object.data)
else:
    bpy.ops.mesh.primitive_cube_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(
        True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
        False, False, False, False))
    ob = bpy.data.objects['Cube']
    bpy.ops.object.mode_set(mode='EDIT')
    mesh = bmesh.from_edit_mesh(bpy.context.object.data)


def setup():
    for j in range(rows):
        for i in range(cols):
            cell = Cell(i, j)
            grid.append(cell)
    global current
    current = grid[0]
    generate_level()


def generate_level():
    # flag for tracking state of when the maze is finished
    done = False

    for f in mesh.faces:
        f.select = False

    while True:
        global grid
        global current
        global stack
        global next_cell

        current.visited = True

        # determine if the maze can move forward to a yet unreached neighboring cell
        next_cell, direction = current.check_neighbors()
        if next_cell:
            next_mesh_move(direction)
            next_cell.visited = True

            # keep track of the directions the maze has gone using the stack
            stack.append(current)

            # sets the current cell to the next cell
            current = next_cell

        elif len(stack) > 0:
            current = stack.pop()
            move_back()

        for cell in grid:
            if cell.visited is False:
                done = False
                break
            else:
                done = True
        if done:
            break


class Cell:
    def __init__(self, i, j):
        self.i = i
        self.j = j
        self.visited = False

    def check_neighbors(self):
        global grid
        neighbors = []
        direction = {}
        direction_key = 0
        up = None
        right = None
        down = None
        left = None

        if index(self.i, self.j - 1):
            up = grid[index(self.i, self.j - 1)]
        if index(self.i + 1, self.j):
            right = grid[index(self.i + 1, self.j)]
        if index(self.i, self.j + 1):
            down = grid[index(self.i, self.j + 1)]
        if index(self.i - 1, self.j):
            left = grid[index(self.i - 1, self.j)]

        if up and not up.visited:
            neighbors.append(up)
            direction[direction_key] = 'up'
            direction_key += 1
        if right and not right.visited:
            neighbors.append(right)
            direction[direction_key] = 'right'
            direction_key += 1

        if down and not down.visited:
            neighbors.append(down)
            direction[direction_key] = 'down'
            direction_key += 1
        if left and not left.visited:
            neighbors.append(left)
            direction[direction_key] = 'left'

        if len(neighbors) > 0:
            r = int(math.floor(random.uniform(0, len(neighbors) - .000001)))
            return neighbors[r], direction[r]
        else:
            return None, None


def index(i, j):
    if i < 0 or j < 0 or i > cols - 1 or j > rows - 1:
        return None
    else:
        return i + j * cols


def next_mesh_move(direction):
    global next_face
    global y_pos
    global x_pos
    for f in mesh.faces:
        f.select = False

    if direction == 'up':
        for f in mesh.faces:
            if f.normal.y == 1.0 and \
                    round(f.calc_center_median()[1]) == y_pos and \
                    round(f.calc_center_median()[0]) == x_pos - 1:
                f.select = True
                next_face = f
                y_pos += y_move_distance * 2
                step_list.append(direction)
        extrude_up()
        extrude_up()

    if direction == 'right':
        for f in mesh.faces:
            if f.normal.x == 1.0 and \
                    round(f.calc_center_median()[0]) == x_pos and \
                    round(f.calc_center_median()[1]) == y_pos - 1:
                f.select = True
                next_face = f
                x_pos += x_move_distance * 2
                step_list.append(direction)
        extrude_right()
        extrude_right()

    if direction == 'down':
        for f in mesh.faces:
            if f.normal.y == -1.0 and \
                    round(f.calc_center_median()[1]) == y_pos - y_move_distance and \
                    round(f.calc_center_median()[0]) == x_pos - 1:
                f.select = True
                next_face = f
                y_pos -= y_move_distance * 2
                step_list.append(direction)
        extrude_down()
        extrude_down()

    if direction == 'left':
        for f in mesh.faces:
            if f.normal.x == -1.0 and \
                    round(f.calc_center_median()[0]) == x_pos - x_move_distance and \
                    round(f.calc_center_median()[1]) == y_pos - 1:
                f.select = True
                next_face = f
                x_pos -= x_move_distance * 2
                step_list.append(direction)
        extrude_left()
        extrude_left()


# Used to keep track of the position in space being moved through
def move_back():
    global y_pos
    global x_pos
    global step_list
    direction = step_list.pop()
    if direction == 'up':
        y_pos -= y_move_distance * 2
    if direction == 'right':
        x_pos -= x_move_distance * 2
    if direction == 'down':
        y_pos += y_move_distance * 2
    if direction == 'left':
        x_pos += x_move_distance * 2


def extrude_up():
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.transform.translate(value=(0, y_move_distance, 0),
                                constraint_axis=(False, True, False),
                                constraint_orientation='GLOBAL',
                                mirror=False, proportional='DISABLED',
                                proportional_edit_falloff='SMOOTH',
                                proportional_size=1,
                                snap=False,
                                snap_target='CLOSEST',
                                snap_point=(0, 0, 0),
                                snap_align=False,
                                snap_normal=(0, 0, 0),
                                texture_space=False,
                                release_confirm=True
                                )


def extrude_right():
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.transform.translate(value=(x_move_distance, 0.0, 0),
                                constraint_axis=(True, False, False),
                                constraint_orientation='GLOBAL',
                                mirror=False, proportional='DISABLED',
                                proportional_edit_falloff='SMOOTH',
                                proportional_size=1,
                                snap=False,
                                snap_target='CLOSEST',
                                snap_point=(0, 0, 0),
                                snap_align=False,
                                snap_normal=(0, 0, 0),
                                texture_space=False,
                                release_confirm=True
                                )


def extrude_down():
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.transform.translate(value=(0, -y_move_distance, 0),
                                constraint_axis=(False, True, False),
                                constraint_orientation='GLOBAL',
                                mirror=False, proportional='DISABLED',
                                proportional_edit_falloff='SMOOTH',
                                proportional_size=1,
                                snap=False,
                                snap_target='CLOSEST',
                                snap_point=(0, 0, 0),
                                snap_align=False,
                                snap_normal=(0, 0, 0),
                                texture_space=False,
                                release_confirm=True
                                )


def extrude_left():
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.transform.translate(value=(-x_move_distance, 0.0, 0),
                                constraint_axis=(True, False, False),
                                constraint_orientation='GLOBAL',
                                mirror=False, proportional='DISABLED',
                                proportional_edit_falloff='SMOOTH',
                                proportional_size=1,
                                snap=False,
                                snap_target='CLOSEST',
                                snap_point=(0, 0, 0),
                                snap_align=False,
                                snap_normal=(0, 0, 0),
                                texture_space=False,
                                release_confirm=True
                                )


if __name__ == "__main__":
    setup()
