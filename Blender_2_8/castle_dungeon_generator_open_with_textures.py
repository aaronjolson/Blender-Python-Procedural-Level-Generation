from random import randint
import bpy
import bmesh


class Dungeon:
    def __init__(self):
        self.x_size = 60
        self.y_size = 40
        self.min_room_size = 5
        self.max_room_size = 15
        self.num_rooms = None
        self.min_rooms = 10
        self.max_rooms = 15
        self.map = None
        self.rooms = None
        self.first_room = None
        self.last_room = None
        self.stairs_up = None
        self.stairs_down = None
        self.connected = None
        self.light = 0

    def generate(self):
        self.map = []
        self.rooms = []
        self.first_room = None
        self.last_room = None
        self.connected = []

        # build out the initial 2d array
        for y in range(self.y_size):
            # initialize each row
            self.map.append([])
            for x in range(self.x_size):
                self.map[y].append({})
                self.map[y][x]['t'] = 0
                self.map[y][x]['path'] = False
                self.map[y][x]['pos'] = {
                    'x': x,
                    'y': y
                }
                if self.light == 0:
                    self.map[y][x]['r'] = 1
                else:
                    self.map[y][x] = 0
        self.num_rooms = get_random_int(self.min_rooms, self.max_rooms)
        i = 0
        while i < self.num_rooms:
            room = {}
            room['x'] = get_random_int(1, (self.x_size - self.max_room_size - 1))
            room['y'] = get_random_int(1, (self.y_size - self.max_room_size - 1))
            room['w'] = get_random_int(self.min_room_size, self.max_room_size)
            room['h'] = get_random_int(self.min_room_size, self.max_room_size)
            room['c'] = False
            if self.does_collide(room):
                continue
            room['w'] -= 1
            room['h'] -= 1
            self.rooms.append(room)
            i += 1
        self.shrink_map(0)
        for k in range(len(self.rooms)):
            room = self.rooms[k]
            closest_room = self.find_closest(room, self.connected)
            if closest_room is None:
                break
            self.connect_rooms(room, closest_room, True)
        for k in range(len(self.rooms)):
            room = self.rooms[k]
            for y in range(room['y'], room['y'] + room['h']):
                for x in range(room['x'], room['x'] + room['w']):
                    self.map[y][x]['t'] = 1
        # this part builds the walls
        for y in range(self.y_size):
            for x in range(self.x_size):
                if self.map[y][x]['t'] == 1:
                    yy = y - 1
                    while yy <= y + 1:
                        xx = x - 1
                        while xx <= x+1:
                            if self.map[yy][xx]['t'] == 0:
                                self.map[yy][xx]['t'] = 2
                            xx += 2
                        yy += 2

        self.find_farthest()
        self.mark_stairs()
        self.place_geometry()

    def does_collide(self, room):
        for i in range(len(self.rooms)):
            comparison_room = self.rooms[i]
            if room == comparison_room:
                continue
            if room['x'] < comparison_room['x'] + comparison_room['w'] \
                    and room['x'] + room['w'] > comparison_room['x'] \
                    and room['y'] < comparison_room['y'] + comparison_room['h'] \
                    and room['y'] + room['h'] > comparison_room['y']:
                return True
        return False

    def point_collide(self, x, y):
        if self.map[x][y]['t'] == 1:
            return False
        return True

    def shrink_map(self, shrink_limit):
        for value in range(shrink_limit):
            for i in range(len(self.rooms)):
                room = self.rooms[i]
                if room['x'] > 1:
                    room['x'] -= 1
                if room['y'] > 1:
                    room['y'] -= 1
                if self.does_collide(room):
                    if room['x'] > 1:
                        room['x'] += 1
                    if room['y'] > 1:
                        room['y'] += 1
                    continue

    def find_closest(self, room, others=None):
        master_room = {'x': room['x'] + room['w'] / 2,
                       'y': room['y'] + room['h'] / 2
                       }
        room_min = 1000
        final_room = None
        for i in range(len(self.rooms)):
            comparison_room = self.rooms[i]
            if room == comparison_room:
                continue
            if others is not None:
                is_closest = False
                for j in range(len(others)):
                    if comparison_room == others[j]:
                        is_closest = True
                        break
                if is_closest:
                    continue
            room_avg = {
                'x': comparison_room['x'] + comparison_room['w'] / 2,
                'y': comparison_room['y'] + comparison_room['h'] / 2
            }
            room_calc = abs(room_avg['x'] - master_room['x']) + abs(room_avg['y'] - master_room['y'])
            if room_calc < room_min:
                room_min = room_calc
                final_room = comparison_room
        return final_room

    def find_farthest(self):
        room_pair = []
        swap_room = 0
        for i in range(len(self.rooms)):
            room = self.rooms[i]
            midA = {
                'x': room['x'] + room['w'] / 2,
                'y': room['y'] + room['h'] / 2
            }
            for j in range(len(self.rooms)):
                if i == j:
                    continue
                closest_room = self.rooms[j]
                midB = {
                    'x': closest_room['x'] + closest_room['w'] / 2,
                    'y': closest_room['y'] + closest_room['h'] /2
                }
                math_room = abs(midB['x'] - midA['x']) + abs(midB['y'] - midA['y'])
                if math_room > swap_room:
                    swap_room = math_room
                    room_pair = [room, closest_room]
        self.first_room = room_pair[0]
        self.last_room = room_pair[1]

    def connect_rooms(self, room, closest_room, good):
        path_part_1 = {
            'x': get_random_int(room['x'], room['x'] + room['w']),
            'y': get_random_int(room['y'], room['y'] + room['h'])
        }
        path_part_2 = {
            'x': get_random_int(closest_room['x'], closest_room['x'] + closest_room['w']),
            'y': get_random_int(closest_room['y'], closest_room['y'] + closest_room['h'])
        }
        while path_part_1['x'] != path_part_2['x'] or path_part_1['y'] != path_part_2['y']:
            if path_part_1["x"] != path_part_2["x"]:
                if path_part_2["x"] < path_part_1["x"]:
                    path_part_2["x"] += 1
                else:
                    path_part_2["x"] -= 1
            else:
                if path_part_1["y"] != path_part_2["y"]:
                    if path_part_2["y"] < path_part_1["y"]:
                        path_part_2["y"] += 1
                    else:
                        path_part_2["y"] -= 1

            self.map[path_part_2['y']][path_part_2['x']]['t'] = 1
        if good:
            room['c'] = True
            closest_room['c'] = True
            self.connected.append(room)

    def mark_stairs(self):
        self.stairs_up = {
            'pos': {
                'x': get_random_int(self.first_room['x'] + 1, self.first_room['x'] + self.first_room['w'] - 1),
                'y': get_random_int(self.first_room['y'] + 1, self.first_room['y'] + self.first_room['h'] - 1)
            }
        }
        self.stairs_down = {
            'pos': {
                'x': get_random_int(self.last_room['x'] + 1, self.last_room['x'] + self.last_room['w'] - 1),
                'y': get_random_int(self.last_room['y'] + 1, self.last_room['y'] + self.last_room['h'] - 1)
            }
        }
        self.map[self.stairs_up["pos"]["y"]][self.stairs_up["pos"]["x"]]["t"] = 3
        self.map[self.stairs_down["pos"]["y"]][self.stairs_down["pos"]["x"]]["t"] = 4

    def place_geometry(self):
        yy = 0
        for y in range(self.y_size):
            xx = 0
            for x in range(self.x_size):
                if self.map[y][x]['t'] == 0 or self.map[y][x]['r'] == 0:  # these are not part of the maze body
                    pass
                elif self.map[y][x]['t'] == 2:
                    # these are the walls
                    bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, location=(xx, yy, 0))
                elif self.map[y][x]['t'] == 3:
                    # this is the beginning
                    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, enter_editmode=False, location=(xx, yy, 0))
                elif self.map[y][x]['t'] == 4:
                    # this is the end
                    bpy.ops.mesh.primitive_cylinder_add(radius=1, enter_editmode=False, location=(xx, yy, 0))
                else:
                    # these are the floor tiles,
                    bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, location=(xx, yy, -1))
                xx += 2
            yy += 2


def get_random_int(low, high):
    return randint(low, high-1)


def separate_the_floor(ob, floor_mat_index):
    bpy.ops.object.mode_set(mode='EDIT')
    # make sure there is only one object in the scene, else figure out a better way to get the object.
    mesh = bmesh.from_edit_mesh(bpy.context.object.data)
    bpy.ops.mesh.select_all(action='DESELECT')
    for f in mesh.faces:
        if f.calc_center_median()[2] == -1:
            f.select = True
            ob.active_material_index = floor_mat_index
            bpy.ops.object.material_slot_assign()


def append_material(directory, filepath, material_name):
    bpy.ops.wm.append(
        filename=material_name,
        directory=directory,
        filepath=filepath,
        link=False,
    )


def assign_material(ob, mat_name):
    ob.data.materials.append(bpy.data.materials.get(mat_name))


# joins all separate cube into a single object,
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
    # get back out of edit mode
    bpy.ops.object.mode_set(mode='OBJECT')


# delete everything in the scene
def clear_scene():
    if bpy.context.active_object:
        if bpy.context.active_object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


if __name__ == '__main__':
    clear_scene()
    dungeon = Dungeon()
    dungeon.generate()
    cleanup_mesh()

    RESOURCE_BLEND_FILE = "resources.blend"
    PATH_TO_PROJECT_DIRECTORY = "C:\\Users\\aaron\\PycharmProjects"  # TODO: change to your own location
    PATH_TO_RESOURCE_FILE = f"\\Blender-Python-Procedural-Level-Generation\\Blender_2_8\\resources\\{RESOURCE_BLEND_FILE}\\Material"
    append_material(
        directory=f"{PATH_TO_PROJECT_DIRECTORY}{PATH_TO_RESOURCE_FILE}",
        filepath=RESOURCE_BLEND_FILE,
        material_name="castlebrick",
    )
    append_material(
        directory=f"{PATH_TO_PROJECT_DIRECTORY}{PATH_TO_RESOURCE_FILE}",
        filepath=RESOURCE_BLEND_FILE,
        material_name="cobblestone",
    )
    if len(bpy.data.objects) > 0:
        ob = bpy.data.objects[0]
        assign_material(ob, 'castlebrick')
        assign_material(ob, 'cobblestone')
        separate_the_floor(ob, 1)
