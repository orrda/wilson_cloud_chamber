import cv2
import numpy as np

path = "C:\\Users\\orrda\\Downloads\\wilson_chamb1.mp4"

class particle:
    def __init__(self, framerange, box):
        self.framerange = framerange
        self.box = box
        pass


    def display_num(self, num):
        cap = cv2.VideoCapture()
        cap.open(path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, self.framerange[0] + num)

        ret, frame = cap.read()
        cv2.rectangle(frame, (self.box[0], self.box[1]), (self.box[2], self.box[3]), (0, 255, 0), 2)

        cv2.imshow('frame', frame)
        cv2.waitKey(0)


    def length(self):
        pass

    def sum(self):
        cap = cv2.VideoCapture(path)
        cap.open(self.framerange[0])

        while True:
            ret, frame = cap.read()
            if ret and self.framerange[0] <= cap.get(cv2.CAP_PROP_POS_FRAMES) <= self.framerange[1]:
                fr = cv2.rectangle(frame, (self.box[0], self.box[1]), (self.box[2], self.box[3]), (0, 255, 0), 2)

                if final_frame is None:
                    final_frame = fr
                final_frame = cv2.addWeighted(final_frame, 0.5, fr, 0.5, 0)
            else:
                break

        return final_frame
        
    def save_to_file(self):
        pass