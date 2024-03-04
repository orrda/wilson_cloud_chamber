from collection import collection as coll
import glob
import matplotlib.pyplot as plt

"""
This script processes a video of a Wilson cloud chamber to detect and clean particles.
It uses the 'collection' module to create a collection object and perform various cleaning operations on the particles.
The cleaned particles are then saved to a file.

"""


def get_lengths(video_path):

    # Create a collection object
    collection = coll(video_path)

    # check if the video has already been processed
    particles_path = video_path[:-4] + "_particles" + ".JSON"
    #collection.load_particles(particles_path)

    if collection.arr == []:
        """ 
        Detect particles in the video, 
        the first argument is the minumum ratio between the area intersection of the boxes and their union area,
        so that it will be considered as the same particle.
        the second argument is the maximum number of frames between the two boxes to be considered as the same particle.
        """
        collection.detect_particles(0.1, 20)

        # Clean the particles by area, first argument is the minimum area and the second is the maximum area
        collection.clean_by_area(1000, 20000)

        # Clean the particles by location, if we know that fo example the particles are only in the middle of the frame
        collection.clean_location(0, 10800, 10, 1000)

        # Clean the particles by brightness
        collection.clean_by_brightness(2, 255)

        # Clean the particles by duration
        collection.clean_by_duration(10, 1000)

        # Save the particles to a folder as a json file so next time we can load them from the file, 
        # and we dont need to detact them again
        collection.save_particles(particles_path)

        # Save the images of the particles to a folder, can be specified as an argument or in 'collection' class
        # saves each particle in a image with the name of the video and the frame that the particle was first detected
        collection.save_particles_images()


    durationes = [(p.framerange[1] - p.framerange[0]) for p in collection.arr]
    lengthes = [p.length() for p in collection.arr]
    lengthes = [l for l in lengthes if l > 0]
    return lengthes, durationes




# put the path to the directory containing the videos here
dirctory = "C:\\Users\\orrda\\OneDrive\\Desktop\\שנה ג\\סמסטר א\\מעבדה\\code\\particales\\week1.1\\סרטונים שבוע 1"

video_paths = glob.glob(dirctory + "\\*.MOV")

all_lengths = []
all_durationes = []
for path in video_paths:
    lengths, durations = get_lengths(path)
    all_lengths = all_lengths + lengths
    all_durationes = all_durationes + durations



# in the end it will show two histograms, one for the length of the particles and one for the duration of the particles
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
