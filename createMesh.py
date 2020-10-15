'''
    Run inside Blender, and populate sys.argv[1] with the JSON location:

    sys.argv.append('data.json')
    exec(open("createMesh.py").read())
'''

try:
    import bpy
    import bmesh
    from mathutils import Vector
except:
    print('Run me in Blender.')

import json
import sys

import numpy as np

def loadData(fileName):
    return np.array(list(json.load(open(fileName, 'r'))))

def createMesh(data):

    print(data.shape)
    nx, ny = data.shape

    size = 20.0
    scale = 1.0

    xBins = np.linspace(-size // 2, size // 2, nx)
    yBins = np.linspace(-size // 2, size // 2, ny)

    bpy.ops.mesh.primitive_grid_add(x_subdivisions=nx, y_subdivisions=ny, size = size)

    ob = bpy.context.object
    me = ob.data

    bm = bmesh.new()
    bm.from_mesh(me)
    faces = bm.faces[:]

    data = np.array(list(json.load(open(fileName, 'r'))))

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

        bmesh.ops.translate(bm, vec=Vector((0,0,w)), verts=r['faces'][0].verts)

    bm.to_mesh(me)
    me.update()

if __name__ == '__main__':

    if len(sys.argv) > 1:

        fileName = sys.argv[1]

        data = loadData(fileName)
        createMesh(data)

    else:

        print('Need JSON file name argument.')
