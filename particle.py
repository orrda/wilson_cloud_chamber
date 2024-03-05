import cv2
import numpy as np
import os


class particle:
    def __init__(self, framerange, contour, video_path, center=None, radius=None, thickness=None, area=None, length=None, width=None, type=None, brightness=None, direction=None, location=None):
        contour = np.array(contour)
        self.framerange = framerange
        self.contour = contour
        self.video_path = video_path

        center, radius = cv2.minEnclosingCircle(contour)
        self.center = center
        self.radius = radius


        self.thickness = None
        self.area = None
        self.length = None
        self.width = None
        self.type = None
        self.brightness = None
        self.direction = None
        self.location = None

        pass


    def display_num(self, num):
        # display the frame of the particle in the given number since the start of the framerange
        cap = cv2.VideoCapture()
        cap.open(self.video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, self.framerange[0] + num)

        ret, frame = cap.read()
        cv2.rectangle(frame, (self.box[0], self.box[1]), (self.box[2], self.box[3]), (0, 255, 0), 2)

        cv2.imshow('frame', frame)
        cv2.waitKey(0)


    def update(self):

        center, radius = cv2.minEnclosingCircle(self.contour)
        self.center = center
        self.radius = radius

        self.length = cv2.arcLength(self.contour, True)
        print(self.area)
        self.area = cv2.contourArea(self.contour)
        print(self.area)
        self.thickness = (radius*radius*np.pi)/self.area


        return self


    def __add__(self, other):
        # add two particles together
        new_contour = self.merge_contours(self.contour, other.contour)
        if new_contour is None:
            return None

        new_framerange = (min(self.framerange[0],other.framerange[0]), max(self.framerange[1], other.framerange[1]))

        new_particle = particle(new_framerange, new_contour, self.video_path)

        center, radius = cv2.minEnclosingCircle(new_contour)
        new_particle.center = center
        new_particle.radius = radius

        new_particle.length = cv2.arcLength(new_particle.contour, True)

        new_particle.area = cv2.contourArea(new_particle.contour)
        
        return new_particle


    def get_brightness(self):
        cap = cv2.VideoCapture(self.video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, self.framerange[0])
        ret, frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        shape = np.zeros((frame.shape[0], frame.shape[1]), dtype=np.uint8)
        shape = cv2.drawContours(shape, [np.array(self.contour)], -1, (255, 255, 255), -1)
        frame = cv2.bitwise_and(frame, frame, mask=shape)

        brightness = np.mean(frame)
        self.brightness = brightness
        return brightness

    
    def particle_type(self):
        # importent function, that requires a non-trivial implementation
        pass

    def particle_width(self):
        # maybe by dividing the area by the length?
        pass

    def save_to_file(self, folder_path, num):
        cap = cv2.VideoCapture(self.video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, self.framerange[0])
        ret, frame = cap.read()
        if not ret:
            return
        box = cv2.boundingRect(np.array(self.contour))
        frame = frame[box[1]:box[1]+box[3], box[0]:box[0]+box[2]]
        frame = cv2.drawContours(frame, [np.array(self.contour)], -1, (0, 255, 0), 2)
        
        duration = self.framerange[1] - self.framerange[0]
        frame = cv2.putText(frame, "duration: " + str(duration), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        frame = cv2.putText(frame, "area: " + str(self.area), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        
        directory = folder_path
        if not os.path.exists(directory):
            os.makedirs(directory)

        file_name = str(num) + ".png"
        file_name = os.path.join(directory, file_name)

        cv2.imwrite(file_name, frame)
        cap.release()

        return

    def get_direction(self):
        (x,y), (MA,ma), angle = cv2.fitEllipse(self.contour)
        self.direction = angle
        return angle

    
    def merge_contours(self, contour1, contour2):
        # merge contours into one
        # create a closed shape from the two contours

        filled = np.zeros((1980, 1080), dtype=np.uint8)

        filled = cv2.drawContours(filled, [contour1, contour2], -1, color = (255,255,255), thickness= -1)
        
        contours, _ = cv2.findContours(filled, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) > 1:
            areas = [cv2.contourArea(c) for c in contours]
            new_contour = contours[areas.index(max(areas))]
        if len(contours) == 1:
            new_contour = contours[0]
        if len(contours) == 0:
            return None

        return new_contour
    
    
    def get_length(self):
        radius = cv2.minEnclosingCircle(np.array(self.contour))[1]
        return radius * 2

