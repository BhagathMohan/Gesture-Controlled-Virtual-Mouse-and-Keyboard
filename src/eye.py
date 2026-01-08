import cv2
import mediapipe as mp
import pyautogui
import time

def eye_move():
    cam = cv2.VideoCapture(0)
    face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
    screen_w, screen_h = pyautogui.size()

    last_click_time = 0
    CLICK_INTERVAL = 0.3  # Minimum interval between clicks
    BLINK_THRESHOLD = 0.015  # Easy blink detection

    # Track previous blink states to detect single blink events
    left_prev = False
    right_prev = False
    both_prev = False

    while True:
        _, frame = cam.read()
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = face_mesh.process(rgb_frame)
        landmark_points = output.multi_face_landmarks
        frame_h, frame_w, _ = frame.shape

        if landmark_points:
            landmarks = landmark_points[0].landmark
            for id, landmark in enumerate(landmarks[474:478]):
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 3, (0, 255, 0))

                if id == 1:
                    screen_x = screen_w * landmark.x
                    screen_y = screen_h * landmark.y
                    pyautogui.moveTo(screen_x, screen_y)

            # Left eye landmarks for blink detection
            left = [landmarks[145], landmarks[159]]
            # Right eye landmarks for blink detection
            right = [landmarks[374], landmarks[386]]

            for landmark in left:
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 3, (0, 255, 255))

            for landmark in right:
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 3, (255, 255, 0))

            # Calculate blink states
            left_blink = (left[0].y - left[1].y) < BLINK_THRESHOLD
            right_blink = (right[0].y - right[1].y) < BLINK_THRESHOLD
            current_time = time.time()

            # Both eyes blink → double click
            if left_blink and right_blink and not both_prev and (current_time - last_click_time) > CLICK_INTERVAL:
                pyautogui.doubleClick()
                last_click_time = current_time
                both_prev = True
            if not (left_blink and right_blink):
                both_prev = False

            # Left eye blink → left click
            if left_blink and not left_prev and not right_blink and (current_time - last_click_time) > CLICK_INTERVAL:
                pyautogui.click()
                last_click_time = current_time
            left_prev = left_blink

            # Right eye blink → right click
            if right_blink and not right_prev and not left_blink and (current_time - last_click_time) > CLICK_INTERVAL:
                pyautogui.rightClick()
                last_click_time = current_time
            right_prev = right_blink

        cv2.imshow('Eye Controlled Mouse', frame)
        if cv2.waitKey(1) == 113:  # Press 'q' to quit
            break

    cam.release()
    cv2.destroyAllWindows()
