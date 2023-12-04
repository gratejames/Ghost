# TODO
 + Add project to git(hub)
# Glossary
Register:           R0,R1,R2,R3                             , store into
\$Register:          The value that the register points to   , store at
Address:            Information at an address
Value:              A value given immediately
\$Address register:  The value pointed at by the address register
Address register:   The value in the address register

# Memory Map
Free:  0x0000 - 0xaeff ( 44799 Bytes )
I/O:   0xaf00 - 0xafff (   256 Bytes )
Video: 0xb000 - 0xefff ( 16384 Bytes )
Stack: 0xf000 - 0xffff (  4096 Bytes )

## I/O
0x00-0x5f: Interrupt Table
0x60-0x6f: Possible eventual interrupt queue
0x70-0x7f: Interrupt data
0x80-0x8f: Display Pallet
0x90-0xfd: Reserved for future use
0xfe: Display settings
0xff: Random Number

### Interrupt Table
#### 0x00: Key Status Change
	0x70: Key code. Refer [[Ghost Keycodes]]
	0x71: Event (0: up, 1: down)
#### 0x01: Mouse Position Change
	0x70: MouseX Position Absolute
	0x71: MouseY Position Absolute
#### 0x02: Mouse Button Change
	0x70: Button Number
	0x71: Event (0: up, 1: down)
#### 0x4f-5f: User defined, not called by hardware. Convention below.
#### 0x5f: High Res. String Print
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
    + 00 Standard: Full color low res       128x128, 16 bit rgb565
    + 01 Mixed: Better res, drgb color      256x256,  4 bit drgb
    + 10 Pallet: Better res, pallet color   256x256,  4 bit pallet
    + 11 Sharp: Best res, no color          512x512,  1 bit pallet
## Stack
0x000 is the stack pointer that points to the end of the stack. A value of 0 means empty, a value of 1 points to:
0x001, the first element that grows to a maximum of 0xfff
Stack values can be address from a call or values from a push instruction