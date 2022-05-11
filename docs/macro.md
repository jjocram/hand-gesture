---
hide:
  - navigation
---
# Macro
Macros are sequence of commands pre-recorded. They are saved as text file in which each line represents a gesture done by the operator. You can create them writing the text file, or using the program while doing hand gestures.

## Create a new macro
### Using the program
1. Launch the script with the argument `--interactive`:
  ```bash
  python3 main.py --interactive
  ```
2. Choose the option `2 - Macro mode` (write `2` and press `enter`)
3. Choose the option `0 - Create a new macro`
4. Write the name for the new macro and press `enter`
5. Do the sequence of gesture you want to record. When you are done press `esc`

### Writing the text file
Create a text file and write the name of the gestures you want to save. One per line. The name of the gestures **must be** the same as those written in the automaton configuration file.

The following example show a macro that:

1. Pick up the parcel A
2. Go to the position B
3. Drop down the parcel

```
pick_up
a
go_to
b
drop_down
```

## Run a macro
1. Launch the script with the argument `--interactive`:
  ```bash
  python3 main.py --interactive
  ```
2. Choose the option `2 - Macro mode` (write `2` and press `enter`)
3. Choose the option `1 - Run an existent one`
4. Write the path of the text file and press `enter`

