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

# total size of the maze to be created eg 10x10
cols = 10
rows = 10

# global variables for keeping track of the grid and cell_stack states during execution
cell_array = []  # keeps a flat list of all cells
cell_stack = []  # keeps stack of the order cells have been visited
direction_stack = []  # for keeping track of all of the moves that have been made

current_cell = None
next_face = None

# Position in space
y_pos = 1.0
x_pos = 1.0

# Controls the distances that are moved
x_move_distance = 2.0
y_move_distance = 2.0


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
    global current_cell
    # create a 2D array of cells inside of the cell_array variable
    for y in range(rows):
        for x in range(cols):
            cell = Cell(x, y)
            cell_array.append(cell)
    # set the current position to the first cell in the cell_array
    current_cell = cell_array[0]
    generate_level()


def generate_level():
    # flag for tracking state of when the maze is finished
    done = False

    # make sure that no faces are selected
    for f in mesh.faces:
        f.select = False

    # enter a long running loop that can only be exited when certain criteria are met
    while True:
        global cell_array
        global current_cell
        global cell_stack
        global next_cell

        current_cell.visited = True

        # determine if the maze can move forward from the current cell to a yet unreached neighboring cell
        next_cell, direction = current_cell.check_neighbors()
        if next_cell:  # if an unvisited neighbor cell was found to move to
            next_mesh_move(direction)
            next_cell.visited = True

            # keep track of the directions the maze has gone using the cell_stack
            cell_stack.append(current_cell)

            # sets the current_cell cell to the next cell
            current_cell = next_cell

        elif len(cell_stack) > 0:  # if there was not an unvisited cell to move to from the current cell
            current_cell = cell_stack.pop()
            move_back()

        for cell in cell_array:
            if cell.visited is False:
                done = False
                break
            else:
                done = True
        if done:
            break


class Cell:
    def __init__(self, x, y):
        self.x = x  # cell's row position
        self.y = y  # cell's column position
        self.visited = False

    def check_neighbors(self):
        global cell_array
        neighbors = []  # keep track of the neighboring cells
        unvisited_directions = {}  # keep track of the relative direction of unvisited neighboring cells
        direction_key = 0  # keeps track of the number of directions available of unvisited cells
        # for storing each individual neighbor cell, if applicable
        up = None
        right = None
        down = None
        left = None

        # check each direction to determine if neighboring cells exist on the cell_array
        if index(self.x, self.y - 1):
            up = cell_array[index(self.x, self.y - 1)]
        if index(self.x + 1, self.y):
            right = cell_array[index(self.x + 1, self.y)]
        if index(self.x, self.y + 1):
            down = cell_array[index(self.x, self.y + 1)]
        if index(self.x - 1, self.y):
            left = cell_array[index(self.x - 1, self.y)]

        # if the cell has a neighbor in a particular direction then check if that neighbor has been visited yet
        # if it has not, store the
        if up and not up.visited:
            neighbors.append(up)
            unvisited_directions[direction_key] = 'up'
            direction_key += 1
        if right and not right.visited:
            neighbors.append(right)
            unvisited_directions[direction_key] = 'right'
            direction_key += 1
        if down and not down.visited:
            neighbors.append(down)
            unvisited_directions[direction_key] = 'down'
            direction_key += 1
        if left and not left.visited:
            neighbors.append(left)
            unvisited_directions[direction_key] = 'left'

        if len(neighbors) > 0:
            # randomly return the direction of an unvisited neighbor cell
            r = int(math.floor(random.uniform(0, len(neighbors) - .000001)))
            return neighbors[r], unvisited_directions[r]
        else:
            return None, None


def index(x, y):
    if x < 0 or y < 0 or x > cols - 1 or y > rows - 1:
        return None
    else:
        return x + y * cols


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
                direction_stack.append(direction)
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
                direction_stack.append(direction)
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
                direction_stack.append(direction)
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
                direction_stack.append(direction)
        extrude_left()
        extrude_left()


# Used to keep track of the position in space being moved through
def move_back():
    global y_pos
    global x_pos
    global direction_stack
    direction = direction_stack.pop()
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
