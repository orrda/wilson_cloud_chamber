import cv2
import numpy as np
import time
from particle import particle
import os
import shutil
import matplotlib.pyplot as plt

class collection:
    """
    A class that represents a collection of particles detected in a video.

    Attributes:
        video_path (str): The path to the video file.
        arr (list): A list to store the detected particles.

    Methods:
        detect_particles: Detects particles in the video based on area and time thresholds.
        add_particle: Adds a new particle to the collection.
        save_particles: Saves the detected particles as images in a folder.
        clean_by_area: Removes particles based on their area.
        clean_location: Removes particles based on their location.
        clean_by_brightness: Removes particles based on their brightness.
        clean_by_duration: Removes particles based on their duration.
        load_particles: Loads previously saved particles from a folder.
    """


    def __init__(self, video_path):
        self.video_path = video_path
        self.arr = []

    def detect_particles(self, area_threshold, time_threshold):
        # Start the timer
        start_time = time.time()

        # Load the video
        cap = cv2.VideoCapture(self.video_path)
        ret, frame = cap.read()

        # Define the parameters for shape detection
        bg_subtractor = cv2.createBackgroundSubtractorMOG2()

        # Loop through each frame in the video
        while cap.isOpened():
            # Read the current frame
            ret, frame = cap.read()

            frame_count = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

            # Break the loop if the video has ended
            if not ret:
                break

            # Apply background subtraction
            fg_mask = bg_subtractor.apply(frame)

            # Perform contour detection on the foreground mask
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Loop through the contours and extract the object information
            for contour in contours:
                # Filter out small contours
                if cv2.contourArea(contour) > 100:
                    x, y, w, h = cv2.boundingRect(contour)
                    box = (x, y, x + w, y + h)
                    box_area = (x + w - x) * (y + h - y)
                    if 10000> box_area > 1000:
                        self.add_particle(box, frame_count, area_threshold, time_threshold)

        # Release the video file and return the detected objects
        cap.release()

        end_time = time.time()
        execution_time = end_time - start_time
        print("Execution time:", execution_time, " seconds, " ,"for: ", frame_count, " frames, ", "Number of particles:", len(self.arr))

        return
    
    def add_particle(self, box, frame_count, area_threshold, time_threshold):
        # Loop through each particle
        for prt in self.arr:
            # Calculate the intersection area between the boxes
            x1, y1, x2, y2 = box
            u_x1, u_y1, u_x2, u_y2 = prt.box
            intersection_area = max(0, min(x2, u_x2) - max(x1, u_x1)) * max(0, min(y2, u_y2) - max(y1, u_y1))

            # Calculate the union area between the boxes
            box_area = (x2 - x1) * (y2 - y1)
            unique_box_area = (u_x2 - u_x1) * (u_y2 - u_y1)
            union_area = box_area + unique_box_area - intersection_area

            # Calculate the overlap ratio
            overlap_ratio = intersection_area / union_area

            # Check if the boxes overlap
            if overlap_ratio > area_threshold:
                if prt.framerange[1] - frame_count < time_threshold:
                    # Update the prt's position
                    prt.framerange[1] = frame_count
                    return

        # Create a new particle object
        new_particle = particle([frame_count, frame_count], box)
        self.arr.append(new_particle)
        print("New particle added")
        return
    
    def save_particles(self):
        folder = os.path.join(os.path.dirname(self.video_path), "particles")
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


        # Check if the folder exists, and delete it if it does

        folder_path = os.path.join(os.path.dirname(self.video_path), "particles")

        os.makedirs(folder_path, exist_ok=True)

        print("Saving ", len(self.arr) ," particles to the folder:", folder_path)

        # Load the video
        cap = cv2.VideoCapture(self.video_path)

        # Save the particles to the folder
        for particle in self.arr:
            cap.set(cv2.CAP_PROP_POS_FRAMES, particle.framerange[0])
            ret, frame = cap.read()

            x1, y1, x2, y2 = particle.box
            particle_image = frame[y1:y2, x1:x2]

            # Save the particle image in the folder
            particle_image_path = os.path.join(folder_path, f"particle_{particle.framerange[0]}.jpg")
            cv2.imwrite(particle_image_path, particle_image)

        return
    
    def clean_by_area(self, min_area, max_area):
        # Loop through the particles and remove the ones that are too small or too large
        new_particles = []
        for particle in self.arr:
            x1, y1, x2, y2 = particle.box
            area = (x2 - x1) * (y2 - y1)
            if min_area < area < max_area:
                new_particles.append(particle)

        print("Number of particles before cleaning:", len(self.arr), "Number of particles after cleaning by area:", len(new_particles))
        self.arr = new_particles
        return

    def clean_location(self, min_x, max_x, min_y, max_y):
        # Loop through the particles and remove the ones that are outside the specified location
        new_particles = []
        for particle in self.arr:
            x1, y1, x2, y2 = particle.box
            if min_x < x1 < max_x and min_y < y1 < max_y and min_x < x2 < max_x and min_y < y2 < max_y:
                new_particles.append(particle)

        print("Number of particles before cleaning:", len(self.arr), "Number of particles after cleaning by location:", len(new_particles))
        self.arr = new_particles
        return    
    
    def clean_by_brightness(self, min_brightness, max_brightness):
        # Loop through the particles and remove the ones that are too bright or too dark
        new_particles = []
        for particle in self.arr:
            cap = cv2.VideoCapture(self.video_path)
            cap.set(cv2.CAP_PROP_POS_FRAMES, particle.framerange[0])
            ret, frame = cap.read()

            x1, y1, x2, y2 = particle.box
            particle_image = frame[y1:y2, x1:x2]

            # Calculate the brightness of the particle
            brightness = np.mean(particle_image)

            if min_brightness < brightness < max_brightness:
                new_particles.append(particle)

        print("Number of particles before cleaning:", len(self.arr), "Number of particles after cleaning by brightness:", len(new_particles))
        self.arr = new_particles
        return
    
    def clean_by_duration(self, min_duration, max_duration):
        # Loop through the particles and remove the ones that are too short or too long
        new_particles = []
        for particle in self.arr:
            duration = particle.framerange[1] - particle.framerange[0]
            if min_duration < duration < max_duration:
                new_particles.append(particle)

        print("Number of particles before cleaning:", len(self.arr), "Number of particles after cleaning by duration:", len(new_particles))
        self.arr = new_particles
        return
    
    def load_particles(self):
        # not sure if it works yet
        folder = os.path.join(os.path.dirname(self.video_path), "particles")
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if file_path.endswith(".jpg"):
                frame_number = int(filename.split("_")[1].split(".")[0])
                particle_image = cv2.imread(file_path)
                x1, y1, x2, y2 = particle.box
                box = (x1, y1, x2, y2)
                new_particle = particle([frame_number, frame_number], box)
                self.arr.append(new_particle)
        return
    
    def __add__(self, other):
        # don't use yet, has problems regarding the video path
        new_collection = collection(self.video_path)
        new_collection.arr = self.arr + other.arr
        return new_collection

    def length_histogram(self):
        """
        Generate a histogram of particle lengths in the collection.

        This function calculates the length of each particle in the collection
        and plots a histogram to visualize the distribution of particle lengths.

        Returns:
            None
        """
        length_list = [particle.length() for particle in self.arr]

        plt.hist(length_list, bins=10)
        plt.xlabel('Particle Length')
        plt.ylabel('Frequency')
        plt.title('Length Histogram')
        plt.show()
        return

            

    