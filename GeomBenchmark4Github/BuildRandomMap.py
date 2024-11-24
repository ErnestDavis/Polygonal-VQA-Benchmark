import numpy as np
import Split
import Graph
import Frame
import FinalizeFaces
import DrawGraph

global numTries, epsilon
numTries = 10
epsilon = 0.07

def BuildRandomMap(nfaces,x,y,seed):
    global vertices,edges,faces
    np.random.seed(seed)
    Split.vertices, Split.edges, Split.faces = Frame.makeFrame(x,y)
    for i in range(nfaces-1):
        AddRandomFace()
    FinalizeFaces.FinalizeFaces(Split.vertices, Split.edges,Split.faces)
    Split.ShowMap(False)
    DrawGraph.DrawGraph(Split.faces,x,y)
    return Graph.Map(Split.vertices,Split.edges,Split.faces,(x,y))
   
def AddRandomFace():
    found = False
    while not found:
        face = ChooseRandomFace()
        match ChooseRandomAction(face):
            case 0:
                 found = RandomlySplitVV(face)
            case 1:
                 found = RandomlySplitVE(face)
            case 2:
                 found = RandomlySplitEE(face)
            case 3:
                 found = RandomlySplitVVPath(face)
            case 4:
                 found = RandomlySplitVCycle(face)
            case 5:
                 found = RandomlySplitVEPath(face)            
            case 6:
                 found = RandomlySplitEEPath(face)
            case 7:
                 found = RandomlySplitSameEdgePath(face)
            case 8:
                 found = RandomlySameEdgeCycle(face)

def ChooseRandomFace():
    faces = Split.faces
    epsilonArea = 0.01
    dist = []
    sum = 0
    for face in faces:
        if (not face.bounded) or (face.area < epsilonArea):
            dist += [0]
        else:
            dist += [face.area]
            sum += face.area
    for i in range(len(faces)): 
        dist[i] /= sum
    return np.random.choice(faces, p=dist)

def ChooseRandomAction(face):
    if DontSplitVV(face):
       return np.random.choice(range(1,9),                       
                             p=[0.11,0.61,0.07,0.00,0.07,0.07,0.07,0.00])
# with cycles                p=[0.10,0.60,0.05,0.05,0.05,0.05,0.05,0.05])
    else:
       return np.random.choice(range(0,9), 
                            p=[0.06,0.11,0.62,0.06,0.00,0.05,0.05,0.05,0.00])
# with cycles               p=[0.05,0.10,0.60,0.05,0.04,0.04,0.04,0.04,0.04])
# uniform probability       p = [1/7,1/7,1/7,1/7,0,1/7,1/7,1/7,0])
def DontSplitVV(face):
    return len(Split.faces) < 5 or len(face.edges) < 4 

def RandomlySplitVV(face):
    global numTries
    k = len(face.edges)
    if k==3:
       return False
    for q in range(numTries):
        i = np.random.choice(k)
        j = i + np.random.choice(range(2,k-1))
        if j > k:
            j-=k
        if Split.SplitFaceVV(face,face.vertices[i],face.vertices[j]):
           return True
    return False

    
def RandomlySplitVE(face):
    global numTries
    k = len(face.edges)
    for q in range(numTries):
        i = np.random.choice(k)
        e = face.edges[i]
        if not SplitableEdge(e):
            continue
        j = i + np.random.choice(range(2,k-1))
        if j > k:
            j-=k
        print("i=",i," j=",j,"k= ",k)
        p = RandomPointOnEdge(e)
        if Split.SplitFaceVE(face,face.vertices[j],e,p):
           return True
    return False


def RandomlySplitEE(face):
    global numTries
    k = len(face.edges)
    for q in range(numTries):
        i,j = np.random.choice(k,size=2,replace=False)
        ei = face.edges[i]
        if not SplitableEdge(ei):
           continue
        ej = face.edges[j]
        if not SplitableEdge(ej):
            continue
        pi = RandomPointOnEdge(ei)
        pj = RandomPointOnEdge(ej)
        if Split.SplitFaceEE(face,ei,pi,ej,pj):
            return True
    return False

def RandomlySplitVVPath(face):
    global numTries
    k = len(face.edges)
    for q in range(numTries):
        i = np.random.choice(k)
        j = i + np.random.choice(range(1,k))
        if j > k:
            j-=k
        va = face.vertices[i]
        vb = face.vertices[j]
        path = RandomPath(face,va.p,vb.p)
        if Split.SplitFaceVVPath(face,va,vb,path):
            return True
    return False

def RandomlySplitVCycle(face):
    global numTries
    k = len(face.edges)
    for q in range(numTries):
        i = np.random.choice(k)
        v = face.vertices[i]
        path = RandomCycle(face,v.p)
        if Split.SplitFaceVCycle(face,v,path):
            return True
    return False


def RandomlySplitVEPath(face):
    global numTries
    k = len(face.edges)
    for q in range(numTries):
        i,j = np.random.choice(k,size=2,replace=True)
        v = face.vertices[i]
        e = face.edges[j]
        if not SplitableEdge(e):
            continue
        p = RandomPointOnEdge(e)
        path = RandomPath(face,v.p,p)
        if Split.SplitFaceVEPath(face,v,e,p,path):
           return True
    return False
        
def RandomlySplitEEPath(face):
    global numTries
    k = len(face.edges)
    for q in range(numTries):
        i,j = np.random.choice(k,size=2, replace=False)
        ea=face.edges[i]
        eb=face.edges[j]
        if not (SplitableEdge(ea) and SplitableEdge(eb)):
            continue
        pa = RandomPointOnEdge(ea)
        pb = RandomPointOnEdge(eb)
        path = RandomPath(face,pa,pb)
        if Split.SplitFaceEEPath(face,ea,eb,pa,pb,path):
           return True
    return False
           

def RandomlySplitSameEdgePath(face):
    global numTries, epsilon
    k = len(face.edges)
    for q in range(numTries):
        i = np.random.choice(k)
        e = face.edges[i]
        if not TwiceSplitableEdge(e):
            continue
        while True:
            pa = RandomPointOnEdge(e)
            pb = RandomPointOnEdge(e)
            if Graph.vecDist(pa,pb) > epsilon:
                break
        path = RandomPath(face,pa,pb)
        if Split.SplitFaceSameEdgePath(face,e,pa,pb,path):
            return True
    return False

def RandomlySameEdgeCycle(face):
    global numTries
    k = len(face.edges)
    for q in range(numTries):
        i = np.random.choice(k)
        e = face.edges[i]
        if not SplitableEdge(e):
            continue
        pa=RandomPointOnEdge(e)
        path = RandomCycle(face,pa)    
        if Split.SplitFaceSameEdgeCycle(face,e,pa,path):
            return True
    return False

def RandomPointOnEdge(edge):
    global epsilon
    while True:
        t = np.random.normal(loc = 0.5, scale=0.20)
        print(t)
        if 0.05 < t and t < 0.95:
            return Graph.Vector(t*edge.tail.p.x + (1-t)*edge.head.p.x,
                                t*edge.tail.p.y + (1-t)*edge.head.p.y)
            
          

def SplitableEdge(e):
    global epsilon
    return Graph.edgeLength(e) > 2*epsilon

def TwiceSplitableEdge(e):
    global epsilon
    return Graph.edgeLength(e) > 4*epsilon


def RandomPath(face,va,vb):
     k = np.random.choice([1,2], p=[2/3,1/3])
     path = []
     for i in range(k):
         path = path + [Graph.randomPointInFace(face,False)]
     return path

   
def RandomCycle(face,v):
     k = np.random.choice([2,3], p=[2/3,1/3])
     path = []
     for i in range(k):
         path = path + [Graph.randomPointInFace(face,False)]
     return path

