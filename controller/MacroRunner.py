class MacroRunner:
    def __init__(self, macro_file_path):
        self.state = 'q0'
        self.macro_file_path = macro_file_path

    def run(self):
        with open(self.macro_file_path) as macro_file:
            actions = [item for sub_list in [el.split() for el in macro_file.readlines()] for item in sub_list]

            for action in actions:
                if self.state == 'q0':  # Robot without package
                    if action == 'go_to':  # Go to
                        print("Going to (without parcel):", end=" ")

                        self.state = 'q2'
                    elif action == 'pick_up':  # Pick up
                        print("Picking up:", end=" ")

                        self.state = 'q1'
                elif self.state == 'q1':  # Robot waiting for parcel id
                    letter = action
                    print(letter)
                    print(f"Sending: picking up parcel: {letter}")
                    print("-------------------------------------")

                    self.state = 'q3'
                elif self.state == 'q2':  # Robot waiting for "direction" without parcel
                    letter = action
                    print(letter)
                    print(f"Sending command: going to {letter}")
                    print("---------------------------")

                    self.state = 'q0'
                elif self.state == 'q3':  # Robot with package
                    if action == 'drop_down':  # Drop down
                        print("Sending command: drop down parcel")
                        print("---------------------------------")

                        self.state = 'q0'
                    elif action == 'go_to':  # Go to
                        print("Going to (with parcel):", end=" ")

                        self.state = 'q4'
                elif self.state == 'q4':  # Robot waiting for "direction" with parcel
                    letter = action
                    print(letter)
                    print(f"Sending command: going to {letter}")
                    print("---------------------------")

                    self.state = 'q3'