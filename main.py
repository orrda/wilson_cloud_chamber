from collection import collection as coll
import glob
import matplotlib.pyplot as plt
import cv2
import numpy as np

"""
This script processes a video of a Wilson cloud chamber to detect and clean particles.
It uses the 'collection' module to create a collection object and perform various cleaning operations on the particles.
The cleaned particles are then saved to a file.

"""


def get_lengths(video_path):

    # Create a collection object
    collection = coll(video_path)

    # check if the video has already been processed
    particles_path = video_path[:-4] + "_particles" + "JSON"
    #collection.load_particles(particles_path)

    print("Number of particles:", len(collection.arr))

    if collection.arr == []:
        # Detect particles in the video
        collection.detect_particles(
                min_area_threshold = 20,
                max_area_threshhold = 2000000,
                time_threshold=10,
                first_frame=0, 
                last_frame=100000,
                frame_box=(200, 1900, 0, 1080)
            )

        # Save the particles to a folder

        collection.save_particles(particles_path)
        
        print("Number of particles:", len(collection.arr))

        #collection.save_particles_images()





    colle = [p for p in collection.arr if 50 < cv2.arcLength(np.array(p.contour), True) < 40000]
    colle = [p for p in colle if p.framerange[1] - p.framerange[0] > 30]

    print("Number of particles:", len(colle))


    frame = np.zeros((1980, 1080), dtype=np.uint8)

    for p in colle:
        frame = cv2.drawContours(frame, [np.array(p.contour)], -1, (255, 255, 255), 1)

    frame = cv2.resize(frame, (0, 0), fx=0.3, fy=0.3)
    cv2.imshow("frame", frame)
    cv2.waitKey(10000)
        

    colle = [p for p in colle if 300 < cv2.contourArea(np.array(p.contour)) < 4000]

    durationes = [(p.framerange[1] - p.framerange[0]) for p in colle]

    lengthes = [p.get_length() for p in colle]

    return lengthes, durationes


dirctory = "C:\\Users\\orrda\\OneDrive\\Desktop\\שנה ג\\סמסטר א\\מעבדה\\code\\particales\\week1.1\\סרטונים שבוע 1"


video_paths = glob.glob(dirctory + "\\*.MOV")

all_lengths = []
all_durationes = []
for path in video_paths:
    lengths, durations = get_lengths(path)
    all_lengths = all_lengths + lengths
    all_durationes = all_durationes + durations


plt.hist(all_lengths, bins=10)
plt.xlabel('Particle Length')
plt.ylabel('Frequency')
plt.title('Length Histogram')
plt.show()

plt.hist(all_durationes, bins=10)
plt.xlabel('Particle Duration')
plt.ylabel('Frequency')
plt.title('Duration Histogram')
plt.show()