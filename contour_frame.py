import cv2
import numpy as np



# Load the video
video_path = "C:\\Users\\orrda\\Downloads\\wilson_chamb1.mp4"
cap = cv2.VideoCapture(video_path)
ret, frame = cap.read()

big_array = np.array(frame)

# Define the parameters for shape detection
min_contour_length = 50  # Minimum contour length to consider as a thin long shape

# Iterate through each frame in the video
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply edge detection to find contours
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Iterate through each contour
    for contour in contours:
        # Calculate the contour length
        contour_length = cv2.arcLength(contour, True)

        # Check if the contour is a thin long shape
        if contour_length > min_contour_length:
            # Add the contour to the big_array
            # Convert the contour to a frame
            contour_frame = np.zeros_like(frame)
            cv2.drawContours(contour_frame, [contour], -1, (255, 255, 255), thickness=cv2.FILLED)
            print(contour_frame)

            # Add the contour frame to the big_array
            if big_array is None:
                big_array = contour_frame
            big_array = cv2.add(big_array, contour_frame/100)
            # Draw an outline around the shape
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)


    # Display the frame with the outlined shapes
    cv2.imshow("Thin Long Shape Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break



# Release the video capture and close the windows
cap.release()
cv2.destroyAllWindows()

# Display big_array as an image
cv2.imshow("Big Array", big_array)
cv2.waitKey(0)
cv2.destroyAllWindows()