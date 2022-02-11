from GestureDetector import GestureBuffer


class GestureController:
    def gesture_control(self, gesture_buffer: GestureBuffer):
        gesture_id = gesture_buffer.get_gesture()
        if gesture_id is not None:
            print("GESTURE: id:", gesture_id, end=" ")

            if gesture_id == 0:  # Forward
                print("--> Forward")
            elif gesture_id == 1:  # STOP
                print("--> Stop")
            if gesture_id == 5:  # Back
                print("--> Back")

            elif gesture_id == 2:  # UP
                print("--> Up")
            elif gesture_id == 4:  # DOWN
                print("--> Down")

            elif gesture_id == 3:  # LAND
                print("--> Land")

            elif gesture_id == 6:  # LEFT
                print("--> Left")
            elif gesture_id == 7:  # RIGHT
                print("--> Right")

            elif gesture_id == -1:
                print("--> Not recognized")
