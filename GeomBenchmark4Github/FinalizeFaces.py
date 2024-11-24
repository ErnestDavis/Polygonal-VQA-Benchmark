import numpy as np
import Graph

global borders, commonVertex

def FinalizeFaces(v,e,f):
    global vertices, edges, faces
    vertices = v
    edges = e
    faces = f
    for i in range(len(faces)):
        faces[i].num=i
    for fa in faces:
        fa.trueVertices = SetTrueVertices(fa)
        fa.numSides = len(fa.trueVertices)-1
    AssignColors()
    AssignLetters()
    return faces    
   
def SetTrueVertices(fa):
    ee = fa.edges
    n = len(ee)
    for i in range(n):
        if abs(ee[i].direction - ee[i-1].direction) > Graph.angleeps:
            istart = i
            break
    trueVertices = [ee[istart].tail]
    for i in range(istart+1,n):
        if abs(ee[i].direction - ee[i-1].direction) > Graph.angleeps:
            trueVertices += [ee[i].tail]
    return trueVertices + [trueVertices[0]]
        
    
def AssignColors():
    global faces, edges, borders, commonVertex
    ff = len(faces)
    borders = [[0]*ff]*ff
    for i in range(1,ff):
        borders[i]=[0]*ff    # Python has some really terrible design decisions
    for e in edges:
        i = e.leftFace.num
        j = e.reverse.leftFace.num
        borders[i][j] = 1
    numBorders = [0]*ff
    for i in range(1,ff):
        for j in range(1,ff):
            numBorders[i] += borders[i][j]
    numBorders[0] = ff+100
    list = []
    for i in range(ff):
        j = np.argmin(numBorders)
        list = [j] + list       
        for k in range(1,ff):
            numBorders[k] -= borders[j][k]
        numBorders[j] = 10000+ff   
    commonVertex = FindCommonVertices(vertices,faces)
    aa = AssignColors1(list,borders)
    for i in range(ff):
        faces[list[i]].color = aa[i]
        
def AssignColors1(list,borders):
    aa = [0]*len(list)   # list of color assignments to the faces indexed in list
    for i in range(1,len(list)):
        possColors = [0]+[2]*6
        li = list[i]
        for j in range(i):
            lj = list[j]
            if borders[li][lj]:
                possColors[aa[j]] = 0
            elif commonVertex[li][lj]:
                possColors[aa[j]] = 1 
        if 2 in possColors:
            aa[i] = possColors.index(2)
        else:
            aa[i]=possColors.index(1)
    return aa     
        
def FindCommonVertices(vertices,faces):
    ff = len(faces)
    commonVertex = [[False]*ff]*ff
    for i in range(1,ff):
        commonVertex[i]=[False]*ff    
    for v in vertices:
        ff = len(v.faces)
        for i in range(ff-1):
            numi = v.faces[i].num
            for j in range(i+1,ff):
                numj = v.faces[j].num                    
                commonVertex[numi][numj] = True
                commonVertex[numj][numi] = True
    return commonVertex

   
    
def AssignLetters():
    global faces
    a = np.array(range(1,len(faces)))
    np.random.shuffle(a)
    faces[0].letter = "Outside"
    for i in range(1,len(faces)):
        faces[i].letter = chr(ord('@')+a[i-1])

