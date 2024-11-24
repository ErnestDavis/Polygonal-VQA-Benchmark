import numpy as np
import Graph
from PIL import Image, ImageColor, ImageDraw, ImageFont

def InitColors():
    global colors, white, black
    black = (0,0,0)
    white = (255,255,255)
    red = (255,0,0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    yellow = (255, 255, 0)
    brown = (150, 75, 0)
    gray = (120,120,120)
    colors = [white, red, blue, green, yellow, brown, gray]


def DrawGraph(faces,maxX,maxY):
    global colors, white, black
    InitColors()
    img = Image.new("RGB", (200+800*maxX, 200+800*maxY), white)
    draw = ImageDraw.Draw(img)
    for face in faces:  
        if face.bounded:
#           Graph.ShowFace(face)
            vvs = FaceVertex2P(face)
            draw.polygon(vvs, fill=colors[face.color], outline=black, width=4)
            lp,d = Graph.LetterPointFace(face)
            (x,y) = V2P(lp)
            if d > 0.03:
                draw.text((x-20,y-20), face.letter, fill=black, font_size=40)
            else:
                draw.text((x-10,y-10), face.letter, fill=black, font_size=20)

    img.show()
    img.save("Attempt1.png")
        

def FaceVertex2P(face):
    vvs = (V2P(face.vertices[0].p),)
    for i in range(1,len(face.vertices)-1):
        vvs += (V2P(face.vertices[i].p),)
    return vvs

# Point to pixel
def V2P(v):
    return (np.floor(100+800*v.x), np.floor(900-800*v.y))