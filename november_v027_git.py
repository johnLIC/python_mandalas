#!/usr/bin/python
# by John Patterson, yesthatjohn@hotmail.com
# multi-threaded animated mandala (or random image) maker.
# Runs in Python 2.7
# Run it like this on the command line:
# ./november_v027.py 0 90 0 1 1
#
# ./november_v027_git.py <startframe> <endframe> <display? 0 or 1> <save images? 0 or 1> <make animated gif? 0 or 1> 

#  args:
#  1) start frame, sys.argv[0]
#  2) end frame, sys.argv[1]
#  3) flag to display sys.argv[2]
#  4) flag to render sys.argv[3]
#  5) sys.argv[3] make animated gif 0/1

# to make images
from PIL import Image
import math
from math import sin,cos,radians,e,sqrt
import random
import sys
import os

# for multiprocessing
from functools import partial
import time
import multiprocessing
 

#####################################################


# the multiprocessing version of this seems very picky about data types.
def pixelCalc(q,r):
    random.seed(12.54 + q +r*r)
    qc = pow(q,1.03+.01*sin(radians(frame*8)))-pow(628,1.03+.01*sin(radians(frame*8)))
    rc = pow(r,1.03+.01*cos(radians(frame*8)))-pow(628,1.03+.01*cos(radians(frame*8)))

    dist = (qc*qc+rc*rc)/(314.*314.+628.*628.)  # distance from center of image to current pixel
    threshold = dist
    dist = pow(dist+.01, .25 +.05*cos(radians(frame*4)))
    dist = dist*(314*314 + 628*628)

    R =255.
    B=60.
    G=200.
    
    R = (1.3 - threshold*threshold)*max(0,220*(1.0-.00235*(q-26*sin(8*radians(.00001*rc*q*qc)))+.25*sin(radians(frame*4)))) # fake shading on red rings
    G = max(0, 15*(1.0-.0235*pow(4*(-.25+(q +dist*.1*sin(.03*radians(pow(dist,.5)+frame*4)))%3000/15000.0), 1)))  
    B = pow(.5*threshold,.5) * max(0,220*(.00002*pow((q-26*sin(8*radians(.00001*rc*q*qc+r)))+.5*sin(radians(frame*4)),2))) # fake shading on red rings         

    R = min(R,255)
    G = min(G,255)
    B = min(B,255)
    B_temp = B
    B = .7*B + .4*G
    G = .7*G + .4*B_temp *qc/314.
        
    if R < 30 and R > 10:
        R = (30-R)*(R-10)
        G = (30-R)*(R-10)*(q/628.)
        B = 255-.05*(30-R)*(R-10)
    if R < 50 and R > 40:
        R = 0
        G = 0
        B = 0
    if R < 70 and R > 60:
        #R = 0
        G = (70-R)*(R-60)*2.0
        B = 0
    if R < 180 and R > 110:
        #R = 0
        G = (120-R)*(R-110)*2.0
        B = 0
    if R < 5 and R > 1:    
        R = (5-R)*(R-1)*80
        G = (5-R)*(R-1)*80
        B = 0.

    if B > 0:
        B = sin(math.pi*B/255.) * 255.
    if B > 200:
        G = 255. * (1.0 - pow(.25*(B%25.), .950)) *qc/314.
        R = .002*G + 255. * (1.0 - pow(.25*(B%25.), 2.0))
        

    return ( int(R), int(G), int(B))  # return one pixel's color data tuple

# This gets called by the pool - each process does one row.
def imageMaker(q, r=1256):    
    for qtemp in range(0,20):
        if q*20+qtemp < 628:
            for r in range(1256):
                RGB.append(pixelCalc(q*20+qtemp,r))
    return RGB

        


# After the pool happens, put the data into an image format, and save and/or gificate the images
def image_array_munger(show, save, gif):
    RGB_flat = []
    for chunk in RGB:
        for elem in chunk:
            RGB_flat.append(elem)
    im = Image.new("RGB", (1256,628))
    im.putdata(RGB_flat)
    if show==1:
        print "showing frame " + str(frame)
        im.show()
    if save==1:
        print "saving " + str(frame)
        if not os.path.exists('render/'+sys.argv[0].split(".")[1] ):
            os.makedirs('render/'+sys.argv[0].split(".")[1] )
        im.save('render/'+sys.argv[0].split(".")[1] + "/" + sys.argv[0].split(".")[1] + "." + str(frame).zfill(4) + '.png')


#####################################################

frame_start = int(sys.argv[1])
frame_end = int(sys.argv[2])
if __name__=='__main__':
    start = time.clock()
    for frame in range(frame_start, frame_end):
        RGB = []  # I don't remember why we want RGB in array_munger
        pool = multiprocessing.Pool(processes=32)  # run 31 processes, so we don't double-write into RGB
        RGB = pool.map(imageMaker, range(0,32))  # run one process for each row in the image
        pool.close()  # "we are not adding any more threads" 
        pool.join()  # wait for all the threads, or maybe that's what the next line does.
        image_array_munger(int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))  # assemble image data array, argv[2] = show?, argv[3] = save?

    # make an animated gif
    if sys.argv[5] == "1":    
        input_path = "render" + sys.argv[0].split(".")[1]+"/"+sys.argv[0].split(".")[1] + ".*.png"
        if not os.path.exists('gif'):
            os.makedirs('gif')
        output_path = "gif" + sys.argv[0].split(".")[1] + ".gif"
        #  convert -delay 10 -loop 0 render/v08.*.png gif/v002_02.gif
        os.system("convert -delay 10 -loop 0 " + input_path + " " + output_path)


