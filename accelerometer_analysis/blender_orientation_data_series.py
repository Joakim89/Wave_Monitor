import bpy
import numpy
import serial

print(serial.serialwin32.win32)

def del_frames():
    context = bpy.context
    for ob in context.selected_objects:
        ob.animation_data_clear()

obj = bpy.context.object


# read file and save to list
f = open("C:/Users/Joakim/Desktop/ITU - SDT DT/Thesis/orientation_visualization/euler-angles2.txt", "r")
readings = []
for line in f.readlines():
    numbers = line.replace("\n", "").split("\t")
    readings.append(numbers)
f.close()

for i in range(len(readings)):
    x, y, z = float(readings[i][0]), float(readings[i][1]), float(readings[i][2])
    obj.rotation_euler = [x, y, z]
    obj.keyframe_insert("rotation_euler", frame=i)

# writing to console: for debugging:
def console_get():
    for area in bpy.context.screen.areas:
        if area.type == 'CONSOLE':
            for space in area.spaces:
                if space.type == 'CONSOLE':
                    return area, space
    return None, None

def console_write(text):
    area, space = console_get()
    if space is None:
        return

    context = bpy.context.copy()
    context.update(dict(
        space=space,
        area=area,
    ))
    for line in text.split("\n"):
        bpy.ops.console.scrollback_append(context, text=line, type='OUTPUT')

console_write("Hello hey hey")
