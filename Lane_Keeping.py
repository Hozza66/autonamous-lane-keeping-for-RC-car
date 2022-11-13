# Autonamous Lane Following Using Open CV
# Authur: Haoran Hong

#Import modules
import cv2  #OpenCV modules for image processing
import numpy as np  #NumPy module for scientific computing
import RPi.GPIO as GPIO #Rasberry Pi GPIO pins

#General setup:

#Naming GPIO pins
straight = 8
lightleft = 10
lightright = 12
hardleft = 16
hardright = 18

#Set input/output for GPIO pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(straight, GPIO.OUT)
GPIO.setup(lightleft, GPIO.OUT)
GPIO.setup(lightright, GPIO.OUT)
GPIO.setup(hardleft, GPIO.OUT)
GPIO.setup(hardright, GPIO.OUT)

cap = cv2.VideoCapture('road.avi') #video capture

leftpos = 165   # initial value for left centre
rightpos = 475  #initial value for right centre

#Values for each of the sub limit region
lg1 = 140   #example lg1 = left green 1
lg2 = 190   #left = the left limit region
rg1 = 450   #green = the green sub-region
rg2 = 500   #numbers 1 = left sub-region minimum
la1 = 115   #2 = left sub-region maximum
la2 = 140   #3 = right sub-region minimum
la3 = 190   #4 = right sub-region maximum
la4 = 215
ra1 = 425
ra2 = 450
ra3 = 500
ra4 = 525
lr1 = 90
lr2 = 115
lr3 = 215
lr4 = 240
rr1 = 400
rr2 = 425
rr3 = 525
rr4 = 550

#Coordinates of text
txtpos = (450,70)
txtpos2 = (250,250)
txtpos3 = (240,250)

#Text colours and font
txtcolor = (147,20,255)
green = (0,255,0)
amber = (0,165,255)
red = (0,0,255)
font = cv2.FONT_HERSHEY_SIMPLEX

#Function for Image processing
def image_process ():

    global roi
    global frame

    ret, frame = cap.read() #obtaining single frame from video
    grey = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)   #covert image to greyscale
    edge = cv2.Canny(grey, 300, 200, 3) #canny edge detection
    edge[340:360, 0:1000]= 0    #set top half of image black
    #Algorithm for trapezoid ROI
    height = frame.shape[0]
    width = frame.shape [1]
    vert = np.array ([[[3*width/4, 3*height/5],
                       [width/4,3*height/5],
                       [40, height],
                       [width - 0, height]]], dtype=np.int32)
    
    roi = region_of_interest(edge, vert)    #set ROI on image

#Function for ROI
def region_of_interest (frame, vert):

    mask = np.zeros_like(frame) # create blank mask
    #mask color fill for channel 3 or 1
    if len(frame.shape)>2:
        channel_count = frame.shape[3]
        ignore_mask_color = (255,) * channel_count
    else:
        ignore_mask_color = 255
    #fill color for defined polygon
    cv2.fillPoly(mask, vert, ignore_mask_color)
    #return image with mask pixels nonzero
    masked_frame = cv2.bitwise_and(frame, mask)
    return masked_frame
                                
#Function for line intersection point
def line_intersection(line1, line2):
    #Algorithm for line intersection
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1]) 

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    #Return for x coordinates outside of limit region
    if x > 240 or x <90:
       if x > 550 or x <400:
            x=0
            cv2.putText(frame,'No Lane',txtpos, font, 1,red,2,cv2.LINE_AA)
    return x, y

#Function for lane tracking
def tracking ():
    global rightpos
    global leftpos
    global turn
    global txtbg

    #Probalistic Hough Transform function
    lines = cv2.HoughLinesP(roi,1,np.pi/180,30,minLineLength=10,maxLineGap=100)
    
    #Output coordinates for lines detected
    for x1,y1,x2,y2 in lines[:,0]:
        cv2.line(frame,(x1,y1),(x2,y2),(255,191,0),1, cv2.LINE_AA)

    #Draw on screen lines representing left and right limit regions
    cv2.line(frame,(90,270),(240,270),(147,20,255),1, cv2.LINE_AA)
    cv2.line(frame,(400,270),(550,270),(147,20,255),1 , cv2.LINE_AA)
    cv2.line(frame,(90,260),(90,280),(147,20,255),1, cv2.LINE_AA)
    cv2.line(frame,(240,260),(240,280),(147,20,255),1 , cv2.LINE_AA)
    cv2.line(frame,(400,260),(400,280),(147,20,255),1, cv2.LINE_AA)
    cv2.line(frame,(550,260),(550,280),(147,20,255),1 , cv2.LINE_AA)

    #Line intersect function for intersect coordinates
    [lanepos,y]=line_intersection([(x1,y1),(x2,y2)], [(90,270),(240,270)])
    [lanepos,y]=line_intersection([(x1,y1),(x2,y2)], [(400,270),(550,270)])

    #Assign colour code for intersect x-coordinate within limit region
    if lg1<lanepos<lg2 or rg1<lanepos<rg2: turn = green
    if (la1<lanepos<la2 or la3<lanepos<la4
        or ra1<lanepos<ra2 or ra3<lanepos<ra4): turn = amber
    if (lr1<lanepos<lr2 or lr3<lanepos<lr4
        or rr1<lanepos<rr2 or rr3<lanepos<rr4): turn = red
    
    #Assign intersect x-coordinate  for left and right limit region with
    # tracking indication lines
    if lr1 < lanepos < lr4 : #if x-coordinate  is within the left limit region
        leftpos = lanepos   #assign left limit region position value
        # tracking lines
        cv2.line(frame,(leftpos,250),(leftpos,290),turn,2 , cv2.LINE_AA)
    else:cv2.line(frame,(leftpos,250),(leftpos,290),turn,2 , cv2.LINE_AA)

    if rr1 < lanepos < rr4: #if x-coordinate  is within the left limit region
        rightpos = lanepos  #assign right limit region position value
        # tracking lines
        cv2.line(frame,(rightpos,250),(rightpos,290),turn,2 , cv2.LINE_AA)
    else:cv2.line(frame,(rightpos,250),(rightpos,290),turn,2 , cv2.LINE_AA)

    # background for status text
    txtbg = cv2.rectangle(frame, (410, 0), (640, 80), (0,0,0), -1)

#Function for steering correction
def steering ():


    cv2.putText(txtbg,'Lane Status:',(420,30), cv2.FONT_HERSHEY_TRIPLEX,
                1,(147,20,255),2,cv2.LINE_AA)   # lane status text

    #Steering conditions for each lane tracking scenario
    #(see report for each conditions)
    #Condition when in lane
    if ((lg1<leftpos<lg2 and rg1<rightpos<rg2) or
        (lg1<leftpos<lg2 and ra1<rightpos<ra2) or
        (lg1<leftpos<lg2 and ra3<rightpos<ra4) or
        (rg1<rightpos<rg2 and la1<leftpos<la2 ) or
        (rg1<rightpos<rg2 and la3<leftpos<la4)):
        GPIO.output(straight, GPIO.HIGH)    #GPIO ouput command signal for MCU
        # onscreen status texts
        cv2.putText(frame,'In lane',txtpos, font, 1,green,2,cv2.LINE_AA)
        cv2.putText(frame,'^Straight^',txtpos3, font, 1,green,2,cv2.LINE_AA)

    # Condition when slight left off centre
    if la1<leftpos<la2 and ra1<rightpos<ra2:
        GPIO.output(lightleft, GPIO.HIGH)   #GPIO ouput command signal for MCU
        # onscreen status texts
        cv2.putText(frame,'Off Centre',txtpos, font, 1,amber,2,cv2.LINE_AA)
        cv2.putText(frame,' <Light<',txtpos2, font, 1,amber,2,cv2.LINE_AA)

    # Condition when slight right off centre
    if la3<leftpos<la4 and ra3<rightpos<ra4:
        GPIO.output(lightright, GPIO.HIGH)  #GPIO ouput command signal for MCU
        # onscreen status texts
        cv2.putText(frame,'Off Centre',txtpos, font, 1,amber,2,cv2.LINE_AA)
        cv2.putText(frame,' >Light>',txtpos2, font, 1,amber,2,cv2.LINE_AA)

    # Condition when left off centre
    if (lr1<leftpos<lr2 and rr1<rightpos<rr2
        or lr1<leftpos<lr2 and ra1<rightpos<ra2
        or rr1<rightpos<rr2 and la1<leftpos<la2 ) :
        GPIO.output(hardleft, GPIO.HIGH)    #GPIO ouput command signal for MCU
        # onscreen status texts
        cv2.putText(frame,'Off Centre',txtpos, font, 1,red,2,cv2.LINE_AA)
        cv2.putText(frame,'<<Hard<<',txtpos2, font, 1,red,2,cv2.LINE_AA)

    # Condition when right off centre
    if (lr3<leftpos<lr4 and rr3<rightpos<rr4
        or lr3<leftpos<lr4 and ra3<rightpos<ra4
        or rr3<rightpos<rr4 and la3<leftpos<la4):
        GPIO.output(hardright, GPIO.HIGH)   #GPIO ouput command signal for MCU
        # onscreen status texts
        cv2.putText(frame,'Off Centre',txtpos, font, 1,red,2,cv2.LINE_AA)
        cv2.putText(frame,'>>Hard>>',txtpos2, font, 1,red,2,cv2.LINE_AA)
        

#Main loop function
while (cap.isOpened()): #while video is running

    #Reset all GPIO low
    GPIO.output(straight, GPIO.LOW)
    GPIO.output(lightleft, GPIO.LOW)
    GPIO.output(lightright, GPIO.LOW)
    GPIO.output(hardleft, GPIO.LOW)
    GPIO.output(hardright, GPIO.LOW)

    image_process ()    #call image processing function
    
    tracking ()     #call lane tracking function
 
    steering ()     #call steering adjustment function
    
    cv2.imshow('Capture',frame) #show original footage with lane following info
    cv2.imshow('Greyscale',grey)    #show greyscale footage
    cv2.imshow('Canny Edge',roi)    #show canny ROI footage
    if cv2.waitKey(1) & 0xFF == ord('q'):   #stop loop when "q" is pressed
      break


cap.released()  #release video capture
cv2.destroyAllWindows() #destroy all windows created
