from collection import collection as coll
import glob
import matplotlib.pyplot as plt
import cv2
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

"""
This script processes a video of a Wilson cloud chamber to detect and clean particles.
It uses the 'collection' module to create a collection object and perform various cleaning operations on the particles.
The cleaned particles are then saved to a file.

"""


dirctory = "C:\\Users\\orrda\\OneDrive\\Desktop\\שנה ג\\סמסטר א\\מעבדה\\code\\particales\\week1.1\\סרטונים שבוע 1"
pix_per_mm = 4.5936
frames_per_second = 30
duration_range = [130, 280]
min_length = 200


def get_lengths(video_path):

    # Create a collection object
    collection = coll(video_path)

    # check if the video has already been processed
    particles_path = video_path[:-4] + "_particles" + "JSON"
    collection.load_particles(particles_path)

    if collection.arr == []:
        # Detect particles in the video
        collection.detect_particles(
                min_area_threshold = 20,
                max_area_threshhold = 2000000,
                time_threshold=8,
                first_frame=0, 
                last_frame=1000000,
                frame_box=(300, 1900, 0, 1080)
            )


        # Save the particles JSON to a file 
        collection.save_particles(particles_path)
        



    # reduce the particles to the ones with the right duration
    colle = [p for p in collection.arr if duration_range[1] > p.framerange[1] - p.framerange[0] > duration_range[0]]

    print("Number of particles for 'path'=...", video_path[-9:], ", is - ", len(colle))

    frame = np.zeros((1980, 1080), dtype=np.uint8)

    for p in colle:
        frame = cv2.drawContours(frame, [np.array(p.contour)], -1, (255, 255, 255), 1)

    frame = cv2.resize(frame, (0, 0), fx=0.3, fy=0.3)
    cv2.imshow("frame", frame)
    cv2.waitKey(100)

    lengthes = [get_contour_length(np.array(p.contour)) for p in colle]
    lengthes = [l for l in lengthes if min_length < l]

    return lengthes


def get_contour_length(contour):
    contour = cv2.approxPolyDP(contour, 0.01*cv2.arcLength(contour, True), True)
    return cv2.arcLength(contour, True)/2





video_paths = glob.glob(dirctory + "\\*.MOV")

all_lengths = []

for path in video_paths:
    all_lengths = all_lengths + get_lengths(path)


all_lengths = [l/pix_per_mm for l in all_lengths]


plt.hist(all_lengths, bins=10)
plt.xlabel('Particle Length [mm]')
plt.ylabel('Frequency')
plt.title('Length Histogram')
plt.show()
