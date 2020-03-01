#!/usr/bin/python
#-*- coding: utf-8 -*-
import threading
import time
from datetime import datetime

import math
import cv2
import numpy as np

time_cycle = 80

class MyAlgorithm(threading.Thread):

    def __init__(self, camera, motors):
        self.camera = camera
        self.motors = motors
        self.threshold_image = np.zeros((640,360,3), np.uint8)
        self.color_image = np.zeros((640,360,3), np.uint8)
        self.stop_event = threading.Event()
        self.kill_event = threading.Event()
        self.lock = threading.Lock()
        self.threshold_image_lock = threading.Lock()
        self.color_image_lock = threading.Lock()
        threading.Thread.__init__(self, args=self.stop_event)

    def getImage(self):
        self.lock.acquire()
        img = self.camera.getImage().data
        self.lock.release()
        return img

    def set_color_image (self, image):
        img  = np.copy(image)
        if len(img.shape) == 2:
          img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        self.color_image_lock.acquire()
        self.color_image = img
        self.color_image_lock.release()

    def get_color_image (self):
        self.color_image_lock.acquire()
        img = np.copy(self.color_image)
        self.color_image_lock.release()
        return img

    def set_threshold_image (self, image):
        img = np.copy(image)
        if len(img.shape) == 2:
          img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        self.threshold_image_lock.acquire()
        self.threshold_image = img
        self.threshold_image_lock.release()

    def get_threshold_image (self):
        self.threshold_image_lock.acquire()
        img  = np.copy(self.threshold_image)
        self.threshold_image_lock.release()
        return img

    def run (self):

        while (not self.kill_event.is_set()):
            start_time = datetime.now()
            if not self.stop_event.is_set():
                self.algorithm()
            finish_Time = datetime.now()
            dt = finish_Time - start_time
            ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
            #print (ms)
            if (ms < time_cycle):
                time.sleep((time_cycle - ms) / 1000.0)

    def stop (self):
        self.stop_event.set()

    def play (self):
        if self.is_alive():
            self.stop_event.clear()
        else:
            self.start()

    def kill (self):
        self.kill_event.set()

    def algorithm(self):
        #GETTING THE IMAGES
        w = 0
        v = 13
        last_turn = 2
        lower = [10, 0, 0]
        upper = [100, 0, 0]
        finished = False
        # Add your code here
#        print "Runing"
        image = self.getImage()

        lower = np.array(lower, dtype = "uint8")
        upper = np.array(upper, dtype = "uint8")



        mask = cv2.inRange(image, lower, upper)
        output = cv2.bitwise_and(image, image, mask = mask)
#        cv2.line(output,(0,300), (700,300), (255, 255, 255), 2, 8)
        moments  = cv2.moments(mask)
        area = moments['m00']
        x = 0
        y = 0
        if(area > 20000):
        	x = int(moments['m10']/moments['m00'])
	        y = int(moments['m01']/moments['m00'])
	        print "( ", x, " , ", y, " )"
	        cv2.rectangle(output, (x, y), (x+2, y+2),(0,0,255), 2)

        if(x == 0):
            w = last_turn
        if(x < 200):
            w = 3
            v = 5
            last_turn = 3
        elif(x > 400):
            w = -3
            v = 5
            last_turn = -3
        elif(x>200 and x<400):
            w = 0
            v = 10
        error = abs(320 - x)

		# show the images
        print "ERROR:", error
        #EXAMPLE OF HOW TO SEND INFORMATION TO THE ROBOT ACTUATORS
        self.motors.sendV(v)
        self.motors.sendW(w)
        #cv2.imshow("Images", np.hstack([image, output]))
    	#	cv2.waitKey(0)

        #SHOW THE FILTERED IMAGE ON THE GUI
        self.set_threshold_image(output)
