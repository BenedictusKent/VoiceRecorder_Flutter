#!/usr/bin/env python
import sys
sys.path.append('/home/robot/catkin_ws/devel/lib/python2.7/dist-packages')

import rospy
import time
import cv2
import math
import numpy as np
from tm_msgs.msg import *
from tm_msgs.srv import *

def send_script(script):
    rospy.wait_for_service('/tm_driver/send_script')
    try:
        script_service = rospy.ServiceProxy('/tm_driver/send_script', SendScript)
        move_cmd = SendScriptRequest()
        move_cmd.script = script
        resp1 = script_service(move_cmd)
    except rospy.ServiceException as e:
        print("Send script service call failed: %s"%e)
    
def set_io(state):
    rospy.wait_for_service('/tm_driver/set_io')
    try:
        io_service = rospy.ServiceProxy('/tm_driver/set_io', SetIO)
        io_cmd = SetIORequest()
        io_cmd.module = 1
        io_cmd.type = 1
        io_cmd.pin = 0
        io_cmd.state = state
        resp1 = io_service(io_cmd)
    except rospy.ServiceException as e:
        print("IO service call failed: %s"%e)

def regionGrowing(img):
    rows = img.shape[0]
    cols = img.shape[1]
    img_label = np.zeros((int(rows), int(cols)), dtype=np.int)
    label = 0
    stack = []
    dire = [[-1,0],[1,0],[0,1],[0,-1]]
    for i in range(rows):
        for j in range(cols):
            if img[i][j] == 255 and img_label[i][j] == 0:
                label += 1
                img_label[i][j] = label
                stack.append([i, j])
                while len(stack) > 0:
                    loc = stack.pop(-1)
                    r = loc[0]
                    c = loc[1]

                    for k in range(4):
                        nr = r+dire[k][0]
                        nc = c+dire[k][1]
                        if nr>=0 and nr<rows and nc>=0 and nc<cols and img_label[nr][nc] == 0 and img[nr][nc] == 255:
                            img_label[nr][nc] = label
                            stack.append([nr, nc])
	
    return img_label, label

def getDescriptor(img_label, n_regions, img_rgb, r_centers, c_centers, angles):
    rows = img_label.shape[0]
    cols = img_label.shape[1]
    for i in range(1, n_regions+1):
        area = 0
        r_center = 0
        c_center = 0
        for r in range(rows):
            for c in range(cols):
                if img_label[r][c] == i:
                    area += 1
                    r_center += r
                    c_center += c
        
        if area < 100:
            continue
        
        r_center //= area
        c_center //= area
        mu11 = 0
        mu20 = 0
        mu02 = 0
        
        for r in range(rows):
            for c in range(cols):
                if img_label[r][c] == i:
                    mu11 += (r - r_center)*(c - c_center)
                    mu20 += (r - r_center)*(r - r_center)
                    mu02 += (c - c_center)*(c - c_center)
        
        angle = 0.5*math.atan2(2 * mu11, mu20 - mu02)
        r_centers.append(r_center)
        c_centers.append(c_center)
        angles.append(angle)

        length = 150
        P1y = int(round(r_center - length * math.cos(angle)))
        P1x = int(round(c_center - length * math.sin(angle)))
        P2y = int(round(r_center + length * math.cos(angle)))
        P2x = int(round(c_center + length * math.sin(angle)))

        cv2.line(img_rgb, (P1x, P1y), (P2x, P2y), (0, 0, 255), 2)
        cv2.circle(img_rgb, (c_center, r_center), 4, (255,0,0), -1)


if __name__ == '__main__':
    try:
        rospy.init_node('send_scripts', anonymous=True)
        #--- move command by joint angle ---#
        # script = 'PTP(\"JPP\",45,0,90,0,90,0,35,200,0,false)'
        #--- move command by end effector's pose (x,y,z,a,b,c) ---#
        # mtx = [[2.65013319e+03, 0.00000000e+00, 2.43817135e+02], [0.00000000e+00, 2.55952742e+03, 4.00199190e+02], [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]]
        # dist = [[ 4.01981628e-01, -4.12785164e+00, -1.19094523e-02, -4.16451477e-02, 6.80704829e+01]]

        targetP1 = "100.00 , 150.00 , 400.00 , 180.00 , 0.00 , 0.00"
        # targetP1 = "350.00 , 380.00 , 135.00 , 180.00 , 0.00 , 0.00"
        script = "PTP(\"CPP\","+targetP1+",100,200,0,false)"

        send_script(script)
        set_io(0.0)# 1.0: close gripper, 0.0: open gripper

        image = cv2.VideoCapture(0)
        ret ,frame = image.read()
        #cv2.imwrite('image20.jpg', frame)
        #undistorted_frame = cv2.undistort(frame, mtx, dist, None, mtx)
        cv2.imwrite('image.jpg', frame[40:-170,100:-160]) 
        #cv2.imwrite('image.jpg', undistorted_frame[40:-170,100:-160])
        image.release()

        img = cv2.imread('image.jpg', cv2.IMREAD_COLOR)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        th, img_bin = cv2.threshold(img_gray, 150, 255, cv2.THRESH_BINARY)

        img_label, n_regions = regionGrowing(img_bin)
        r_centers = []
        c_centers = []
        angles = []
        height = 110

        getDescriptor(img_label, n_regions, img, r_centers, c_centers, angles)

        cv2.imshow("Result",img)
        for i in range(len(r_centers)):
            print(r_centers[i], c_centers[i], angles[i]*180/math.pi)

        for i in range(len(r_centers)):

            x = 1.1267750978091868 * r_centers[i] - 1.0938629253027443 * c_centers[i] + 343.9786726668608
            y = 1.0775851441372453 * r_centers[i] + 1.1433776167399117 * c_centers[i] + 6.654863050272979
            angle = (angles[i] * 180 / math.pi) - 45

            print(x,y,angle)

            #--- move command by end effector's pose (x,y,z,rx,ry,rz) ---#
            targetP1 = str(x) + "," + str(y) + ", 180.00 , 180.00 , 0.00 , " + str(angle)
            script = "PTP(\"CPP\"," + targetP1 + ",100,200,0,false)"
            send_script(script)

            targetP1 = str(x) + "," + str(y) + ", 108.00 , 180.00 , 0.00 , " + str(angle)
            script = "PTP(\"CPP\"," + targetP1 + ",100,200,0,false)"
            send_script(script)

            set_io(1.0) # 1.0: close gripper, 0.0: open gripper

            targetP1 = str(x) + "," + str(y) + ", 180.00 , 180.00 , 0.00 , " + str(angle)
            script = "PTP(\"CPP\"," + targetP1 + ",100,200,0,false)"
            send_script(script)

            time.sleep(5)

            targetP1 = "400.00 , 400.00 ," + str(height) + ", 180.00 , 0.00 , 0.00"
            script = "PTP(\"CPP\"," + targetP1 + ",100,200,0,false)"
            send_script(script)

            set_io(0.0) # 1.0: close gripper, 0.0: open gripper

            targetP1 = "400.00 , 400.00 ," + str(height+35) + ", 180.00 , 0.00 , 0.00"
            script = "PTP(\"CPP\"," + targetP1 + ",100,200,0,false)"
            send_script(script)

            height = height + 25

        targetP1 = "100.00 , 150.00 , 400.00 , 180.00 , 0.00 , 0.00"
        script = "PTP(\"CPP\"," + targetP1 + ",100,200,0,false)"
        send_script(script)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    except rospy.ROSInterruptException:
        pass