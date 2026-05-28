# A line editor for GHOST - WIP

## Initialization

1. Set up a dynamically allocated array for the lines of the file: The Line Array
2. Read the file into a buffer of size
    a. As you read the file, each time you encounter a newline, put that *pointer* into the Line Array, and replace the 0xa char with a 0/null
3. Set up a second, empty array to keep track of lines in dynamic memory: The Live Array
4. Set "Unsaved Changes" to false.
    a. While it would be possible to keep track of which lines had changes, any line *after* any changed lines will need to be re-writen as file length changes, so there'd be no gain

## De-init

1. Free all in Live Array
2. Free both malloc'd arrays

## Notes

+ Ctrl+C should be able to escape any command, at any stage, safely. This means that commands should wait to take action until after 'enter' is pressed. For example, `Change` should postpone deleting the old line until the end.
+ For ranged index, the order shoud be enforced, i.e. that the largest is greater than the lowest.
+ Possible, the syntax N,N-N could be allowed, providing a way to combine ranged and single line selection. Initially only single lines will be implemented, ranges and arrays second, then mixed if decided.

## Commands

### Print `p`

If no lines are given, prints the whole file. Also accepts a single line `N` or a line range `N-N` or a line array `N,N,N`.
By default, it will print line numbers `I: `. Due to limitations in whitespace/string handling in the shell at this time, this is unconfigurable for the time being.

### Append `a`

The Append command opens a new line after the selected line. Unlike many other commands, 0 is allowed
Once 'enter' is pressed, alloc a new buffer and copy in the new text. Insert the pointer to this new line into the Line Array.

### Delete `d`

Remove the given line/lines by removing given indexes from the Line Array.
Find the index of the line to be deleted, and remove it (shifting down the array as needed). If this pointer is in the Live Array, it should be freed and removed.

### Change `c`

Changes the given line.
Once enter is pressed, follow the 'append' instructions to create a new buffer and copy the string to it. Replace the old line index with the new one. If the old one was in the Live Array, free it.

### Save `s` and Save As `S`

A lowercase s will save the file to the same name that it was opened with OR to the name it was last saved with, if 'Save As' was previously used.
An uppercase S will open an editor line, allowing for a save name to be entered.
Reconstruct the file from the Line Array, writing it line by line to he file.

### Edit `e`

Opens an editor line, allowing for a file name to be entered to open. All program memory is freed, and state is reset. The file is opened.

### Quit `q`

Quit the editor. Prompt before exiting if there are unsaved changes.

### Help `h`

Prints the help file.

## Optional Commands

### Join `j`

Join two lines.

### Undo `u`

Undoes the last change

### Mark `m`

Marks the given line, allowing it to be refered to as simple 'm' in future commands

## Program State

bool UnsavedChanges
vector<ptr> Line Array
vector<ptr> Live Array

## Usage Example

> p
> 1:Line 1
> 2:Line 3
> a1
> Line 2
> p
> 1:Line 1
> 2:Line 2
> 3:Line 3

## Notes & todo

- [ ] Need command to check file length

- [ ] Backspace support

- [ ] More error checking in number inputs

```
yield line:
10,14-15,17

; R1 -> pointer to first value
; R0 <- value
fetch_value:
    ; Add values to R1 until
    RET

yield_line:
    if final_value != 0xffff:
        JMP yield_line_range
    call fetch_value -> cur_value
    if next_char==comma:
        if first_value != 0xffff:
            return cur_value
        else:
            final_value = cur_value
            return inital_value

    if next_char==dash:
        inital_value = cur_value
        JMP yield_line

    if next_char==null:
        done = true
        return cur_value

    JMP invalid_char

    yield_line_range:
        if first_value != final_value:
            first_value +=1
        else:
            initial_value = 0xffff
            final_value = 0xffff
        return first_value

line_pointer: .db 0
first_value: .db 0xffff
final_value: .db 0xffff
done:        .db 0
```
