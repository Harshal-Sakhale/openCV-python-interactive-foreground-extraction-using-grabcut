#!/usr/bin/env python
'''
===============================================================================
Interactive Image Segmentation using GrabCut algorithm.

This sample shows interactive image segmentation using grabcut algorithm.

USAGE:
    python grabcut.py <filename>

README FIRST:
    Two windows will show up, one for input and one for output.

    At first, in input window, draw a rectangle around the object using the
left mouse button. Then press 'n' to segment the object (once or a few times)
For any finer touch-ups, you can press any of the keys below and draw lines on
the areas you want. Then again press 'n' to update the output.

Key '0' - To select areas of sure background
Key '1' - To select areas of sure foreground
Key '2' - To select areas of probable background
Key '3' - To select areas of probable foreground
Key 'x' - To change background color
Key 'd' - To decrease brush thickness (touchup curves)
Key 'i' - To increase brush thickness (touchup curves)
Key 'n' - To update the segmentation
Key 'r' - To reset the setup
Key 's' - To save the results
===============================================================================
'''

# Python 2/3 compatibility
from __future__ import print_function

import numpy as np
import cv2 as cv

import sys

class App():
    BLUE = [255,0,0]        # rectangle color
    RED = [0,0,255]         # PR BG
    GREEN = [0,255,0]       # PR FG
    BLACK = [0,0,0]         # sure BG
    WHITE = [255,255,255]   # sure FG
    YELLOW = [0,255,255] # ROI
    PINK = [255,0, 255]
    ORANGE= [0,165,255]     
    clist=[BLUE, RED, GREEN, BLACK, WHITE, YELLOW, PINK, ORANGE]

    DRAW_BG = {'color' : BLACK, 'val' : 0}
    DRAW_FG = {'color' : WHITE, 'val' : 1}
    DRAW_PR_BG = {'color' : RED, 'val' : 2}
    DRAW_PR_FG = {'color' : GREEN, 'val' : 3}

    # setting up flags
    rect = (0,0,1,1)
    drawing = False         # flag for drawing curves
    rectangle = False       # flag for drawing rect
    rect_over = False       # flag to check if rect drawn
    rect_or_mask = 100      # flag for selecting rect or mask mode
    value = DRAW_FG         # drawing initialized to FG
    thickness = 3           # brush thickness
    bgi=0
    bgcol=clist[bgi]
    rXo=0
    rYo=0

    def onmouse(self, event, x, y, flags, param):
        # Draw Rectangle
        if not self.rect_over:
          if event == cv.EVENT_LBUTTONDOWN:
              self.rectangle = True
              self.ix, self.iy = x,y
  
          elif event == cv.EVENT_MOUSEMOVE:
              if self.rectangle == True:
                  #self.img = self.img2.copy()
                  self.winS = self.winS0.copy()
                  #cv.rectangle(self.img, (self.ix, self.iy), (x, y), self.BLUE, 2)
                  cv.rectangle(self.winS, (self.ix, self.iy), (x, y), self.BLUE, 1)
                  #self.rect = (min(self.ix, x), min(self.iy, y), abs(self.ix - x), abs(self.iy - y))
                  self.rect = ( int(min(self.ix, x)/self.scale), int(min(self.iy, y)/self.scale), int(abs(self.ix - x)/self.scale), int(abs(self.iy - y)/self.scale))
                  self.rect_or_mask = 0
  
          elif event == cv.EVENT_LBUTTONUP:
              self.rectangle = False
              self.rect_over = True
            #  cv.rectangle(self.img, (self.ix, self.iy), (x, y), self.BLUE, 2)
              self.blr= (self.ix, self.iy), (x, y) # Blue rectangle
              cv.rectangle(self.winS, self.blr[0], self.blr[1], self.BLUE, 1)
              #self.rect = (min(self.ix, x), min(self.iy, y), abs(self.ix - x), abs(self.iy - y))
              self.rect = ( int(min(self.ix, x)/self.scale), int(min(self.iy, y)/self.scale), int(abs(self.ix - x)/self.scale), int(abs(self.iy - y)/self.scale))
              self.rect_or_mask = 0
              print(" Now press the key 'n' a few times until no further change \n")
        else:
            # POI selection (Yellow rectangle)
            if event == cv.EVENT_LBUTTONDOWN:
                self.winS=self.winS0.copy()
                cv.rectangle(self.winS, self.blr[0], self.blr[1], self.BLUE, 1)
                cv.rectangle(self.winS, (x-self.delta, y-self.delta), (x+self.delta, y+self.delta), self.YELLOW, 1)
                cv.circle(self.winS, (x,y), 5 , self.YELLOW, 2)
                self.poi=(int(x/self.scale),int(y/self.scale))
	
                # Top left point within the ROI		
                ptpy=self.poi[1]-self.HBSIZE
                ptpx=self.poi[0]-self.HBSIZE
                
		# Offsets into real image
                self.rXo = ptpx
                self.rYo = ptpy

                # input image win x indices
                ptix0=ptpx
                ptix1=ptpx+self.BSIZE
                ptiy0=ptpy
                ptiy1=ptpy+self.BSIZE
                
                # ROI image winP indices
                
                ptox0=0
                ptox1=self.BSIZE
                ptoy0=0
                ptoy1=self.BSIZE
                win=self.img
                if ptpx < 0 or ptpy < 0 or ptix1 > win.shape[1] or ptiy1  > win.shape[0]:
                        self.winP=self.winPC0.copy() # whole white
                        if ptpx < 0 :
                                ptox0=abs(ptpx)
                                ptix0=0
                                
                        if ptpy < 0 :
                                ptoy0=abs(ptpy)
                                ptiy0=0
                        
                        if ptix1 > win.shape[1] :
                                ptix1=win.shape[1]
                                ptox1=win.shape[1] - ptpx

                        if ptiy1 > win.shape[0] :
                                ptiy1 = win.shape[0]
                                ptoy1 = win.shape[0] - ptpy
                        
                self.winP[ptoy0:ptoy1,ptox0:ptox1,:]=win[ptiy0:ptiy1,ptix0:ptix1,:]
                #print(self.winP.shape)
                self.winP0=self.winP.copy()                








    def onmouse2(self, event, x, y, flags, param):
        # draw touchup curves
	
	# Real image co-ordinates from current co-ordinates

        ptValid = True
        rX=x+self.rXo
        rY=y+self.rYo

        if rX < 0 or rY < 0 or rX >= self.img.shape[1] or rY >= self.img.shape[0]:
            ptValid = False
        

        #print("rX = ",rX,", rY = ",rY)

        if event == cv.EVENT_LBUTTONDOWN:
           # if not ptValid:
           #     print("Invalid point") 

            if self.rect_over == False:
                print("first draw rectangle \n")
            else:
                self.drawing = True
                if ptValid:
                    cv.circle(self.winP, (x,y), self.thickness, self.value['color'], -1)
                    cv.circle(self.mask, (rX,rY), self.thickness, self.value['val'], -1)

        elif event == cv.EVENT_MOUSEMOVE:
            if self.drawing == True and ptValid:
                cv.circle(self.winP, (x, y), self.thickness, self.value['color'], -1)
                cv.circle(self.mask, (rX,rY), self.thickness, self.value['val'], -1)

        elif event == cv.EVENT_LBUTTONUP:
            if self.drawing == True:
                self.drawing = False
                if ptValid:
                    cv.circle(self.winP, (x, y), self.thickness, self.value['color'], -1)
                    cv.circle(self.mask, (rX,rY), self.thickness, self.value['val'], -1)





    def hfill(self,myimg):
        if myimg.shape[0] < self.BSIZE :
                band = np.zeros((self.BSIZE-myimg.shape[0],self.BSIZE,3),dtype=np.uint8)
                band.fill(255)
                myimg=np.vstack((myimg,band))
        return myimg

    def run(self):
        # Loading images
        if len(sys.argv) == 2:
            filename = sys.argv[1] # for drawing purposes
        else:
            filename = 'messi5.jpg'
            print("No input image given, so loading default image, %s \n" % (filename))
            print("Correct Usage: python grabcut.py <filename> \n")
           

        self.img = cv.imread(filename)
        self.img2 = self.img.copy()                               # a copy of original image

	# SQUARE BOX SIZE BSIZE x BSIZE
        self.BSIZE=400
        self.HBSIZE=int(self.BSIZE/2) # Half of box size
        
        self.scale=self.BSIZE/max(self.img.shape)

        self.delta=int(self.HBSIZE * self.scale) # delta +/- around poi

        self.winS=cv.resize(self.img,None,fx=self.scale,fy=self.scale)

        if self.winS.shape[0] < self.BSIZE :
                band = np.zeros((self.BSIZE-self.winS.shape[0],self.BSIZE,3),dtype=np.uint8)
                band.fill(255)
                self.winS=np.vstack((self.winS,band))
                
        self.winS0=self.winS.copy()
        
        # winP is 400x400 ROI
        self.winP = np.zeros((self.BSIZE,self.BSIZE,3),dtype=np.uint8)
        self.winP.fill(255)
        self.winP0=self.winP.copy()
        self.winPC0=self.winP.copy()# Reset Clear (White)

        self.mask = np.zeros(self.img.shape[:2], dtype = np.uint8) # mask initialized to PR_BG
        self.mask2 = np.zeros(self.img.shape[:2], dtype = np.uint8) # mask initialized to PR_BG
        self.output = np.zeros(self.img.shape, np.uint8)           # output image to be shown
        # input and output windows
        cv.namedWindow('Touchup curves')
        cv.namedWindow('input output')
        cv.setMouseCallback('Touchup curves', self.onmouse2)
        cv.setMouseCallback('input output', self.onmouse)

        print(" Instructions: \n")
        print(" Draw a rectangle around the object using left mouse button \n")

        while(1):

            outS=cv.resize(self.output,None,fx=self.scale,fy=self.scale)
            outS=self.hfill(outS)
            outP=np.hstack((self.winS,outS))
            cv.imshow('input output', outP)
            cv.imshow('Touchup curves', self.winP)
          
            k = cv.waitKey(1)

            # key bindings
            if k == 27 or k == ord('q'):         # esc or q to exit
                break
            elif k == ord('0'): # BG drawing
                print(" mark background regions with left mouse button \n")
                self.value = self.DRAW_BG
            elif k == ord('1'): # FG drawing
                print(" mark foreground regions with left mouse button \n")
                self.value = self.DRAW_FG
            elif k == ord('2'): # PR_BG drawing
                self.value = self.DRAW_PR_BG
            elif k == ord('3'): # PR_FG drawing
                self.value = self.DRAW_PR_FG
            elif k == ord('d'): # Decrease brush thickness
                if self.thickness != 1: # Dont decrease below 1
                    self.thickness -= 1
                print("Brush thickness =",self.thickness)
            elif k == ord('i'): # Increase brush thickness
                self.thickness += 1
                print("Brush thickness =",self.thickness)
            elif k == ord('x'): # Change background color
                if self.bgi < (len(self.clist)-1) :
                    self.bgi += 1
                else :
                    self.bgi = 0
                self.bgcol=self.clist[self.bgi]
            elif k == ord('s'): # save image
                bar = np.zeros((self.img.shape[0], 5, 3), np.uint8)
                res = np.hstack((self.img2, bar, self.img, bar, self.output))
                cv.imwrite('grabcut_output.png', res)
                cv.imwrite('foreground.png', self.output)
                cv.imwrite("foreground_BGT.png",np.dstack((self.output,self.mask2)))
                print(" Result saved as image \n")
            elif k == ord('r'): # reset everything
                print("resetting \n")
                self.rect = (0,0,1,1)
                self.drawing = False
                self.rectangle = False
                self.rect_or_mask = 100
                self.rect_over = False
                self.value = self.DRAW_FG
                self.img = self.img2.copy()
                self.mask = np.zeros(self.img.shape[:2], dtype = np.uint8) # mask initialized to PR_BG
                self.output = np.zeros(self.img.shape, np.uint8)           # output image to be shown
            elif k == ord('n'): # segment the image
                print(""" For finer touchups, mark foreground and background after pressing keys 0-3
                and again press 'n'\nApplying grabcut.....""",end='')
                try:
                    bgdmodel = np.zeros((1, 65), np.float64)
                    fgdmodel = np.zeros((1, 65), np.float64)
                    if (self.rect_or_mask == 0):         # grabcut with rect
                        cv.grabCut(self.img2, self.mask, self.rect, bgdmodel, fgdmodel, 1, cv.GC_INIT_WITH_RECT)
                        self.rect_or_mask = 1
                    elif (self.rect_or_mask == 1):       # grabcut with mask
                        cv.grabCut(self.img2, self.mask, self.rect, bgdmodel, fgdmodel, 1, cv.GC_INIT_WITH_MASK)
                except:
                    import traceback
                    traceback.print_exc()
                print("applied.")
            self.mask2 = np.where((self.mask==1) + (self.mask==3), 255, 0).astype('uint8')
            self.output = cv.bitwise_and(self.img2, self.img2, mask=self.mask2)
            self.output[self.mask2 == 0 ] = self.bgcol
            
            
        print('Done')


if __name__ == '__main__':
    print(__doc__)
    App().run()
    cv.destroyAllWindows()
