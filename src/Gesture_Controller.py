# # Imports
# import cv2
# import mediapipe as mp
# import pyautogui
# import math
# from enum import IntEnum
# from ctypes import cast, POINTER
# from comtypes import CLSCTX_ALL
# from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
# from google.protobuf.json_format import MessageToDict
# import screen_brightness_control as sbcontrol

# pyautogui.FAILSAFE = False
# mp_drawing = mp.solutions.drawing_utils
# mp_hands = mp.solutions.hands

# # Gesture Encodings
# def gest_control():
#     class Gest(IntEnum):
#         FIST = 0
#         PINKY = 1
#         RING = 2
#         MID = 4
#         LAST3 = 7
#         INDEX = 8
#         FIRST2 = 12
#         LAST4 = 15
#         THUMB = 16    
#         PALM = 31
#         V_GEST = 33
#         TWO_FINGER_CLOSED = 34
#         PINCH_MAJOR = 35
#         PINCH_MINOR = 36

#     class HLabel(IntEnum):
#         MINOR = 0
#         MAJOR = 1

#     class HandRecog:
#         def __init__(self, hand_label):
#             self.finger = 0
#             self.ori_gesture = Gest.PALM
#             self.prev_gesture = Gest.PALM
#             self.frame_count = 0
#             self.hand_result = None
#             self.hand_label = hand_label
    
#         def update_hand_result(self, hand_result):
#             self.hand_result = hand_result

#         def get_signed_dist(self, point):
#             sign = -1
#             if self.hand_result.landmark[point[0]].y < self.hand_result.landmark[point[1]].y:
#                 sign = 1
#             dist = (self.hand_result.landmark[point[0]].x - self.hand_result.landmark[point[1]].x)**2
#             dist += (self.hand_result.landmark[point[0]].y - self.hand_result.landmark[point[1]].y)**2
#             dist = math.sqrt(dist)
#             return dist*sign
    
#         def get_dist(self, point):
#             dist = (self.hand_result.landmark[point[0]].x - self.hand_result.landmark[point[1]].x)**2
#             dist += (self.hand_result.landmark[point[0]].y - self.hand_result.landmark[point[1]].y)**2
#             dist = math.sqrt(dist)
#             return dist
    
#         def get_dz(self,point):
#             return abs(self.hand_result.landmark[point[0]].z - self.hand_result.landmark[point[1]].z)

#         def set_finger_state(self):
#             if self.hand_result == None:
#                 return

#             points = [[8,5,0],[12,9,0],[16,13,0],[20,17,0]]
#             self.finger = 0
#             for idx,point in enumerate(points):
#                 dist = self.get_signed_dist(point[:2])
#                 dist2 = self.get_signed_dist(point[1:])
#                 try:
#                     ratio = round(dist/dist2,1)
#                 except:
#                     ratio = round(dist/0.01,1)
#                 self.finger = self.finger << 1
#                 if ratio > 0.5 :
#                     self.finger = self.finger | 1
    
#         def get_gesture(self):
#             if self.hand_result == None:
#                 return Gest.PALM

#             current_gesture = Gest.PALM

#             # Detect pinch gestures
#             if self.finger in [Gest.LAST3,Gest.LAST4] and self.get_dist([8,4]) < 0.12:
#                 if self.hand_label == HLabel.MINOR :
#                     current_gesture = Gest.PINCH_MINOR
#                 else:
#                     current_gesture = Gest.PINCH_MAJOR
#             elif Gest.FIRST2 == self.finger :
#                 point = [[8,12],[5,9]]
#                 dist1 = self.get_dist(point[0])
#                 dist2 = self.get_dist(point[1])
#                 ratio = dist1/dist2
#                 if ratio > 1.7:
#                     current_gesture = Gest.V_GEST
#                 else:
#                     if self.get_dz([8,12]) < 0.1:
#                         current_gesture =  Gest.TWO_FINGER_CLOSED
#                     else:
#                         current_gesture =  Gest.MID
#             else:
#                 current_gesture =  self.finger
        
#             if current_gesture == self.prev_gesture:
#                 self.frame_count += 1
#             else:
#                 self.frame_count = 0

#             self.prev_gesture = current_gesture

#             if self.frame_count > 4 :
#                 self.ori_gesture = current_gesture
#             return self.ori_gesture

#     class Controller:
#         tx_old = 0
#         ty_old = 0
#         trial = True
#         flag = False
#         grabflag = False
#         pinchmajorflag = False
#         pinchminorflag = False
#         pinchstartxcoord = None
#         pinchstartycoord = None
#         pinchdirectionflag = None
#         prevpinchlv = 0
#         pinchlv = 0
#         framecount = 0
#         prev_hand = None
#         pinch_threshold = 0.03

#         def getpinchylv(hand_result):
#             dist = round((Controller.pinchstartycoord - hand_result.landmark[8].y)*10,1)
#             return dist

#         def getpinchxlv(hand_result):
#             dist = round((hand_result.landmark[8].x - Controller.pinchstartxcoord)*10,1)
#             return dist
    
#         def changesystembrightness():
#             brightness_value = sbcontrol.get_brightness(display=0)
#             if isinstance(brightness_value, list) and len(brightness_value) > 0:
#                 brightness_value = float(brightness_value[0])
#             else:
#                 brightness_value = float(brightness_value)
#             currentBrightnessLv = brightness_value / 100.0
#             currentBrightnessLv += Controller.pinchlv / 50.0
#             currentBrightnessLv = max(0.0, min(1.0, currentBrightnessLv))
#             sbcontrol.fade_brightness(int(100 * currentBrightnessLv), start=int(brightness_value))
    
#         def changesystemvolume():
#             devices = AudioUtilities.GetSpeakers()
#             interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
#             volume = cast(interface, POINTER(IAudioEndpointVolume))
#             currentVolumeLv = volume.GetMasterVolumeLevelScalar()
#             currentVolumeLv += Controller.pinchlv/50.0
#             currentVolumeLv = max(0.0, min(1.0, currentVolumeLv))
#             volume.SetMasterVolumeLevelScalar(currentVolumeLv, None)
    
#         # --------- SCROLL ------------------
#         def scrollVertical():
#             pyautogui.scroll(int(Controller.pinchlv * 100))  # scroll up/down, no Ctrl pressed
        
#         def scrollHorizontal():
#             pyautogui.keyDown('shift')
#             pyautogui.scroll(int(Controller.pinchlv * 100))  # horizontal scroll using Shift
#             pyautogui.keyUp('shift')

#         def get_position(hand_result):
#             point = 9
#             position = [hand_result.landmark[point].x ,hand_result.landmark[point].y]
#             sx,sy = pyautogui.size()
#             x_old,y_old = pyautogui.position()
#             x = int(position[0]*sx)
#             y = int(position[1]*sy)
#             if Controller.prev_hand is None:
#                 Controller.prev_hand = x,y
#             delta_x = x - Controller.prev_hand[0]
#             delta_y = y - Controller.prev_hand[1]
#             distsq = delta_x**2 + delta_y**2
#             ratio = 1
#             Controller.prev_hand = [x,y]
#             if distsq <= 25:
#                 ratio = 0
#             elif distsq <= 900:
#                 ratio = 0.07 * (distsq ** (1/2))
#             else:
#                 ratio = 2.1
#             x , y = x_old + delta_x*ratio , y_old + delta_y*ratio
#             return (x,y)

#         def pinch_control_init(hand_result):
#             Controller.pinchstartxcoord = hand_result.landmark[8].x
#             Controller.pinchstartycoord = hand_result.landmark[8].y
#             Controller.pinchlv = 0
#             Controller.prevpinchlv = 0
#             Controller.framecount = 0

#         def pinch_control(hand_result, controlHorizontal, controlVertical):
#             lvx =  Controller.getpinchxlv(hand_result)
#             lvy =  Controller.getpinchylv(hand_result)
            
#             # Determine scroll/volume direction
#             if abs(lvy) > abs(lvx) and abs(lvy) > Controller.pinch_threshold:
#                 Controller.pinchdirectionflag = False
#                 Controller.pinchlv = lvy
#             elif abs(lvx) > Controller.pinch_threshold:
#                 Controller.pinchdirectionflag = True
#                 Controller.pinchlv = lvx
#             else:
#                 return

#             Controller.framecount += 1
#             if Controller.framecount >= 5:
#                 if Controller.pinchdirectionflag:
#                     controlHorizontal()
#                 else:
#                     controlVertical()
#                 Controller.framecount = 0

#         def handle_controls(gesture, hand_result, is_left_hand=False):
#             x,y = None,None
#             if gesture != Gest.PALM :
#                 x,y = Controller.get_position(hand_result)
        
#             if gesture != Gest.FIST and Controller.grabflag:
#                 Controller.grabflag = False
#                 pyautogui.mouseUp(button = "left")

#             if gesture != Gest.PINCH_MAJOR and Controller.pinchmajorflag:
#                 Controller.pinchmajorflag = False

#             if gesture != Gest.PINCH_MINOR and Controller.pinchminorflag:
#                 Controller.pinchminorflag = False

#             if gesture == Gest.V_GEST:
#                 Controller.flag = True
#                 pyautogui.moveTo(x, y, duration = 0.1)

#             elif gesture == Gest.FIST:
#                 if not Controller.grabflag : 
#                     Controller.grabflag = True
#                     pyautogui.mouseDown(button = "left")
#                 pyautogui.moveTo(x, y, duration = 0.1)

#             elif gesture == Gest.MID and Controller.flag:
#                 pyautogui.click()
#                 Controller.flag = False

#             elif gesture == Gest.INDEX and Controller.flag:
#                 pyautogui.click(button='right')
#                 Controller.flag = False

#             elif gesture == Gest.TWO_FINGER_CLOSED and Controller.flag:
#                 pyautogui.doubleClick()
#                 Controller.flag = False

#             # ----------------- PINCH HANDLING -----------------
#             if gesture in [Gest.PINCH_MINOR, Gest.PINCH_MAJOR]:
#                 if is_left_hand:  # Left-hand → scroll
#                     if Controller.pinchminorflag == False:
#                         Controller.pinch_control_init(hand_result)
#                         Controller.pinchminorflag = True
#                     Controller.pinch_control(
#                         hand_result,
#                         Controller.scrollHorizontal,
#                         Controller.scrollVertical
#                     )
#                 else:             # Right-hand → brightness/volume
#                     if Controller.pinchmajorflag == False:
#                         Controller.pinch_control_init(hand_result)
#                         Controller.pinchmajorflag = True
#                     Controller.pinch_control(
#                         hand_result,
#                         Controller.changesystembrightness,
#                         Controller.changesystemvolume
#                     )

#     class GestureController:
#         gc_mode = 0
#         cap = None
#         CAM_HEIGHT = None
#         CAM_WIDTH = None
#         hr_major = None
#         hr_minor = None
#         dom_hand = True

#         def __init__(self):
#             GestureController.gc_mode = 1
#             GestureController.cap = cv2.VideoCapture(0)
#             GestureController.CAM_HEIGHT = GestureController.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
#             GestureController.CAM_WIDTH = GestureController.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    
#         def classify_hands(results):
#             left , right = None,None
#             try:
#                 handedness_dict = MessageToDict(results.multi_handedness[0])
#                 if handedness_dict['classification'][0]['label'] == 'Right':
#                     right = results.multi_hand_landmarks[0]
#                 else:
#                     left = results.multi_hand_landmarks[0]
#             except:
#                 pass

#             try:
#                 handedness_dict = MessageToDict(results.multi_handedness[1])
#                 if handedness_dict['classification'][0]['label'] == 'Right':
#                     right = results.multi_hand_landmarks[1]
#                 else:
#                     left = results.multi_hand_landmarks[1]
#             except:
#                 pass
        
#             if GestureController.dom_hand == True:
#                 GestureController.hr_major = right
#                 GestureController.hr_minor = left
#             else :
#                 GestureController.hr_major = left
#                 GestureController.hr_minor = right

#         def start(self):
#             handmajor = HandRecog(HLabel.MAJOR)
#             handminor = HandRecog(HLabel.MINOR)

#             with mp_hands.Hands(max_num_hands = 2,min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
#                 while GestureController.cap.isOpened() and GestureController.gc_mode:
#                     success, image = GestureController.cap.read()
#                     if not success:
#                         print("Ignoring empty camera frame.")
#                         continue
                
#                     image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
#                     image.flags.writeable = False
#                     results = hands.process(image)
#                     image.flags.writeable = True
#                     image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

#                     if results.multi_hand_landmarks:                   
#                         GestureController.classify_hands(results)
#                         handmajor.update_hand_result(GestureController.hr_major)
#                         handminor.update_hand_result(GestureController.hr_minor)

#                         handmajor.set_finger_state()
#                         handminor.set_finger_state()

#                         # Handle left hand first
#                         if handminor.hand_result:
#                             gest_name_minor = handminor.get_gesture()
#                             Controller.handle_controls(gest_name_minor, handminor.hand_result, is_left_hand=True)

#                         # Handle right hand
#                         if handmajor.hand_result:
#                             gest_name_major = handmajor.get_gesture()
#                             Controller.handle_controls(gest_name_major, handmajor.hand_result, is_left_hand=False)
                    
#                         for hand_landmarks in results.multi_hand_landmarks:
#                             mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
#                     else:
#                         Controller.prev_hand = None
                        
#                     cv2.imshow('Gesture Controller', image)
#                     if cv2.waitKey(5) & 0xFF == 13:
#                         break

#             GestureController.cap.release()
#             cv2.destroyAllWindows()

#     gc1 = GestureController()
#     gc1.start()

# # Run the gesture controller
# #gest_control()


# Imports
import cv2
import mediapipe as mp
import pyautogui
import math
from enum import IntEnum
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from google.protobuf.json_format import MessageToDict
import screen_brightness_control as sbcontrol

pyautogui.FAILSAFE = False
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands


def gest_control():

    class Gest(IntEnum):
        FIST = 0
        MID = 4
        INDEX = 8
        FIRST2 = 12
        LAST3 = 7
        LAST4 = 15
        PALM = 31
        V_GEST = 33
        TWO_FINGER_CLOSED = 34
        PINCH_MAJOR = 35
        PINCH_MINOR = 36

    class HLabel(IntEnum):
        MINOR = 0
        MAJOR = 1

    class HandRecog:
        def __init__(self, label):
            self.finger = 0
            self.prev = Gest.PALM
            self.stable = Gest.PALM
            self.count = 0
            self.hand = None
            self.label = label

        def update(self, hand):
            self.hand = hand

        def dist(self, p):
            return math.hypot(
                self.hand.landmark[p[0]].x - self.hand.landmark[p[1]].x,
                self.hand.landmark[p[0]].y - self.hand.landmark[p[1]].y
            )

        def dz(self, p):
            return abs(self.hand.landmark[p[0]].z - self.hand.landmark[p[1]].z)

        def set_finger(self):
            self.finger = 0
            tips = [[8,5],[12,9],[16,13],[20,17]]
            for t in tips:
                self.finger <<= 1
                if self.dist([t[0],0]) > self.dist([t[1],0]):
                    self.finger |= 1

        def gesture(self):
            g = Gest.PALM
            if self.finger in [Gest.LAST3, Gest.LAST4] and self.dist([8,4]) < 0.12:
                g = Gest.PINCH_MAJOR if self.label == HLabel.MAJOR else Gest.PINCH_MINOR
            elif self.finger == Gest.FIRST2:
                g = Gest.V_GEST
            else:
                g = self.finger

            if g == self.prev:
                self.count += 1
            else:
                self.count = 0

            self.prev = g
            if self.count > 4:
                self.stable = g
            return self.stable

    class Controller:
        exit_flag = False
        exit_frames = 0

        @staticmethod
        def handle_exit(gesture, hand):
            if gesture == Gest.PINCH_MAJOR:
                dx = abs(hand.landmark[8].x - hand.landmark[4].x)
                dy = abs(hand.landmark[8].y - hand.landmark[4].y)
                dz = abs(hand.landmark[8].z - hand.landmark[4].z)

                if dx < 0.02 and dy < 0.02 and dz < 0.02:
                    Controller.exit_frames += 1
                else:
                    Controller.exit_frames = 0
            else:
                Controller.exit_frames = 0

            if Controller.exit_frames > 20:
                Controller.exit_flag = True

    class GestureController:
        def __init__(self):
            self.cap = cv2.VideoCapture(0)

        def start(self):
            major = HandRecog(HLabel.MAJOR)

            with mp_hands.Hands(
                max_num_hands=1,
                min_detection_confidence=0.6,
                min_tracking_confidence=0.6
            ) as hands:

                while self.cap.isOpened():
                    ret, frame = self.cap.read()
                    if not ret:
                        break

                    frame = cv2.flip(frame, 1)
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    res = hands.process(rgb)

                    if res.multi_hand_landmarks:
                        hand = res.multi_hand_landmarks[0]
                        major.update(hand)
                        major.set_finger()
                        g = major.gesture()

                        Controller.handle_exit(g, hand)
                        mp_drawing.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

                    cv2.imshow("Gesture Controller", frame)

                    if Controller.exit_flag:
                        break

                    if cv2.waitKey(1) & 0xFF == 27:
                        break

            self.cap.release()
            cv2.destroyAllWindows()

    GestureController().start()


gest_control()



