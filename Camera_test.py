import cv2
import numpy as np
import time

# Initialize the video capture object
videoCaptureObject = cv2.VideoCapture(0)

# Create a window for displaying video
cv2.namedWindow('Capturing Video', cv2.WINDOW_NORMAL)
cv2.setWindowProperty('Capturing Video', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Initialize variables for the LED circle
circle_radius = 3
circle_color = (0, 0, 255)  # Red color
circle_center = (25, 25)

# Initialize variables for LED blinking
blink_interval = 0.5  # Blink interval in seconds
last_blink_time = time.time()
circle_visible = True  # Flag for circle visibility

while True:
    ret, frame = videoCaptureObject.read()

    # Calculate time since the last blink
    current_time = time.time()
    time_since_last_blink = current_time - last_blink_time

    # Toggle circle visibility if the blink interval has passed
    if time_since_last_blink >= blink_interval:
        circle_visible = not circle_visible
        last_blink_time = current_time

    # Draw the blinking circle if it's visible
    if circle_visible:
        cv2.circle(frame, circle_center, circle_radius, circle_color, -1)

    # Display the frame
    cv2.imshow('Capturing Video', frame)

    # Check for the 'q' key press to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and destroy windows
videoCaptureObject.release()
cv2.destroyAllWindows()
