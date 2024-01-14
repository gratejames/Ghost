# TODO
+ [x] Add project to git(hub)
# Glossary
Register:           R0,R1,R2,R3                             , store into
\$Register:          The value that the register points to   , store at
Address:            Information at an address
Value:              A value given immediately

# Memory Map
Free:  0x0000 - 0xaeff ( 44799 Bytes )
I/O:   0xaf00 - 0xafff (   256 Bytes )
Video: 0xb000 - 0xefff ( 16384 Bytes )
Stack: 0xf000 - 0xffff (  4096 Bytes )

## I/O
0x00-0x5f: Interrupt Table
0x60-0x7f: Unused
0x80-0x8f: Display Pallet
0x90-0xfd: Unused
0xfe: Display settings
0xff: Random Number

### Interrupt Table
#### 0x00: Key Status Change                     Done
	Push all
	Push key code. Refer [[Ghost Keycodes]]
	Push event (0: up, 1: down)
#### 0x01: Mouse Position Change                 NYI
	Push all
	Push MouseX position (absolute to window)
	Push MouseY position (absolute to window)
#### 0x02: Mouse Button Change                   NYI
	Push all
	Push button number
	Push event (0: up, 1: down)
#### 0x4f-5f: User defined, not called by hardware. Convention below.
#### 0x5e: High Res. String Print
	0x70: String Address
	0x71: X Start Position
	0x72: Y Position
	0x73: Font Address
#### 0x5f: High Res. Character Print
	0x70: Char Value
	0x71: X Position
	0x72: Y Position
	0x73: Font Address
## Video
Display settings:
    + 000 Standard: Full color low res       128x128, 16 bit rgb565
    + 001 Mixed: Better res, drgb color      256x256,  4 bit drgb
    + 010 Pallet: Better res, pallet color   256x256,  4 bit pallet
    + 011 Sharp: Best res, no color          512x512,  1 bit pallet
    + 100
## Stack
0x000 is the stack pointer that points to the end of the stack. A value of 0 means empty, a value of 1 points to:
0x001, the first element that grows to a maximum of 0xfff
Stack values can be address from a call or values from a push instruction