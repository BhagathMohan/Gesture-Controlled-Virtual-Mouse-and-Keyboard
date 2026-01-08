import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
from time import sleep
import numpy as np
from pynput.keyboard import Controller
from collections import deque
import time

def vk_keyboard():
    try:
        cap = cv2.VideoCapture(0)
        cap.set(3, 1280)
        cap.set(4, 720)
        
        detector = HandDetector(detectionCon=0.8, maxHands=1)
        
        keyboard_keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
                         ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
                         ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]]
        
        # Add special keys row
        special_keys = ["SPACE", "CAPS", "ENTER", "BACK", "CLEAR"]
        
        # Caps lock state
        caps_lock_on = False
        
        final_text = ""
        keyboard_controller = Controller()
        
        # MOVED KEYBOARD UP - from y=350 to y=100
        # This keeps your hand in webcam vision
        buttonList = []
        for row_idx in range(len(keyboard_keys)):
            for col_idx, key in enumerate(keyboard_keys[row_idx]):
                buttonList.append({
                    'pos': (80 * col_idx + 60, 80 * row_idx + 100),  # MOVED UP SIGNIFICANTLY
                    'size': (70, 70),
                    'text': key
                })
        
        # Add special keys at bottom of keyboard (not at bottom of screen)
        special_y = 100 + len(keyboard_keys) * 80 + 10  # Just below main keyboard
        special_widths = [110, 90, 100, 90, 100]  # Custom widths for each special key
        x_offset = 60
        for idx, key in enumerate(special_keys):
            buttonList.append({
                'pos': (x_offset, special_y),
                'size': (special_widths[idx], 70),
                'text': key
            })
            x_offset += special_widths[idx] + 10  # 10px gap between keys
        
        # FIX 3: IMPROVED PINCH DETECTION with debouncing
        pinch_history = deque(maxlen=5)  # Track last 5 frames
        key_pressed = False
        last_key_time = 0
        key_cooldown = 0.25  # 250ms cooldown between presses
        
        # Smooth hand tracking
        index_history = deque(maxlen=3)
        
        # Visual feedback
        last_pressed_key = None
        last_pressed_time = 0
        
        print("Virtual Keyboard started. Press 'Q' to quit.")
        print("Instructions:")
        print("- Position your hand in the UPPER area of webcam")
        print("- Hover index finger over a key")
        print("- Pinch index and middle finger together to type")
        print("- CAPS: Toggle uppercase/lowercase")
        print("- ENTER: New line")
        print("- BACK: Delete last character")
        print("- CLEAR: Delete all text")
        
        while True:
            success, img = cap.read()
            
            if not success:
                print("Failed to read from camera")
                break
            
            # Use webcam feed as background
            img = cv2.flip(img, 1)
            img = cv2.resize(img, (1000, 600))
            
            # Detect hands
            hands, img = detector.findHands(img, draw=True, flipType=False)
            
            # Create semi-transparent overlay
            overlay = img.copy()
            
            current_time = time.time()
            hovered_button = None
            
            # Process hand detection FIRST to determine hovered button
            if hands and len(hands) > 0:
                hand = hands[0]
                lmList = hand.get("lmList", [])
                
                if lmList and len(lmList) >= 21:
                    index_tip = lmList[8]
                    middle_tip = lmList[12]
                    
                    # Smooth index finger position
                    index_history.append((index_tip[0], index_tip[1]))
                    if len(index_history) >= 2:
                        avg_x = sum(p[0] for p in index_history) / len(index_history)
                        avg_y = sum(p[1] for p in index_history) / len(index_history)
                        index_x, index_y = int(avg_x), int(avg_y)
                    else:
                        index_x, index_y = index_tip[0], index_tip[1]
                    
                    # Draw index finger indicator
                    cv2.circle(img, (index_x, index_y), 12, (0, 255, 0), -1)
                    cv2.circle(img, (index_x, index_y), 15, (255, 255, 255), 2)
                    
                    # Find which button is being hovered
                    for button in buttonList:
                        x, y = button['pos']
                        w, h = button['size']
                        
                        if x < index_x < x + w and y < index_y < y + h:
                            hovered_button = button
                            break
            
            # Draw all buttons with proper state
            for button in buttonList:
                x, y = button['pos']
                w, h = button['size']
                
                # FIX 1: Check if button position is valid
                if x >= 0 and y >= 0 and x + w < img.shape[1] and y + h < img.shape[0]:
                    
                    # Determine button state
                    is_pressed = (last_pressed_key == button['text'] and 
                                 current_time - last_pressed_time < 0.2)
                    is_hovered = (hovered_button == button)
                    is_caps = (button['text'] == 'CAPS' and caps_lock_on)
                    
                    # Choose color based on state
                    if is_pressed:
                        color = (0, 255, 0)  # Green when pressed
                    elif is_caps:
                        color = (0, 200, 0)  # Green when CAPS LOCK is ON
                    elif is_hovered:
                        color = (0, 255, 255)  # Yellow when hovered
                    else:
                        color = (255, 144, 30)  # Orange default
                    
                    # Draw button
                    cvzone.cornerRect(overlay, (x, y, w, h), 15, rt=0)
                    cv2.rectangle(overlay, (x, y), (x + w, y + h), color, cv2.FILLED)
                    
                    # Display button text with caps indicator
                    button_text = button['text']
                    
                    # Show lowercase for letter keys when caps is off
                    if len(button_text) == 1 and button_text.isalpha() and not caps_lock_on:
                        button_text = button_text.lower()
                    
                    # Adjust text size and position for different key types
                    if len(button['text']) > 2:
                        # Special keys (SPACE, BACK, CLEAR, CAPS, ENTER)
                        text_scale = 1.8 if button['text'] == 'SPACE' else 1.6
                        text_size = cv2.getTextSize(button_text, cv2.FONT_HERSHEY_PLAIN, text_scale, 2)[0]
                        text_x = x + (w - text_size[0]) // 2
                        text_y = y + (h + text_size[1]) // 2 + 5
                        cv2.putText(overlay, button_text, (text_x, text_y), 
                                   cv2.FONT_HERSHEY_PLAIN, text_scale, (0, 0, 0), 2)
                    else:
                        # Regular keys
                        cv2.putText(overlay, button_text, (x + 20, y + 50), 
                                   cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 3)
            
            # Blend overlay with original image
            img = cv2.addWeighted(overlay, 0.6, img, 0.4, 0)
            
            # Text display box - positioned at bottom but above edge
            text_box_y = 520  # Moved up a bit
            cv2.rectangle(img, (50, text_box_y), (850, text_box_y + 50), (255, 255, 255), cv2.FILLED)
            cv2.rectangle(img, (50, text_box_y), (850, text_box_y + 50), (200, 200, 200), 3)
            
            # Display typed text with scrolling (replace newlines with ↵ symbol for display)
            display_text = final_text.replace('\n', '↵')
            text_to_display = display_text[-35:] if len(display_text) > 35 else display_text
            cv2.putText(img, text_to_display, (60, text_box_y + 35), 
                       cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
            
            # Process pinch detection
            if hands and len(hands) > 0:
                hand = hands[0]
                lmList = hand.get("lmList", [])
                
                if lmList and len(lmList) >= 21:
                    index_tip = lmList[8]
                    middle_tip = lmList[12]
                    
                    # Smooth index position (already calculated above)
                    if len(index_history) >= 2:
                        avg_x = sum(p[0] for p in index_history) / len(index_history)
                        avg_y = sum(p[1] for p in index_history) / len(index_history)
                        index_x, index_y = int(avg_x), int(avg_y)
                    else:
                        index_x, index_y = index_tip[0], index_tip[1]
                    
                    # Check if hovering over any button
                    for button in buttonList:
                        x, y = button['pos']
                        w, h = button['size']
                        
                        if x < index_x < x + w and y < index_y < y + h:
                            try:
                                # FIX 3: IMPROVED PINCH DETECTION
                                length, info, img_with_line = detector.findDistance(
                                    (index_tip[0], index_tip[1]), 
                                    (middle_tip[0], middle_tip[1]), 
                                    img
                                )
                                
                                # Add to pinch history
                                is_pinching = length < 35
                                pinch_history.append(is_pinching)
                                
                                # Display pinch distance
                                mid_x = (index_tip[0] + middle_tip[0]) // 2
                                mid_y = (index_tip[1] + middle_tip[1]) // 2
                                status = "PINCH!" if is_pinching else f"{int(length)}px"
                                cv2.putText(img, status, (mid_x - 30, mid_y - 10),
                                           cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 0), 2)
                                
                                # Require majority vote from history (3 out of 5)
                                if len(pinch_history) >= 3:
                                    pinch_votes = sum(pinch_history)
                                    
                                    # FIX 3: Only register key press if:
                                    # 1. Majority agree it's a pinch (at least 3/5 frames)
                                    # 2. Not already pressed
                                    # 3. Cooldown period has passed
                                    if (pinch_votes >= 3 and 
                                        not key_pressed and 
                                        current_time - last_key_time >= key_cooldown):
                                        
                                        # Process the key press
                                        key_text = button['text']
                                        
                                        # Process different key types
                                        if key_text == "CAPS":
                                            # Toggle caps lock - no keyboard output needed
                                            caps_lock_on = not caps_lock_on
                                            print(f"Caps Lock: {'ON' if caps_lock_on else 'OFF'}")
                                            # Update state for CAPS
                                            key_pressed = True
                                            last_key_time = current_time
                                            last_pressed_key = key_text
                                            last_pressed_time = current_time
                                        
                                        elif key_text == "SPACE":
                                            keyboard_controller.press(' ')
                                            keyboard_controller.release(' ')
                                            final_text += ' '
                                            # Update state
                                            key_pressed = True
                                            last_key_time = current_time
                                            last_pressed_key = key_text
                                            last_pressed_time = current_time
                                            print(f"Key pressed: {key_text}")
                                        
                                        elif key_text == "ENTER":
                                            # Send Enter/Return key
                                            from pynput.keyboard import Key
                                            keyboard_controller.press(Key.enter)
                                            keyboard_controller.release(Key.enter)
                                            final_text += '\n'
                                            # Update state
                                            key_pressed = True
                                            last_key_time = current_time
                                            last_pressed_key = key_text
                                            last_pressed_time = current_time
                                            print(f"Key pressed: {key_text}")
                                        
                                        elif key_text == "BACK":
                                            if final_text:
                                                keyboard_controller.press('\b')
                                                keyboard_controller.release('\b')
                                                final_text = final_text[:-1]
                                            # Update state
                                            key_pressed = True
                                            last_key_time = current_time
                                            last_pressed_key = key_text
                                            last_pressed_time = current_time
                                            print(f"Key pressed: {key_text}")
                                        
                                        elif key_text == "CLEAR":
                                            # Send backspace for each character to clear text in external apps
                                            chars_to_delete = len(final_text)
                                            for _ in range(chars_to_delete):
                                                keyboard_controller.press('\b')
                                                keyboard_controller.release('\b')
                                            final_text = ""
                                            # Update state
                                            key_pressed = True
                                            last_key_time = current_time
                                            last_pressed_key = key_text
                                            last_pressed_time = current_time
                                            print(f"Key pressed: {key_text}")
                                        
                                        else:
                                            # Regular letter/character keys
                                            # Apply caps lock to letter keys only
                                            if key_text.isalpha():
                                                output_char = key_text.upper() if caps_lock_on else key_text.lower()
                                            else:
                                                output_char = key_text
                                            
                                            keyboard_controller.press(output_char)
                                            keyboard_controller.release(output_char)
                                            final_text += output_char
                                            # Update state
                                            key_pressed = True
                                            last_key_time = current_time
                                            last_pressed_key = key_text
                                            last_pressed_time = current_time
                                            print(f"Key pressed: {key_text}")
                                    
                                    # Release when fingers separate
                                    elif pinch_votes <= 1 and key_pressed:
                                        key_pressed = False
                                        pinch_history.clear()  # Clear history on release
                                
                            except Exception as e:
                                pass
                            
                            break  # Only process one button at a time
            
            # FIX 4: Better instructions display
            # Semi-transparent instruction box at top
            cv2.rectangle(img, (0, 0), (1000, 80), (0, 0, 0), -1)
            img[0:80, 0:1000] = cv2.addWeighted(img[0:80, 0:1000], 0.3, 
                                                 np.zeros_like(img[0:80, 0:1000]), 0.7, 0)
            
            cv2.putText(img, "VIRTUAL KEYBOARD - Press 'Q' to quit", (50, 25), 
                       cv2.FONT_HERSHEY_PLAIN, 1.8, (255, 255, 255), 2)
            cv2.putText(img, "Hover finger over key, then PINCH to type", (50, 50), 
                       cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 255), 2)
            
            # Show caps lock and typing status indicator
            status_text = ""
            if caps_lock_on:
                status_text = "CAPS ON"
                cv2.putText(img, status_text, (50, 75), 
                           cv2.FONT_HERSHEY_PLAIN, 1.3, (0, 255, 0), 2)
            if key_pressed:
                typing_x = 150 if caps_lock_on else 50
                cv2.putText(img, "TYPING...", (typing_x, 75), 
                           cv2.FONT_HERSHEY_PLAIN, 1.3, (0, 255, 0), 2)
            
            cv2.imshow("Virtual Keyboard", img)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q') or key == 27:
                break
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            cap.release()
            cv2.destroyAllWindows()
            print("Virtual Keyboard closed successfully!")
        except:
            pass

if __name__ == "__main__":
    vk_keyboard()