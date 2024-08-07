import cv2
import numpy as np

# List to store the points
points = []


# Mouse callback function to capture points
def draw_circle(event, x, y, flags, param):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 12:  # 3 grids, 4 points each
            points.append((x, y))
        else:
            points.clear()
            points.append((x, y))


# Initialize the webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cv2.namedWindow('Webcam')
cv2.setMouseCallback('Webcam', draw_circle)

print(
    "Click on the video feed to select points in the order of top-left, top-right, bottom-left, bottom-right for each grid (3 sets of 4 points).")

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

    # Draw grids if we have 4 points for each grid (total 12 points)
    if len(points) == 12:
        # Labels for each grid
        grid_labels = ['U', 'L', 'R']

        for grid_index in range(3):  # 3 grids
            # Get the 4 points for the current grid
            grid_points = points[grid_index * 4:(grid_index + 1) * 4]
            grid_label = grid_labels[grid_index]

            # Draw the perspective square
            cv2.line(img, grid_points[0], grid_points[1], (255, 0, 0), 2)
            cv2.line(img, grid_points[1], grid_points[3], (255, 0, 0), 2)
            cv2.line(img, grid_points[3], grid_points[2], (255, 0, 0), 2)
            cv2.line(img, grid_points[2], grid_points[0], (255, 0, 0), 2)

            # Calculate the 1/3 and 2/3 points along the top and bottom lines
            top_third1 = (
                int(grid_points[0][0] + (grid_points[1][0] - grid_points[0][0]) / 3),
                int(grid_points[0][1] + (grid_points[1][1] - grid_points[0][1]) / 3)
            )
            top_third2 = (
                int(grid_points[0][0] + 2 * (grid_points[1][0] - grid_points[0][0]) / 3),
                int(grid_points[0][1] + 2 * (grid_points[1][1] - grid_points[0][1]) / 3)
            )

            bottom_third1 = (
                int(grid_points[2][0] + (grid_points[3][0] - grid_points[2][0]) / 3),
                int(grid_points[2][1] + (grid_points[3][1] - grid_points[2][1]) / 3)
            )
            bottom_third2 = (
                int(grid_points[2][0] + 2 * (grid_points[3][0] - grid_points[2][0]) / 3),
                int(grid_points[2][1] + 2 * (grid_points[3][1] - grid_points[2][1]) / 3)
            )

            # Draw vertical grid lines
            cv2.line(img, top_third1, bottom_third1, (0, 255, 0), 2)
            cv2.line(img, top_third2, bottom_third2, (0, 255, 0), 2)

            # Calculate the 1/3 and 2/3 points along the left and right lines
            left_third1 = (
                int(grid_points[0][0] + (grid_points[2][0] - grid_points[0][0]) / 3),
                int(grid_points[0][1] + (grid_points[2][1] - grid_points[0][1]) / 3)
            )
            left_third2 = (
                int(grid_points[0][0] + 2 * (grid_points[2][0] - grid_points[0][0]) / 3),
                int(grid_points[0][1] + 2 * (grid_points[2][1] - grid_points[0][1]) / 3)
            )

            right_third1 = (
                int(grid_points[1][0] + (grid_points[3][0] - grid_points[1][0]) / 3),
                int(grid_points[1][1] + (grid_points[3][1] - grid_points[1][1]) / 3)
            )
            right_third2 = (
                int(grid_points[1][0] + 2 * (grid_points[3][0] - grid_points[1][0]) / 3),
                int(grid_points[1][1] + 2 * (grid_points[3][1] - grid_points[1][1]) / 3)
            )

            # Draw horizontal grid lines
            cv2.line(img, left_third1, right_third1, (0, 255, 0), 2)
            cv2.line(img, left_third2, right_third2, (0, 255, 0), 2)

            # Draw 10x10 pixel squares inside each cell of the 3x3 grid
            square_size = 10


            def interpolate(p1, p2, t):
                """Interpolate between points p1 and p2 by a factor of t."""
                return (int(p1[0] + t * (p2[0] - p1[0])), int(p1[1] + t * (p2[1] - p1[1])))


            # Loop over the 3x3 grid cells
            for i in range(3):
                for j in range(3):
                    # Interpolate to find the corners of the current grid cell
                    top_left = interpolate(interpolate(grid_points[0], grid_points[2], i / 3),
                                           interpolate(grid_points[1], grid_points[3], i / 3), j / 3)
                    top_right = interpolate(interpolate(grid_points[0], grid_points[2], i / 3),
                                            interpolate(grid_points[1], grid_points[3], i / 3), (j + 1) / 3)
                    bottom_left = interpolate(interpolate(grid_points[0], grid_points[2], (i + 1) / 3),
                                              interpolate(grid_points[1], grid_points[3], (i + 1) / 3), j / 3)
                    bottom_right = interpolate(interpolate(grid_points[0], grid_points[2], (i + 1) / 3),
                                               interpolate(grid_points[1], grid_points[3], (i + 1) / 3), (j + 1) / 3)

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
                    cv2.rectangle(img, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (0, 0, 255), 1)

                    # Extract and save the region inside the small square
                    if top_left_x >= 0 and top_left_y >= 0 and bottom_right_x <= img.shape[1] and bottom_right_y <= \
                            img.shape[0]:
                        roi = img[top_left_y:bottom_right_y, top_left_x:bottom_right_x]
                        filename = f'{1}-{grid_index + 1}-{grid_label}{3 * i + j + 1}.png'
                        cv2.imwrite(filename, roi)

    # Display the frame with drawings
    cv2.imshow('Webcam', img)

    # Break the loop on 'ESC' key press
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Release the capture and close windows
cap.release()
cv2.destroyAllWindows()
