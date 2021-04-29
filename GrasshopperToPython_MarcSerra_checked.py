"""Provides a scripting component.
    Inputs:
        x: [int] Number of curves
        y: [int] Y coordinate
        numSegments: [int] Number of divisions of each line
    Output:
        a: [point] Initial points X direction
        b: [piont] Moved points in Y direction
        c: [curve] Lines from pt0 to ptMoved
        d: [point] Grid of points moved in zAxis
        e: [curve] Interpolated curves from Grid Points
        f: [surface] Surface lofted from Interpolated Curves
        g: [mesh] Mesh"""

#you will need all this libraries
import Rhino.Geometry as rg
import ghpythonlib.treehelpers as th #this library is needed to import nested lists to grasshopper trees
import math #this library is needed to create sine and cosine waves

#----------------------------------------------------------
#1.- create first series of points -

pointList1 = []
for i in range(x):
    ptA = rg.Point3d(i,0,0)
    pointList1.append(ptA)

a = pointList1

#----------------------------------------------------------
#2. - create second series of points -

pointList2 = []
for i in range(x):
    ptB = rg.Point3d(i,y,0)
    pointList2.append(ptB)

b = pointList2

#----------------------------------------------------------
#3. - create lines from two serie of points - 

lineList = []
for i in (range(len(a))):
    line = rg.LineCurve(a[i],b[i])
    lineList.append(line)

c = lineList

#----------------------------------------------------------
#4.- divide curve -

allDivPts = [] #this will be a list of lists
for line in lineList:
    linePts =[] #create an empty list to fill each iteration
    curve = line.ToNurbsCurve()
    params = rg.Curve.DivideByCount(curve,10,True)
    for p in params:
        divPt = rg.Curve.PointAt(line,p)
        linePts.append(divPt)
    allDivPts.append(linePts) #append the list of points PER LINE to another list

d = th.list_to_tree(allDivPts) #this is how you output nested lists to gh trees

#----------------------------------------------------------
#5.- apply sine function to points

allMovedPts = [] #list of all moved points
for list in allDivPts:
    movedPts= [] #list of moved points
    for pt in list:
        vector = rg.Vector3d(pt)
        vLen = vector.Length
        zVec = rg.Vector3d(0,0,math.sin(vLen))
        newPt = pt + zVec
        movedPts.append(newPt)
    allMovedPts.append(movedPts)

d = th.list_to_tree(allMovedPts) #output list of list to gh

#----------------------------------------------------------
#6.- make a curve from a list of points

curveList = []
for list in allMovedPts:
    curveInt = rg.Curve.CreateInterpolatedCurve(list,3,rg.CurveKnotStyle.Chord)
    curveList.append(curveInt)

e = curveList

#----------------------------------------------------------
# 7.- create a loft surface from curves

surface = rg.Brep.CreateFromLoft(curveList,rg.Point3d.Unset,rg.Point3d.Unset,rg.LoftType.Normal,False)

f = surface

#----------------------------------------------------------
#8.- create a mesh from Brep

allMesh = rg.Mesh()

for i in range(len(allMovedPts)-1):
    for j in range(len(allMovedPts[i])-1):
        m = rg.Mesh()
        v0 = allMovedPts[i][j]
        v1 = allMovedPts[i][j+1]
        v2 = allMovedPts[i+1][j+1]
        v3 = allMovedPts[i+1][j]
        
        m.Vertices.Add(v0)
        m.Vertices.Add(v1)
        m.Vertices.Add(v2)
        m.Vertices.Add(v3)
        
        m.Faces.AddFace(0,1,2,3)
        
        allMesh.Append(m)

allMesh.Weld(math.pi)
allMesh.Normals.ComputeNormals()

g = allMesh

#THE END