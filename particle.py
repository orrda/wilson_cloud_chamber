import cv2
import numpy as np

path = "C:\\Users\\orrda\\Downloads\\wilson_chamb1.mp4"

class particle:
    def __init__(self, framerange, box):
        self.framerange = framerange
        self.box = box
        pass


    def display_num(self, num):
        # display the frame of the particle in the given number since the start of the framerange
        cap = cv2.VideoCapture()
        cap.open(path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, self.framerange[0] + num)

        ret, frame = cap.read()
        cv2.rectangle(frame, (self.box[0], self.box[1]), (self.box[2], self.box[3]), (0, 255, 0), 2)

        cv2.imshow('frame', frame)
        cv2.waitKey(0)


    def length(self):
        frame_sum = self.sum()
        #frame_sum = cv2.cvtColor(frame_sum, cv2.COLOR_BGR2GRAY)
        # sharpen the image
        #frame_sum = cv2.filter2D(frame_sum, -1, np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]))

        contours , _ = cv2.findContours(frame_sum, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        print(len(contours))
        length_list = [cv2.arcLength(c, True) for c in contours]

        length = max(length_list)/2

        return length

    def sum(self):
        cap = cv2.VideoCapture(path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, self.framerange[0])
        final_frame = None

        while True:
            ret, frame = cap.read()
            if frame is None:
                break
            frame = frame[self.box[1]:self.box[3], self.box[0]:self.box[2]]

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

    def particle_type(self):
        # importent function, that requires a non-trivial implementation
        pass

    def particle_width(self):
        # maybe by dividing the area by the length?
        pass