"""
This script processes a video of a Wilson cloud chamber to detect and clean particles.
It uses the 'collection' module to create a collection object and perform various cleaning operations on the particles.
The cleaned particles are then saved to a file.
"""

from collection import collection as coll

video_path = "C:\\Users\\orrda\\Downloads\\wilson_chamb1.mp4"

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

# save the particles to a file
collection.save_particles()