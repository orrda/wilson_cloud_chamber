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
        self.saving_folder = r'C:\Users\orrda\Downloads\new_particals'


    def detect_particles(self, min_area_threshold, max_area_threshhold, time_threshold, first_frame=0, last_frame=10000, frame_box = [0,1000,0,1980]):
        # Start the timer
        start_time = time.time()

        # Load the video
        cap = cv2.VideoCapture(self.video_path)
        ret, frame = cap.read()

        cap.set(cv2.CAP_PROP_POS_FRAMES, first_frame)


        # Define the parameters for shape detection
        bg_subtractor = cv2.createBackgroundSubtractorMOG2()

        # Loop through each frame in the video
        while cap.isOpened() :
            # Read the current frame
            ret, frame = cap.read()
            frame_count = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

            # Break the loop if the video has ended
            if not ret or frame_count > last_frame:
                break

            # Crop the frame to the region of interest
            frame = frame[frame_box[0]:frame_box[1], frame_box[2]:frame_box[3]]

            
            # Apply background subtraction
            fg_mask = bg_subtractor.apply(frame)
            fg_mask = cv2.medianBlur(fg_mask, 5)
            
            fg_mask_sum = np.sum(fg_mask)
            if fg_mask_sum > 10000000:
                continue

            # Perform contour detection on the binary frame
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Loop through the contours and extract the object informationn
            for contour in contours:
                
                # Filter out small contours
                if cv2.contourArea(contour) > min_area_threshold:
                    # Add the particle to the collection
                    self.add_particle(
                            frame_count, 
                            contour, 
                            max_area_threshhold,
                            time_threshold
                        )
                    
            
            # Draw the contours on the frame in yellow
            contours = []
            for particle in self.arr:
                if particle.framerange[1] == frame_count:
                    contours.append(particle.contour)
            cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)

            print("frame number: ", frame_count, "number of particles: ", len(self.arr))

            # Display the frame in a smaller window
            small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            small_fg_mask = cv2.resize(fg_mask, (0, 0), fx=0.5, fy=0.5)
            cv2.imshow("Frame", small_frame)
            cv2.imshow("Foreground Mask", small_fg_mask)
            cv2.waitKey(10)


        # Release the video file and return the detected objects
        cap.release()

        end_time = time.time()
        execution_time = end_time - start_time
        print("Execution time:", execution_time, " seconds, " ,"for: ", frame_count, " frames, ", "Number of particles:", len(self.arr))

        return



    def add_particle(self, frame_count, contour, max_area_threshold,time_threshold):

        # Create a new particle object
        our_particle = particle([frame_count, frame_count], contour, self.video_path)
        
        # Get the bounding circle of the contour
        center, radius = cv2.minEnclosingCircle(contour)

        # get the particles that are a distance of 10 frames from the current frame
        particles = [p for p in self.arr if frame_count - p.framerange[1] < time_threshold]

        # and check if the particle is close to the current center
        particles = [p for p in particles if 
                        np.sqrt((p.center[0] - center[0])**2 + (p.center[1] - center[1])**2) - p.radius - radius < 5
                     ]

        # Loop through each particle in particles, and connect the contours if they intersect
        for part in particles:
            # check if the contours intersect
            if do_they_intersect(part.contour, contour):
                new_particle = part + our_particle
                if new_particle != None and cv2.contourArea(new_particle.contour) < max_area_threshold:
                    self.arr.remove(part)
                    our_particle = new_particle
        
        if cv2.arcLength(np.array(our_particle.contour), True) > 60:
            if our_particle == None:
                print("None")
            self.arr = self.arr + [our_particle]
        return


    def save_particles(self, file_path):
        # Convert the collection object to a dictionary

        file_path = file_path

        arr = [particle.__dict__ for particle in self.arr]
        for i in range(len(arr)):
            arr[i]["contour"] = arr[i]["contour"].tolist()
        
        collection_dict = {
            "video_path": self.video_path,
            "arr": arr
        }
        # check if the file exists
        if os.path.exists(file_path):
            # Delete the file
            os.remove(file_path)
            
        # Save the collection as a JSON file
        with open(file_path, "w") as json_file:
            good = json.dump(collection_dict, json_file)
            if not good:
                print("Failed to save ", file_path)
            else:
                print("Saved ", len(self.arr), " particles to the file: ", file_path)

    def save_particles_images(self):

        folder_path = self.saving_folder

        print("Saving ", len(self.arr) ," particles to the folder:", folder_path)

        # Load the video
        cap = cv2.VideoCapture(self.video_path)

        vid_num = self.video_path.split("\\")[-1].split(".")[0]

        # Save the particles to the folder
        for particle in self.arr:
            cap.set(cv2.CAP_PROP_POS_FRAMES, particle.framerange[0])
            ret, frame = cap.read()

            
            rect = cv2.boundingRect(np.array(particle.contour))
            x, y, w, h = rect
            particle_image = frame[y:y+h, x:x+w]

            # Save the particle image in the folder
            particle_image_path = os.path.join(folder_path, f"video_{vid_num}_particle_{particle.framerange[0]}.png")
            good = cv2.imwrite(particle_image_path, particle_image)
            if not good:
                print("Failed to save ", particle_image_path)

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



def do_they_intersect(contour1, contour2):
    # check if the contours intersect
    for point in contour2:
        x, y = point[0]
        x = int(x)
        y = int(y)
        if cv2.pointPolygonTest(contour1, (x,y), False) > -1:
            return True
    for point in contour1:
        x, y = point[0]
        x = int(x)
        y = int(y)
        if cv2.pointPolygonTest(contour2, (x,y), False) > -1:
            return True
    return False

