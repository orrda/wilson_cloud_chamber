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

    # check if the video has already been processed
    particles_path = video_path[:-4] + "_particles" + ".JSON"
    #collection.load_particles(particles_path)

    if collection.arr == []:
        # Detect particles in the video
        collection.detect_particles(0.1, 20)

        # Clean the particles by area
        collection.clean_by_area(1000, 20000)

        # Clean the particles by location
        collection.clean_location(0, 10800, 10, 1000)

        # Clean the particles by brightness
        collection.clean_by_brightness(2, 100)

        # Clean the particles by duration
        collection.clean_by_duration(10, 1000)

        # Save the particles to a folder
        collection.save_particles(particles_path)

    durationes = [(p.framerange[1] - p.framerange[0]) for p in collection.arr]
    lengthes = [p.length() for p in collection.arr]
    lengthes = [l for l in lengthes if l > 0]
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