from random import randint
import bpy
import bmesh

ROOM_MIN = 1000


class Dungeon:
    def __init__(self):
        self.x_size = 60
        self.y_size = 40
        self.min_room_size = 5
        self.max_room_size = 15
        self.min_rooms = 10
        self.max_rooms = 15
        self.num_rooms = None
        self.map = None
        self.rooms = None
        self.connected = None

    def generate(self):
        self.map = []
        self.rooms = []
        self.connected = []

        for y in range(self.y_size):  # build out the initial 2d grid array
            self.map.append([])
            for x in range(self.x_size):  # initialize each row
                self.map[y].append({})
                self.map[y][x]['t'] = 0
                self.map[y][x]['pos'] = {
                    'x': x,
                    'y': y
                }
                self.map[y][x]['r'] = 1

        self.num_rooms = get_random_int(self.min_rooms, self.max_rooms)  # set the total number of rooms to be generated

        i = 0
        while i < self.num_rooms:
            # generate rooms, check if the are overlapping, shrink the w and h by 1
            room = {}
            room['x'] = get_random_int(1, (self.x_size - self.max_room_size - 1))
            room['y'] = get_random_int(1, (self.y_size - self.max_room_size - 1))
            room['w'] = get_random_int(self.min_room_size, self.max_room_size)
            room['h'] = get_random_int(self.min_room_size, self.max_room_size)
            room['connected'] = False
            if self.does_collide(room):
                continue
            room['w'] -= 1
            room['h'] -= 1
            self.rooms.append(room)
            i += 1
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
        self.place_cubes()

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

    def find_closest(self, room, others=None):
        master_room = {'x': room['x'] + room['w'] / 2,
                       'y': room['y'] + room['h'] / 2
                       }
        room_min = ROOM_MIN
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

    def connect_rooms(self, room, closest_room, should_connect):
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
        if should_connect:
            room['connected'] = True
            closest_room['connected'] = True
            self.connected.append(room)

    def place_cubes(self):
        yy = 0
        for y in range(self.y_size):
            xx = 0
            for x in range(self.x_size):
                if self.map[y][x]['t'] == 0 or self.map[y][x]['t'] == 2:
                    pass
                else:
                    bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, location=(xx, yy, 0))
                xx += 2
            yy += 2


def get_random_int(low, high):
    return randint(low, high - 1)


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
