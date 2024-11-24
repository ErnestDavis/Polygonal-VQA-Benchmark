import numpy
import Graph
import Frame
import GraphCheck
import DrawGraph
import FinalizeFaces

global debug 
debug = True

def SplitFaceVV(face,va,vb):
    global faces, edges, debug
    if debug:
       debugShow("SplitFaceVV", face, [va,vb], [], [], [])        
    eea = Graph.ArcsAtVertexInFace(va,face)  
    eeb = Graph.ArcsAtVertexInFace(vb,face)
    if (SplitAtVAngleTooSmall(va.p,vb,eeb) or 
           SplitAtVAngleTooSmall(vb.p,va,eea)):
        return False
    if TrueEdgesCollide(eea,eeb):
        return False
    ee = eea + eeb
    if not(face.convex) and not(Graph.InteriorEdge(va.p,vb.p,face,ee)):
        return False
    ef = Graph.Edge(va,vb,True)
    er = ef.reverse
    face1 = InsertFace(face,va,vb,[er])
    face2 = InsertFace(face,vb,va,[ef])
    for v in face.vertices:
        SetVertexFaces(v)
    faces.remove(face) 
    faces += [face1,face2]
    edges += [ef,er]
    if debug:
        print("Success\n")
    return True


def SplitFaceVE(face,v,e,p):
    global vertices, edges, faces
    if debug:
       debugShow("SplitFaceVE", face, [v], [e], [p], [])  
    eea = Graph.ArcsAtVertexInFace(v,face) 
    if (SplitAtVAngleTooSmall(p,v,eea) or SplitAtEAngleTooSmall(v.p,p,e)):
       return False
    if TrueEdgesCollide(eea,[e]):
        return False;
    ee = eea + [e]
    if (not(face.convex) and not(Graph.InteriorEdge(v.p,p,face,ee))):
         return False
    if Graph.tooClose(p,e.tail.p) or Graph.tooClose(p,e.head.p):
        return False
    vNew = Graph.Vertex(p)
    [e1,e2] = SplitEdge(e,[vNew])
    ex = Graph.Edge(v,vNew,True)
    face1 = InsertFace(face,e.head,v,[ex,e2])
    face2 = InsertFace(face,v,e.tail,[e1,ex.reverse])
    e.tail.outarcs.remove(e)
    e.head.outarcs.remove(e.reverse)
    SplitEdgeOfFlip(e,[e2.reverse,e1.reverse])
    for v in face.vertices + [vNew]:
        SetVertexFaces(v)
    vertices += [vNew]
    faces.remove(face)
    faces += [face1,face2]
    FixEdges([e],[e1,e2,ex])
    if debug:
        print("Success\n")
    return True

def SplitFaceEE(face,ea,pa,eb,pb):
    global vertices, edges, faces
    if debug:
       debugShow("SplitFaceEE", face, [], [ea,eb], [pa,pb], []) 
    if ea.trueEdge == eb.trueEdge:
        return False
    if (SplitAtEAngleTooSmall(pb,pa,ea) or SplitAtEAngleTooSmall(pa,pb,eb)):
       return False
    if (not(face.convex) and not(Graph.InteriorEdge(pa,pb,face,[ea,eb]))):
        return False
    if (Graph.tooClose(pa,ea.tail.p) or Graph.tooClose(pa,ea.head.p) or 
        Graph.tooClose(pb,eb.tail.p) or Graph.tooClose(pb,eb.head.p)):
        return False
    va = Graph.Vertex(pa)
    vb = Graph.Vertex(pb)
    ec = Graph.Edge(va,vb,True)
    ecx = ec.reverse
    [ea1,ea2] = SplitEdge(ea,[va])
    [eb1,eb2] = SplitEdge(eb,[vb])
    face1 = InsertFace(face,ea.head,eb.tail,[eb1,ecx,ea2])
    face2 = InsertFace(face,eb.head,ea.tail,[ea1,ec,eb2])
    ea.tail.outarcs.remove(ea)
    ea.head.outarcs.remove(ea.reverse)
    eb.tail.outarcs.remove(eb)
    eb.head.outarcs.remove(eb.reverse)
    SplitEdgeOfFlip(ea,[ea2.reverse,ea1.reverse])
    SplitEdgeOfFlip(eb,[eb2.reverse,eb1.reverse])
    for v in face.vertices + [va,vb]:
        SetVertexFaces(v)
    vertices += [va,vb]
    faces.remove(face)
    faces += [face1,face2]
    FixEdges([ea,eb],[ea1,ea2,eb1,eb2,ec])
    if debug:
       print("Success\n")
    return True

def SplitFaceVVPath(face,va,vb,path):
    global vertices, faces, edges
    if debug:
       debugShow("SplitFaceVVPath", face, [va,vb], [], [], path) 
    eea = Graph.ArcsAtVertexInFace(va,face)  
    eeb = Graph.ArcsAtVertexInFace(vb,face)  
    if (SplitAtVAngleTooSmall(path[0],va,eea) or SplitAtVAngleTooSmall(path[-1],vb,eeb)
        or SplitAtPathAngleTooSmall([va.p]+path+[vb.p], False)):
       return False
    if not(Graph.InteriorPath(face,va.p,vb.p,path,eea,eeb)):
        return False
    if Graph.PathSelfCrossing([va.p]+path+[vb.p], va==vb):
        return False
    if (vb == va):
       return False
    v1 = va
    newVVS = []
    newEdges = []
    newRevEdges = []
    for p in path:
        v2 = Graph.Vertex(p)
        newVVS += [v2]
        newEdge = Graph.Edge(v1,v2,True) 
        newEdges += [newEdge]
        newRevEdges = [newEdge.reverse]+ newRevEdges
        v1 = v2
    newEdge = Graph.Edge(v1,vb,True) 
    newEdges += [newEdge]
    newRevEdges = [newEdge.reverse]+ newRevEdges
    face1 = InsertFace(face,va,vb,newRevEdges)
    face2 = InsertFace(face,vb,va,newEdges)
#   for e in newEdges:
#       Graph.ShowEdge(e)
#    Graph.ShowFace(face1)
#    Graph.ShowFace(face2)
    for v in face.vertices + newVVS:
        SetVertexFaces(v)
    vertices +=  newVVS
    edges = edges + newEdges + newRevEdges 
    faces.remove(face) 
    faces += [face1,face2]
    if debug:
        print("Success\n")
    return True

def SplitFaceVCycle(face,va,path):
    global vertices, faces, edges
    if debug:
       debugShow("SplitFaceVCycle", face, [va], [], [], path) 
    eea = Graph.ArcsAtVertexInFace(va,face)  
    if (SplitAtVAngleTooSmall(path[0],va,eea) or SplitAtVAngleTooSmall(path[-1],va,eea)
        or SplitAtPathAngleTooSmall([va.p]+path+[va.p],True)):
       return False
    if not(Graph.InteriorPath(face,va.p,va.p,path,eea,eea)):
        return False
#   print("Passed InteriorPath")
    if Graph.PathSelfCrossing([va.p]+path+[va.p], True):
        return False
#   print("Passed SelfCrossing")
    newVVS = []
    newEdges = []
    newRevEdges = []
    if not(Graph.PathCounterClockwise(va.p,path)):
        path.reverse()
    v1 = va
    for p in path:
        v2 = Graph.Vertex(p)
        newVVS += [v2]
        newEdge = Graph.Edge(v1,v2,True) 
        newEdges += [newEdge]
        newRevEdges = [newEdge.reverse]+newRevEdges
        v1 = v2
    newEdge = Graph.Edge(v1,va,True) 
    newEdges += [newEdge]
    newRevEdges = [newEdge.reverse]+ newRevEdges
    face1 = BuildNewFaceFromEdges(newEdges)
    face2 = BuildNewFaceFromEdges(newRevEdges+FaceCycleEdgesFrom(face,va))
#   for e in newEdges:
#       Graph.ShowEdge(e)
#    Graph.ShowFace(face1)
#    Graph.ShowFace(face2)
    for v in face.vertices + newVVS:
        SetVertexFaces(v)
    vertices +=  newVVS
    edges = edges + newEdges + newRevEdges 
    faces.remove(face) 
    faces += [face1,face2]
    if debug:
        print("Success\n")
    return True

def SplitFaceVEPath(face,va,eb,pb,path):
    global vertices, faces, edges
    if debug:
       debugShow("SplitFaceVEPath", face, [va], [eb], [pb], path) 
    eea = Graph.ArcsAtVertexInFace(va,face)  
    if (SplitAtVAngleTooSmall(path[0],va,eea) or SplitAtEAngleTooSmall(path[-1],pb,eb)
        or SplitAtPathAngleTooSmall([va.p]+path+[pb],False)):
       return False
    if not(Graph.InteriorPath(face,va.p,pb,path,eea,[eb])):
        return False
    if Graph.PathSelfCrossing([va.p]+path+[pb], False):
        return False
    v1 = va
    newVVS = []
    newEdges = []
    newRevEdges = []
    for p in path+[pb]:
        v2 = Graph.Vertex(p)
        newVVS += [v2]
        newEdge = Graph.Edge(v1,v2,True) 
        newEdges += [newEdge]
        newRevEdges = [newEdge.reverse]+ newRevEdges
        v1 = v2
    vNew = v2
    [e1,e2] = SplitEdge(eb,[vNew])
    newEdges += [e2]
    newRevEdges = [e1]+ newRevEdges
    face1 = InsertFace(face,eb.head,va,newEdges)
    face2 = InsertFace(face,va,eb.tail,newRevEdges)
    eb.tail.outarcs.remove(eb)
    eb.head.outarcs.remove(eb.reverse)
    SplitEdgeOfFlip(eb,[e2.reverse,e1.reverse])
    FixEdges([eb],[e1,e2]+newEdges)
#   for e in newEdges:
#       Graph.ShowEdge(e)
#    Graph.ShowFace(face1)
#    Graph.ShowFace(face2)
    for v in face.vertices + newVVS:
        SetVertexFaces(v)
    vertices +=  newVVS
    faces.remove(face) 
    faces += [face1,face2]
    if debug:
        print("Success\n")
    return True

def SplitFaceEEPath(face,ea,eb,pa,pb,path):
    if debug:
       debugShow("SplitFaceEEPath", face, [], [ea,eb], [pa,pb], path) 
    global vertices, faces, edges
    if (SplitAtEAngleTooSmall(path[0],pa,ea) or SplitAtEAngleTooSmall(path[-1],pb,eb)
        or SplitAtPathAngleTooSmall([pa]+path+[pb],False)):
       return False
    if not(Graph.InteriorPath(face,pa,pb,path,[ea],[eb])):
        return False
    if Graph.PathSelfCrossing([pa]+path+[pb], False):
        return False
    va = Graph.Vertex(pa)
    v1 = va
    newVVS = [va]
    newEdges = []
    newRevEdges = []
    for p in path+[pb]:
        v2 = Graph.Vertex(p)
        newVVS += [v2]
        newEdge = Graph.Edge(v1,v2,True) 
        newEdges += [newEdge]
        newRevEdges = [newEdge.reverse]+ newRevEdges
        v1 = v2
    vb = v2
    [ea1,ea2] = SplitEdge(ea,[va])
    [eb1,eb2] = SplitEdge(eb,[vb])
    newEdges = [ea1] + newEdges + [eb2]
    newRevEdges = [eb1] + newRevEdges + [ea2]
    face1 = InsertFace(face,eb.head,ea.tail,newEdges)
    face2 = InsertFace(face,ea.head,eb.tail,newRevEdges)
    ea.tail.outarcs.remove(ea)
    ea.head.outarcs.remove(ea.reverse)
    eb.tail.outarcs.remove(eb)
    eb.head.outarcs.remove(eb.reverse)
    SplitEdgeOfFlip(ea,[ea2.reverse,ea1.reverse])
    SplitEdgeOfFlip(eb,[eb2.reverse,eb1.reverse])
    FixEdges([ea,eb],newEdges+[eb1,ea2])
    for v in face.vertices + newVVS:
        SetVertexFaces(v)
    vertices +=  newVVS
    faces.remove(face) 
    faces += [face1,face2]
    if debug:
        print("Success\n")
    return True

def SplitFaceSameEdgePath(face,e,pa,pb,path):
    global vertices, faces, edges
    if debug:
       debugShow("SplitFaceSameEdgePath", face, [], [e], [pa,pb], path) 
    if abs(Graph.signedAngle(pb,pa,e.head.p)) > 0.01:
        (pa,pb) = (pb,pa)      
        path.reverse()
    if (SplitAtEAngleTooSmall(path[0],pa,e) or SplitAtEAngleTooSmall(path[-1],pb,e)
        or SplitAtPathAngleTooSmall([pa]+path+[pb],False)):
       return False
    if not(Graph.InteriorPath(face,pa,pb,path,[e],[e])):
        print("Failed")
        return False
    if Graph.PathSelfCrossing([pa]+path+[pb], False):
        return False
    va = Graph.Vertex(pa)
    v1 = va
    newVVS = [va]
    newEdges = []
    newRevEdges = []
    for p in path+[pb]:
        v2 = Graph.Vertex(p)
        newVVS += [v2]
        newEdge = Graph.Edge(v1,v2,True) 
        newEdges += [newEdge]
        newRevEdges = [newEdge.reverse]+ newRevEdges
        v1 = v2
    vb = v2
    [e1,e2,e3]  = SplitEdge(e,[va,vb])
    newEdges = [e1] + newEdges + [e3]
    newRevEdges += [e2] 
    face1 = InsertFace(face,e.head,e.tail,newEdges)
    face2 = BuildNewFaceFromEdges(newRevEdges)
    e.tail.outarcs.remove(e)
    e.head.outarcs.remove(e.reverse)
    SplitEdgeOfFlip(e,[e3.reverse,e2.reverse,e1.reverse])
    FixEdges([e],[e2]+newEdges)
    for v in face.vertices + newVVS:
        SetVertexFaces(v)
    vertices +=  newVVS
    faces.remove(face) 
    faces += [face1,face2]
    if debug:
        print("Success\n")
    return True

def SplitFaceSameEdgeCycle(face,e,pa,path):
    global vertices, faces, edges
    if debug:
       debugShow("SplitFaceEECyc", face, [], [e], [pa], path) 
    if (SplitAtEAngleTooSmall(path[0],pa,e) or SplitAtEAngleTooSmall(path[-1],pa,e)
           or SplitAtPathAngleTooSmall([pa]+path+[pa],True)):
         return False
    if not(Graph.InteriorPath(face,pa,pa,path,[e],[e])):
        return False
    if Graph.PathSelfCrossing([pa]+path+[pa], True):
        return False
    if not(Graph.PathCounterClockwise(pa,path)):
        path.reverse()
    va = Graph.Vertex(pa)
    v1 = va
    newVVS = [va]
    newEdges = []
    newRevEdges = []
    for p in path:
        v2 = Graph.Vertex(p)
        newVVS += [v2]
        newEdge = Graph.Edge(v1,v2,True) 
        newEdges += [newEdge]
        newRevEdges = [newEdge.reverse]+ newRevEdges
        v1 = v2
    eLast = Graph.Edge(v1,va,True) 
    newEdges += [eLast]
    newRevEdges = [eLast.reverse] + newRevEdges
    [e1,e2] = SplitEdge(e,[va])
    newRevEdges = [e1] + newRevEdges + [e2]
    face1 = InsertFace(face,e.head,e.tail,newRevEdges)
    face2 = BuildNewFaceFromEdges(newEdges)
    e.tail.outarcs.remove(e)
    e.head.outarcs.remove(e.reverse)
    SplitEdgeOfFlip(e,[e2.reverse,e1.reverse])
    FixEdges([e],[e1,e2]+newEdges)
    for v in face.vertices + newVVS:
        SetVertexFaces(v)
    vertices +=  newVVS
    faces.remove(face) 
    faces += [face1,face2]
    if debug:
        print("Success\n")
    return True

def TrueEdgesCollide(eea,eeb):
    for ea in eea:
        for eb in eeb:
            if ea.trueEdge == eb.trueEdge:
                return True
    return False

def SplitAtVAngleTooSmall(p,v,ee):
    return (Graph.AngleTooSmall(p,v.p,ee[0].head.p) or 
            Graph.AngleTooSmall(p,v.p,ee[1].tail.p)) 

def SplitAtEAngleTooSmall(pa,pb,e):
    return (Graph.AngleTooSmall(pa,pb,e.head.p) or 
            Graph.AngleTooSmall(pa,pb,e.tail.p))

def SplitAtPathAngleTooSmall(path,cycle):
    for i in range(len(path)-2):
        if Graph.AngleTooSmall(path[i],path[i+1],path[i+2]):
            return True
        if cycle and Graph.AngleTooSmall(path[-2],path[0],path[1]):
            return True
    return False

def InsertFace(face,v1,v2,ee):
#    print("\nInsertFace")
#    Graph.ShowVertex(v1)
#    Graph.ShowVertex(v2)
#    for e in ee:
#        Graph.ShowEdge(e)
    newee = NewEdgesForFace(face,v1,v2,ee)
    newFace = BuildNewFaceFromEdges(newee)
#   Graph.ShowFace(newFace)
    return newFace

def NewEdgesForFace(face,v1,v2,newee):
    facevv = face.vertices
    i = facevv.index(v1)
    j = facevv.index(v2)
    if i <= j:
       ee = face.edges[i:j]
    else:
       ee = face.edges[i:len(face.edges)] + face.edges[0:j]
    return ee+newee

def FaceCycleEdgesFrom(face,v):
    i = face.vertices.index(v)
    return face.edges[i:len(face.edges)]+face.edges[0:i]

def BuildNewFaceFromEdges(newee):
    newFace = Graph.Face(newee,True)
    for ea in newee:
        ea.leftFace = newFace
    return newFace

def SplitEdge(e,newVVS):
     vvs = [e.tail] + newVVS + [e.head]
     er = e.reverse
     newEdges = []
     for i in range(len(vvs)-1):
         newEdge = Graph.Edge(vvs[i], vvs[i+1], True)
         newEdge.trueEdge = e.trueEdge
         newEdges  += [newEdge]
         newEdge.reverse.trueEdge = er.trueEdge
     return newEdges

def SplitEdgeOfFlip(e,newEdges):
    ex = e.reverse
    flip = ex.leftFace
    i = flip.edges.index(ex)
    flip.edges.remove(ex)
    for en in newEdges:
        flip.edges.insert(i,en)
        i += 1
        en.leftFace=flip
    flip.vertices = Graph.getVertices(flip.edges)
       

def SetVertexFaces(v):
    v.outarcs = sorted(v.outarcs, key = lambda e: e.direction)
    v.faces = []
    for ex in v.outarcs:
        v.faces += [ex.leftFace]

def FixEdges(edgesRemove,edgesAdd):
    global edges
    for e in edgesRemove:
        edges.remove(e)
        edges.remove(e.reverse)
    for e in edgesAdd:
        edges += [e,e.reverse]



def ShowMap(IncludeEdges):
    global vertices,edges,faces
    if IncludeEdges:
       Graph.ShowMap(vertices,edges,faces)
    else:
       Graph.ShowMap(vertices,[],faces)

def GC():
    global vertices,edges,faces
    return GraphCheck.GraphCheck(vertices,edges,faces)
   
def test1():
    global vertices,edges,faces
    vertices, edges, faces = Frame.makeFrame(1,1)
    frame = faces[1]
    va = frame.vertices[0]
    vb = frame.vertices[2]
    SplitFaceVV(frame,va,vb)
    faces = FinalizeFaces.FinalizeFaces(vertices,edges,faces)
#   Graph.ShowMap(vertices,edges,faces)
    DrawGraph.DrawGraph(faces,1,1)

def test2():
    global vertices,edges,faces
    vertices, edges, faces = Frame.makeFrame(1,1)
    frame = faces[1]
    va = frame.vertices[0]
    eb = frame.vertices[1].outarcs[0]
    SplitFaceVE(frame,va,eb,Graph.Vector(1,0.5))
    faces = FinalizeFaces.FinalizeFaces(vertices,edges,faces)
    DrawGraph.DrawGraph(faces,1,1)

def test3():
    global vertices,edges,faces
    vertices, edges, faces = Frame.makeFrame(1,1)
    frame = faces[1]
    va = frame.vertices[0]
    vb = frame.vertices[2]
    SplitFaceVV(frame,va,vb)
    va = vertices[1]
    eb = edges[9]
    face = faces[1]
    SplitFaceVE(face,va,eb,Graph.Vector(0.5,0.5))
    faces = FinalizeFaces.FinalizeFaces(vertices,edges,faces)
    DrawGraph.DrawGraph(faces,1,1)

def test4():
    global vertices,edges,faces
    vertices, edges, faces = Frame.makeFrame(1,1)
    frame = faces[1]
    pa =  Graph.Vector(0.5,0)
    pb =  Graph.Vector(0.5,1)
    ea = frame.edges[0]
    eb = frame.edges[2]
    SplitFaceEE(frame,ea,pa,eb,pb)
    faces = FinalizeFaces.FinalizeFaces(vertices,edges,faces)
    DrawGraph.DrawGraph(faces,1,1)

def test4A():
    global vertices,edges,faces
    vertices, edges, faces = Frame.makeFrame(1,1)
    frame = faces[1]
    pa =  Graph.Vector(0,0.5)
    pb =  Graph.Vector(1,0.5)
    ea = frame.edges[3]
    eb = frame.edges[1]
    SplitFaceEE(frame,ea,pa,eb,pb)
    faces = FinalizeFaces.FinalizeFaces(vertices,edges,faces)
    DrawGraph.DrawGraph(faces,1,1)

def test5():
    global vertices,edges,faces
    vertices, edges, faces = Frame.makeFrame(1,1)
    frame = faces[1]
    pa =  Graph.Vector(0.5,0)
    pb =  Graph.Vector(1,0.5)
    ea = frame.edges[0]
    eb = frame.edges[1]
    SplitFaceEE(frame,ea,pa,eb,pb)
    faces = FinalizeFaces.FinalizeFaces(vertices,edges,faces)
    DrawGraph.DrawGraph(faces,1,1)

def test6():
    global vertices,edges,faces
    vertices, edges, faces = Frame.makeFrame(1,1)
    frame = faces[1]
    pa =  Graph.Vector(0.5,0.5)
    SplitFaceVVPath(frame,vertices[0],vertices[1],[pa])
    faces = FinalizeFaces.FinalizeFaces(vertices,edges,faces)
    DrawGraph.DrawGraph(faces,1,1)

def test7():
    global vertices,edges,faces
    vertices, edges, faces = Frame.makeFrame(1,1)
    frame = faces[1]
    path = [ Graph.Vector(0.2,0.7),  Graph.Vector(0.7,0.2)]
    SplitFaceVVPath(frame,frame.vertices[0],frame.vertices[2],path)
    faces = FinalizeFaces.FinalizeFaces(vertices,edges,faces)
    DrawGraph.DrawGraph(faces,1,1)

def test8():
    global vertices,edges,faces
    vertices, edges, faces = Frame.makeFrame(1,1)
    frame = faces[1]
    path = [ Graph.Vector(0.2,0.7),  Graph.Vector(0.7,0.2)]
    SplitFaceVCycle(frame,frame.vertices[0],path)
    faces = FinalizeFaces.FinalizeFaces(vertices,edges,faces)
    DrawGraph.DrawGraph(faces,1,1)

def test9():
    global vertices,edges,faces
    vertices, edges, faces = Frame.makeFrame(1,1)
    frame = faces[1]
    path = [ Graph.Vector(0.2,0.7),  Graph.Vector(0.7,0.2)]
    pb =  Graph.Vector(1.0,0.5)
    eb = faces[1].edges[1]
    success = SplitFaceVEPath(frame,frame.vertices[0],eb,pb,path)
    if not success:
        return False
    faces = FinalizeFaces.FinalizeFaces(vertices,edges,faces)
    DrawGraph.DrawGraph(faces,1,1)

def test10():
    global vertices,edges,faces
    vertices, edges, faces = Frame.makeFrame(1,1)
    frame = faces[1]
    path = [ Graph.Vector(0.2,0.7),  Graph.Vector(0.7,0.2)]
    pb =  Graph.Vector(0.5,0.0)
    eb = faces[1].edges[0]
    success = SplitFaceVEPath(frame,frame.vertices[0],eb,pb,path)
    if not success:
        return False
    faces = FinalizeFaces.FinalizeFaces(vertices,edges,faces)
    DrawGraph.DrawGraph(faces,1,1)

def test11():
    global vertices,edges,faces
    vertices, edges, faces = Frame.makeFrame(1,1)
    frame = faces[1]
    path = [ Graph.Vector(0.2,0.7),  Graph.Vector(0.7,0.2)]
    pb =  Graph.Vector(0.5,0.0)
    eb = frame.edges[0]
    SplitFaceVEPath(frame,frame.vertices[1],eb,pb,path)
    faces = FinalizeFaces.FinalizeFaces(vertices,edges,faces)
    DrawGraph.DrawGraph(faces,1,1)

def test12():
    global vertices,edges,faces
    vertices, edges, faces = Frame.makeFrame(1,1)
    frame = faces[1]
    path = [ Graph.Vector(0.2,0.7),  Graph.Vector(0.7,0.2)]
    pa =  Graph.Vector(0.5,0.0)
    pb =  Graph.Vector(1.0,0.5)
    ea = frame.edges[0]
    eb = frame.edges[1]
    SplitFaceEEPath(frame,ea,eb,pa,pb,path)
    faces = FinalizeFaces.FinalizeFaces(vertices,edges,faces)
    DrawGraph.DrawGraph(faces,1,1)

def test12A():
    global vertices,edges,faces
    vertices, edges, faces = Frame.makeFrame(1,1)
    frame = faces[1]
    path = [ Graph.Vector(0.2,0.35)]
    pa =  Graph.Vector(0.0,0.31)
    pb =  Graph.Vector(1.0,0.85)
    ea = frame.edges[3]
    eb = frame.edges[1]
    SplitFaceEEPath(frame,ea,eb,pa,pb,path)
    faces = FinalizeFaces.FinalizeFaces(vertices,edges,faces)
    DrawGraph.DrawGraph(faces,1,1)

def test13():
    global vertices,edges,faces
    vertices, edges, faces = Frame.makeFrame(1,1)
    frame = faces[1]
    path = [ Graph.Vector(0.2,0.7),  Graph.Vector(0.7,0.2)]
    pa =  Graph.Vector(0.2,0.0)
    pb =  Graph.Vector(0.7,0.0)
    e = frame.edges[0]
    SplitFaceSameEdgePath(frame,e,pa,pb,path)
    faces = FinalizeFaces.FinalizeFaces(vertices,edges,faces)
    DrawGraph.DrawGraph(faces,1,1)

def test14():
    global vertices,edges,faces
    vertices, edges, faces = Frame.makeFrame(1,1)
    frame = faces[1]
    path = [ Graph.Vector(0.2,0.7),  Graph.Vector(0.7,0.2)]
    pa =  Graph.Vector(0.5,0.0)
    e = frame.edges[0]
    SplitFaceSameEdgeCycle(frame,e,pa,path)
    faces = FinalizeFaces.FinalizeFaces(vertices,edges,faces)
    DrawGraph.DrawGraph(faces,1,1)

def test2Fail1():
    global vertices,edges,faces
    vertices, edges, faces = Frame.makeFrame(1,1)
    frame = faces[1]
    va = frame.vertices[0]
    vb = frame.vertices[2]
    SplitFaceVV(frame,va,vb)
    va = vertices[1]
    eb = edges[9]
    face = faces[1]
    SplitFaceVE(face,va,eb, Graph.Vector(0.5,0.5))
    SplitFaceVV(face,vertices[0],vertices[2])

def test2Fail2():
    global vertices,edges,faces
    vertices, edges, faces = Frame.makeFrame(1,1)  
    frame = faces[1]
    va = frame.vertices[0]
    vb = frame.vertices[2]
    SplitFaceVV(frame,va,vb)
    va = vertices[1]
    eb = edges[9]
    face = faces[1]
    SplitFaceVE(face,va,eb, Graph.Vector(0.5,0.5))
    eb = edges[9]
    ec = edges[11]
    pb =  Graph.Vector(0.75,0.75)
    pc =  Graph.Vector(0.25,0.25)
    SplitFaceEE(face,eb,pb,ec,pc)

def testFail3():
    global vertices,edges,faces
    vertices, edges, faces = Frame.makeFrame(1,1) 
    return SplitFaceSameEdgeCycle(faces[1],edges[0],Graph.Vector(0.5,0), 
                             [Graph.Vector(0.5,0.2),Graph.Vector(0.51,0.19)])
    
def testFail4():
    global vertices,edges,faces
    vertices, edges, faces = Frame.makeFrame(1,1) 
    SplitFaceVCycle(faces[1],vertices[0], [Graph.Vector(0.4,0.2),Graph.Vector(0.2,0.4)])
    f = faces[2]
    return SplitFaceSameEdgeCycle(f,f.edges[3],Graph.Vector(0.41,0.0), 
                                 [Graph.Vector(0.41,0.4),Graph.Vector(0.7,0.7)])

def testFail5():
    global vertices,edges,faces
    vertices, edges, faces = Frame.makeFrame(1,1) 
    f = faces[1]
    SplitFaceSameEdgeCycle(f,f.edges[0],Graph.Vector(0.41,0.0), 
                                 [Graph.Vector(0.41,0.4),Graph.Vector(0.7,0.7)])
    return SplitFaceVCycle(faces[1],vertices[0], [Graph.Vector(0.4,0.2),Graph.Vector(0.2,0.4)])

def debugShow(splitType, face, vertices, edges, points, path):
    print(splitType)
    Graph.ShowFaceShort(face)
    if vertices != []:
        for v in vertices:
            print(str(v))
    if edges != []:
        for e in edges:
            print(str(e))
    if points != []:
        print("First point", points[0])
    if len(points) == 2:
        print("Second point", points[1])
    if path != []:
       print("Path:")
       for p in path:
            print(str(p))
    print("")

