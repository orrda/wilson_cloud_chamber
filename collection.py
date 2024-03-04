import cv2
import numpy as np
import time
from particle import particle
import os
import shutil
import json
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
        self.start_frame = 0
        self.saving_folder = r'C:\Users\orrda\Downloads\new_particals'

    def detect_particles(self, area_threshold, time_threshold):
        # Start the timer
        start_time = time.time()

        # Load the video
        cap = cv2.VideoCapture(self.video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
        ret, frame = cap.read()

        # Define the parameters for shape detection
        bg_subtractor = cv2.createBackgroundSubtractorMOG2()

        # Loop through each frame in the video
        while cap.isOpened():
            # Read the current frame
            ret, frame = cap.read()

            frame_count = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            if frame_count % 50 == 0:
                print("frame: ", frame_count)

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

            # Display the frame with the detected objects
            """
            relevant_particles = [p for p in self.arr if frame_count - p.framerange[1] < 10]
            relevant_boxes = [p.box for p in relevant_particles]
            for box in relevant_boxes:
                x1, y1, x2, y2 = box
                frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            cv2.imshow('frame', small_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            """


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
        new_particle = particle([frame_count, frame_count], box, self.video_path)
        self.arr.append(new_particle)
        return
    
    def save_particles_images(self, folder_path = None):
        if folder_path is None:
            folder_path = self.saving_folder
        else:
            self.saving_folder = folder_path

        print("Saving ", len(self.arr) ," particles to the folder:", folder_path)

        # Load the video
        cap = cv2.VideoCapture(self.video_path)

        vid_num = self.video_path.split("\\")[-1].split(".")[0]

        # Save the particles to the folder
        for particle in self.arr:
            cap.set(cv2.CAP_PROP_POS_FRAMES, particle.framerange[0])
            ret, frame = cap.read()

            x1, y1, x2, y2 = particle.box
            particle_image = frame[y1:y2, x1:x2]

            # Save the particle image in the folder
            particle_image_path = os.path.join(folder_path, f"video_{vid_num}_particle_{particle.framerange[0]}.png")
            good = cv2.imwrite(particle_image_path, particle_image)
            if not good:
                print("Failed to save ", particle_image_path)

        return

    def save_particles(self, file_path):
        # Convert the collection object to a dictionary
        collection_dict = {
            "video_path": self.video_path,
            "arr": [particle.__dict__ for particle in self.arr]
        }

        # Save the collection as a JSON file
        with open(file_path, "w") as json_file:
            json.dump(collection_dict, json_file)

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
    
    def load_particles(self, file_path):

        # check if the video has already been processed
        if not os.path.exists(file_path):
            print("No saved particles found")
            return

        # Load the collection from the JSON file
        with open(file_path, "r") as json_file:
            collection_dict = json.load(json_file)
            self.video_path = collection_dict["video_path"]
            self.arr = [particle(**particle_dict) for particle_dict in collection_dict["arr"]]
            print("Loaded ", len(self.arr), " particles from the file: ", file_path)
        return
        
