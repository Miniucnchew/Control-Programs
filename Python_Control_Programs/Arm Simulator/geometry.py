"""
Simple geometry maker fumctions for arm demo

(C)2008 by Mark Tomczak (fixermark@gmail.com)

Free for educational and demonstration purposes, and for all uses regarding the
FIRST Robotics competition.

This program was built with Panda3D 1.4.2 (http://www.panda3d.org)
"""
from pandac.PandaModules import *

def makeCube():
    """
    Builds cubes from scratch in Panda. Panda is designed to load completed
    models, called eggs---since we don't have an egg around, we'll just
    build a cube that's 1 unit long on each side.

    This is basically rendering stuff that has little bearing on the
    simulation; for more information visit the Panda manual at
    http://panda3d.org/wiki/index.php/How_Panda3D_Stores_Vertices_and_Geometry
    """
    vertices=[
        (-.5,-.5,-.5),
        (-.5,-.5,.5),
        (-.5,.5,-.5),
        (-.5,.5,.5),
        (.5,-.5,-.5),
        (.5,-.5,.5),
        (.5,.5,-.5),
        (.5,.5,.5)
    ]
    windings=[
        ((0,0,-1),[0,2,6,4]),
        ((0,0,1),[5,7,3,1]),
        ((0,-1,0),[4,5,1,0]),
        ((0,1,0),[2,3,7,6]),
        ((-1,0,0),[0,1,3,2]),
        ((1,0,0),[6,7,5,4])
    ]
    vdata=GeomVertexData('vertdata',GeomVertexFormat.getV3n3(),Geom.UHStatic)

    vertex=GeomVertexWriter(vdata,'vertex')
    normal=GeomVertexWriter(vdata,'normal')
    
    for (normalCoords,windingEntries) in windings:
        for x in windingEntries:
            vertex.addData3f(*(vertices[x]))
            normal.addData3f(*normalCoords)


    prim=GeomTrifans(Geom.UHStatic)

    for i in xrange(0,len(windings)):
        prim.addConsecutiveVertices(i*4,4)
        prim.closePrimitive()

    geom=Geom(vdata)
    geom.addPrimitive(prim)

    node=GeomNode('gnode')
    node.addGeom(geom)

    return node
                             
    
    
