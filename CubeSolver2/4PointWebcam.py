import cv2
import numpy as np

# List to store the points
points = []

# Mouse callback function to capture points
def draw_circle(event, x, y, flags, param):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 4:
            points.append((x, y))
        else:
            points.clear()
            points.append((x, y))


# Initialize the webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cv2.namedWindow('Webcam')
cv2.setMouseCallback('Webcam', draw_circle)

print("Click on the video feed to select points in the order of top-left, top-right, bottom-left, bottom-right.")

# Counter for naming saved images
counter = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    img = frame.copy()

    # Draw existing points
    for point in points:
        cv2.circle(img, point, 5, (0, 0, 255), -1)

    # If we have 4 points, draw the perspective square, grid lines, and inner squares
    if len(points) == 4:
        # Draw the perspective square
        '''
        cv2.line(img, points[0], points[1], (255, 0, 0), 2)
        cv2.line(img, points[1], points[3], (255, 0, 0), 2)
        cv2.line(img, points[3], points[2], (255, 0, 0), 2)
        cv2.line(img, points[2], points[0], (255, 0, 0), 2)
        '''
        # Calculate the 1/3 and 2/3 points along the top and bottom lines
        top_third1 = (
            int(points[0][0] + (points[1][0] - points[0][0]) / 3),
            int(points[0][1] + (points[1][1] - points[0][1]) / 3)
        )
        top_third2 = (
            int(points[0][0] + 2 * (points[1][0] - points[0][0]) / 3),
            int(points[0][1] + 2 * (points[1][1] - points[0][1]) / 3)
        )

        bottom_third1 = (
            int(points[2][0] + (points[3][0] - points[2][0]) / 3),
            int(points[2][1] + (points[3][1] - points[2][1]) / 3)
        )
        bottom_third2 = (
            int(points[2][0] + 2 * (points[3][0] - points[2][0]) / 3),
            int(points[2][1] + 2 * (points[3][1] - points[2][1]) / 3)
        )

        # Draw vertical grid lines
        cv2.line(img, top_third1, bottom_third1, (0, 255, 0), 2)
        cv2.line(img, top_third2, bottom_third2, (0, 255, 0), 2)

        # Calculate the 1/3 and 2/3 points along the left and right lines
        left_third1 = (
            int(points[0][0] + (points[2][0] - points[0][0]) / 3),
            int(points[0][1] + (points[2][1] - points[0][1]) / 3)
        )
        left_third2 = (
            int(points[0][0] + 2 * (points[2][0] - points[0][0]) / 3),
            int(points[0][1] + 2 * (points[2][1] - points[0][1]) / 3)
        )

        right_third1 = (
            int(points[1][0] + (points[3][0] - points[1][0]) / 3),
            int(points[1][1] + (points[3][1] - points[1][1]) / 3)
        )
        right_third2 = (
            int(points[1][0] + 2 * (points[3][0] - points[1][0]) / 3),
            int(points[1][1] + 2 * (points[3][1] - points[1][1]) / 3)
        )

        # Draw horizontal grid lines
        cv2.line(img, left_third1, right_third1, (0, 255, 0), 2)
        cv2.line(img, left_third2, right_third2, (0, 255, 0), 2)

        # Draw 32x32 pixel squares inside each cell of the 3x3 grid
        square_size = 32


        def interpolate(p1, p2, t):
            """Interpolate between points p1 and p2 by a factor of t."""
            return (int(p1[0] + t * (p2[0] - p1[0])), int(p1[1] + t * (p2[1] - p1[1])))


        # Loop over the 3x3 grid cells
        for i in range(3):
            for j in range(3):
                # Interpolate to find the corners of the current grid cell
                top_left = interpolate(interpolate(points[0], points[2], i / 3),
                                       interpolate(points[1], points[3], i / 3), j / 3)
                top_right = interpolate(interpolate(points[0], points[2], i / 3),
                                        interpolate(points[1], points[3], i / 3), (j + 1) / 3)
                bottom_left = interpolate(interpolate(points[0], points[2], (i + 1) / 3),
                                          interpolate(points[1], points[3], (i + 1) / 3), j / 3)
                bottom_right = interpolate(interpolate(points[0], points[2], (i + 1) / 3),
                                           interpolate(points[1], points[3], (i + 1) / 3), (j + 1) / 3)

                # Find the center of the current cell
                center_x = (top_left[0] + top_right[0] + bottom_left[0] + bottom_right[0]) // 4
                center_y = (top_left[1] + top_right[1] + bottom_left[1] + bottom_right[1]) // 4

                # Top-left corner of the small square
                top_left_x = center_x - square_size // 2
                top_left_y = center_y - square_size // 2

                # Bottom-right corner of the small square
                bottom_right_x = top_left_x + square_size
                bottom_right_y = top_left_y + square_size

                # Draw the small square centered at the center of the current cell
                #cv2.rectangle(img, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (0, 0, 255), 1)

                if top_left_x >= 0 and top_left_y >= 0 and bottom_right_x <= img.shape[1] and bottom_right_y <= \
                        img.shape[0]:
                    roi = img[top_left_y:bottom_right_y, top_left_x:bottom_right_x]
                    cv2.imwrite(f'roi_{counter}.png', roi)
                    counter += 1

                # Extract and save the region inside the small square


    # Display the frame with drawings
    cv2.imshow('Webcam', img)

    # Break the loop on 'ESC' key press
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break



# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
