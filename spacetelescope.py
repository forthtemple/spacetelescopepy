
import re
import requests
import json
import platform
import math

# import tkinter module 
from tkinter import *        

# Following will import tkinter.ttk module and 
# automatically override all the widgets 
# which are present in tkinter module. 
from tkinter.ttk import *

from PIL import ImageTk, Image, ImageEnhance

import numpy as np

import urllib.request
import os
import csv

# convert declination +41° 16′ 9″ to decimal angle
def dectodeg(s):
  #s=re.sub(r'[^\+\- ,0-9]', '', s) #sub(r'\W+', '',position)
  clean=re.sub(r'[^\+ ,0-9]', '', s) #sub(r'\W+', '',position)
  d =  clean.split()
  if len(d)==2:
    d.append('0')
  val=float(d[0])+float(d[1])/60+float(d[2])/3600
  if s[0]=='-':
    return -val
  else:
    return val


# s= "06 40 34.8"    or "0h 42m 44s
# convert right ascension 0h 42m 44s to decimal angle
def ratodeg(s):
  #s = "06 40 34.8 10 04 22 06 41 11.6 10 02 24 06 40 50.9 10 01 43"
  clean=re.sub(r'[^\+ ,0-9.]', '', s) #sub(r'\W+', '',position)
  d = [float(i) for i in clean.split()] 
  if len(d)==2:
    d.append(0)
 
  # d = [6.0, 40.0, 34.8, 10.0, 4.0, 22.0, 6.0, 41.0, 11.6, 10.0, 2.0, 24.0, 6.0, 40.0, 50.9, 10.0, 1.0, 43.0]

  d2 = [d[i:i+3] for i in range(0, len(d), 3)]  
  # d2 = [[6.0, 40.0, 34.8], [10.0, 4.0, 22.0], [6.0, 41.0, 11.6], [10.0, 2.0, 24.0], [6.0, 40.0, 50.9], [10.0, 1.0, 43.0]]

  d3 = [(s/3600 + m/60 + h) * 15 for h,m,s in d2]

  d4 = [d3[i:i+2] for i in range(0, len(d3), 2)]

  val= d4[0][0]
  if s[0]=='-':
    return -val
  else:
    return val




#RA 0h 42m 44s | Dec +41° 16′ 9″ andromeda
positionx=10.598519410353974  #ra 
positiony=41.199680240566416  #dec 
fov=1.5

pixels=500

    
def getpic():
  global img
  global panel
  global fov
  global positionx
  global positiony
  global pixels
  global msg
  global largeimage
  
  position=str(positionx)+','+str(positiony)
  filename=position.replace(",","__").replace(" ","_")+'w'+str(fov)+".jpg"
  print("pos",position,filename)

  #filename=os.path.basename(paths[0])

  if (fov-0.4<=0):
    blend=0
  else:
    #make it blend faster when fov low and taper off as fov gets higher
    blend=(math.sqrt(fov-0))/(math.sqrt(40-0))
  print("blend",blend)
  #blend=1/fov
  if blend<0.9:
    if not os.path.exists("cache/"+filename):
      url="https://alasky.cds.unistra.fr/hips-image-services/hips2fits?hips=CDS/P/DSS2/color&width="+str(pixels)+"&height="+str(pixels)+"&fov="+str(fov)+"&projection=SIN&coordsys=icrs&rotation_angle=0.0&object="+position+"&format=jpg"  
      urllib.request.urlretrieve(url, "cache/"+filename)
 
      img = Image.open("cache/"+filename) #skv7680327858564.fits') #skv7684881361472.fits')
    else:
      img=Image.open("cache/"+filename)

  # blend the large nasa image with the unistra image
  if blend>0.25:
      left= 4096*(180-positionx)/360
      top=-(positiony -90)/180 *2048
      width=4096 *fov / 360 
      imglarge=largeimage.crop((left-width/2, top-width/2, left+width/2, top+width/2))
      #check if need to wrap
      #this is only doing wrapping left and right up and down but not in the corners!
      if left-width/2<0: # and top-width/2>=0 and left+width/2<4096 and top+width/2<2048:
        #if wrapping in x direction
        print("mergex")
        imglarge2=largeimage.crop((left-width/2+4096, top-width/2, 4096, top+width/2))
        w,h =imglarge.size
        imgmerge = Image.new("RGB",(w,h)) #, (250,250,250))
        imgmerge.paste(imglarge,(0,0))
        imgmerge.paste(imglarge2,(0,0))
        imglarge=imgmerge
 
      elif top-width/2<0 : # and top-width/2>=0 and left+width/2<4096 and top+width/2<2048:
        #if wrapping going up
        print("mergey")
        imglarge2=largeimage.crop((left-width/2, top-width/2+2048, left+width/2, 2048))
        w,h =imglarge.size
        imgmerge = Image.new("RGB",(w,h)) #, (250,250,250))
        imgmerge.paste(imglarge,(0,0))
        imgmerge.paste(imglarge2,(0,0))
        imglarge=imgmerge
      elif top+width/2>2048:
        #if wrapping going down
        print('mergey2')
        imglarge2=largeimage.crop((left-width/2, 0, left+width/2, top+width/2-2048))
        w,h =imglarge.size
        imgmerge = Image.new("RGB",(w,h)) #, (250,250,250))
        imgmerge.paste(imglarge,(0,0))
        imgmerge.paste(imglarge2,(0,int(h-(top+width/2-2048) )))
        imglarge=imgmerge

      imglarge=imglarge.resize((pixels,pixels), Image.Resampling.LANCZOS) #, Image.ANTIALIAS)
      imglarge = ImageEnhance.Brightness(imglarge) 
      imglarge=imglarge.enhance(2.0)

  if (blend>=0.9):
    img=imglarge
  elif (blend>0.25): 
    img=Image.blend(img.convert('RGB'), imglarge.convert('RGB'), blend)

  try:
    img = ImageTk.PhotoImage(img) #file='resulti.jpg')#result.png') #Image.open('result.png')) #pil_img) #pil_img) #)
    panel.configure(image=img)
    panel.image = img
    panel.update()
  except Exception as e:
    print("err",e)
  
  msg.set("RA: {:.3f}, Dec {:.3f} fov: {:.3f}  ".format(positionx, positiony, fov)) #a, b, c))position+" w"+str(width)+"h"+str(height))


# scale in blocks of 8 so dont have infinite number of images in cache
def rescalepos():
  global positionx
  global positiony
  global lookupfound

  positionx=round((positionx% 360)/(fov/8))*(fov/8) 
  if positiony>90:
    positiony-=180
  elif positiony<-90:    
    positiony+=180
  positiony=round((positiony)/(fov/8))*(fov/8) 
  lookupfound.set('') 

  
def zoomout():
  global fov
  if fov*1.5<200:
    fov*=1.5  
    rescalepos()
    getpic()  

def zoomin():
  global fov
  if fov/1.5>0.08:
    fov/=1.5  
    rescalepos()
    getpic()  


def left():
  global positionx
  global positiony
  global fov
  positionx+=fov/8
  rescalepos()
  getpic()  

def right():
  global positionx
  global positiony
  global fov
  positionx-=fov/8  
  rescalepos()
  getpic()  
  
def up():
  global positionx
  global positiony
  global fov
  positiony+=fov/8
  rescalepos()
  getpic()  
  
def down():
  global positionx
  global positiony
  global fov
  positiony-=fov/8
  rescalepos()
  getpic()  

def constellation():
    global largeimage
    global largeimageconstellation
    global largeimagenoconstellation
    if constellationvisible.get() == 1:
        print("Checkbutton is selected")
        largeimage=largeimageconstellation
    else:
        print("Checkbutton is deselected")
        largeimage=largeimagenoconstellation
    getpic()

def lookup():
    global searchvar
    global positionx
    global positiony
    global lookupfound
    if searchvar.get()!='':
      payload = {"name":{"v":searchvar.get()}}

      r = requests.post("https://ned.ipac.caltech.edu/srs/ObjectLookup", json=payload)
      lookupjson=json.loads(r.text)
      '''
      {
        "QueryTime": "Tue Feb 25 08:59:10 2025",
        "Copyright": "(C) 2025 California Institute of Technology",
        "Version": "2.1",
        "Supplied": "andromeda",
        "NameResolver": "NED-NNS",
        "Interpreted": {
            "Name": "Andromeda Galaxy"
        },
        "Preferred": {
            "Name": "MESSIER 031",
            "Position": {
                "RA": 10.684799,
                "Dec": 41.269076,
                "UncSemiMajor": 0,
                "UncSemiMinor": 0,
                "PosAngle": 0,
                "RefCode": "2016MNRAS.461.3443V"
            },
            "ObjType": {
            "Value": "G",
            "RefCode": null
            },
            "Redshift": {
            "Value": -0.000991,
            "Uncertainty": 0.000003,
            "RefCode": "2000UZC...C......0F",
            "QualityFlag": "SUN "
            }
        },
        "StatusCode": 100,
        "ResultCode": 3
       }
      ''' 
      if lookupjson['ResultCode']!=3:
        msg.set("Object '"+searchvar.get()+"' could not be found")
      else:
        print('response',lookupjson)

        print('response', lookupjson['Preferred']['Position']['RA'], lookupjson['Preferred']['Position']['Dec'])
        positionx=lookupjson['Preferred']['Position']['RA']
        positiony=lookupjson['Preferred']['Position']['Dec']
        rescalepos()
        lookupfound.set(lookupjson['Interpreted']['Name']) 
        getpic()
    else:
       msg.set("Please enter an object to lookup")
# Create Object
root = Tk() 
root.title("Telescope")

# Initialize tkinter window with dimensions 100x100             
root.geometry(str(pixels+200)+'x'+str(pixels+200)) #'600x500')     

myContainer1 = Frame(root)
myContainer1.pack()


myContainer2 = Frame(myContainer1)
myContainer2.pack()

btn = Button(myContainer2, text = '-', 
                command = zoomout) 

# Set the position of button on the top of window 
btn.pack(side = 'left')     
btn = Button(myContainer2, text = '+', 
                command = zoomin) 

# Set the position of button on the top of window 
btn.pack(side = 'left')     

btn = Button(myContainer2, text = '<', 
                command = left) 

# Set the position of button on the top of window 
btn.pack(side = 'left')     
btn = Button(myContainer2, text = '>', 
                command = right) 

# Set the position of button on the top of window 
btn.pack(side = 'left')     
btn = Button(myContainer2, text = '^', 
                command = up) 

# Set the position of button on the top of window 
btn.pack(side = 'left')     

btn = Button(myContainer2, text = 'v', 
                command = down) 

# Set the position of button on the top of window 
btn.pack(side = 'left')     

myContainer4 = Frame(myContainer1)
myContainer4.pack()

lookupfound = StringVar()
label = Label(myContainer4, textvariable=lookupfound,font='Helvetica 10 bold')#, bg = "green"\, bd = 100, fg = "white", font = "Castellar")  
label.pack(side = 'left')  

msg = StringVar()
label = Label(myContainer4, textvariable=msg)#, bg = "green"\, bd = 100, fg = "white", font = "Castellar")  
label.pack(side = 'left')  


myContainer3 = Frame(myContainer1)
myContainer3.pack()

label = Label(myContainer3, text="Object Search")  
label.pack(side = 'left')  
searchvar=StringVar()
searchedit = Entry(myContainer3,textvariable = searchvar) #, font=('calibre',10,'normal')) 
searchedit.insert(0, 'NGC 24'  )                       
searchedit.pack(side = 'left')

btn = Button(myContainer3, text = 'Search', 
                command = lookup) 

# Set the position of button on the top of window 
btn.pack(side = 'left')  

constellationvisible = IntVar()
checkbutton =  Checkbutton(myContainer3, text="Show constellations", variable=constellationvisible, 
                             onvalue=1, offvalue=0, command=constellation)
constellationvisible.set(1)                             
checkbutton.pack(side = 'left')  

largeimageconstellation = Image.open('starmap_2020_4kconst.png') #skv7684881361472.fits')
largeimagenoconstellation = Image.open('starmap_2020_4k.png') #skv7684881361472.fits')
largeimage=largeimageconstellation
#img = Image.open('deleteme.png') #starmap_2020_4k.exr')#png') #skv7684881361472.fits')

panel = Label(myContainer1) #, image = img)
panel.pack(side = "bottom", fill = "both") #, expand = "yes")

getpic()  
root.mainloop() 
