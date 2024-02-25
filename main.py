from collection import collection as coll
import glob
import matplotlib.pyplot as plt

"""
This script processes a video of a Wilson cloud chamber to detect and clean particles.
It uses the 'collection' module to create a collection object and perform various cleaning operations on the particles.
The cleaned particles are then saved to a file.


currentliy some problems with the latest videos, probably because of using .MOV format instead of .mp4
"""

video_path = "C:\\Users\\orrda\\Downloads\\wilson_chamb1.mp4"


def get_lengths(video_path):

    # Create a collection object
    collection = coll(video_path)

    # Detect particles in the video
    collection.detect_particles(0.2, 40)

    # Clean the particles by area
    collection.clean_by_area(1500, 10000)

    # Clean the particles by location
    collection.clean_location(0, 10800, 10, 1000)

    # Clean the particles by brightness
    collection.clean_by_brightness(2, 50)

    # Clean the particles by duration
    collection.clean_by_duration(5, 1000)

    # Save the particles to a folder
    collection.save_particles("C:\\Users\\orrda\\OneDrive\\Desktop\\שנה ג\\סמסטר א\\מעבדה\\code\\particales\\week1.1\\סרטונים שבוע 1\\particles")

    lengths = [part.length() for part in collection.arr]

    return lengths


dirctory = "C:\\Users\\orrda\\OneDrive\\Desktop\\שנה ג\\סמסטר א\\מעבדה\\code\\particales\\week1.1\\סרטונים שבוע 1"


video_paths = glob.glob(dirctory + "\\*.MOV")

all_lengths = []
for path in video_paths:
    all_lengths.append(get_lengths(path))

plt.hist(all_lengths, bins=10)
plt.xlabel('Particle Length')
plt.ylabel('Frequency')
plt.title('Length Histogram')
plt.show()