"""
    Run inside Blender, and populate sys.argv[1] with the JSON location:

    sys.argv.append('data.json')
    exec(open("createMesh.py").read())
"""

try:
    import bpy
    import bmesh
    from mathutils import Vector
except:
    print("Run me in Blender.")

import json
import sys
import math

import numpy as np


def loadData(fileName):
    return np.array(list(json.load(open(fileName, "r"))))


def createMesh(data):

    print(data.shape)
    nx, ny = data.shape

    size = 20.0
    scale = 1.0

    xBins = np.linspace(-size // 2, size // 2, nx)
    yBins = np.linspace(-size // 2, size // 2, ny)

    bpy.ops.mesh.primitive_grid_add(x_subdivisions=nx, y_subdivisions=ny, size=size)

    ob = bpy.context.object
    me = ob.data

    bm = bmesh.new()
    bm.from_mesh(me)
    faces = bm.faces[:]

    data = np.array(list(json.load(open(fileName, "r"))))

    for face in faces:

        print(face.index)

        center = face.calc_center_median()

        xBinIdx = np.digitize(center[0], xBins)
        yBinIdx = np.digitize(center[1], yBins)

        # TODO: Fix me properly
        xBinIdx = max(0, min(xBinIdx, nx - 1))
        yBinIdx = max(0, min(yBinIdx, ny - 1))

        w = data[xBinIdx][yBinIdx] * scale

        r = bmesh.ops.extrude_discrete_faces(bm, faces=[face])

        bmesh.ops.translate(bm, vec=Vector((0, 0, w)), verts=r["faces"][0].verts)

    bm.to_mesh(me)
    me.update()

    # Add a plane for interest

    bpy.ops.mesh.primitive_plane_add(size=1000, location=(0, 0, -10.0))

    # Add and align the camera

    camera_data = bpy.data.cameras.new(name="Camera")
    camera_object = bpy.data.objects.new("Camera", camera_data)
    camera_object.location = (66.0, -65.0, 78.0)
    camera_object.rotation_euler = (math.radians(55.8), 0, math.radians(45.8))

    bpy.context.scene.collection.objects.link(camera_object)

    # Add a light source

    lamp_data = bpy.data.lights.new(name="Lamp", type="POINT")
    lamp_object = bpy.data.objects.new(name="Lamp", object_data=lamp_data)
    lamp_object.location = (50, -30, 80)
    lamp_object.data.energy = 1e5
    bpy.context.scene.collection.objects.link(lamp_object)


if __name__ == "__main__":

    if len(sys.argv) > 1:

        fileName = sys.argv[1]

        data = loadData(fileName)
        createMesh(data)

    else:

        print("Need JSON file name argument.")
