# TODO
+ [x] Add project to git(hub)
+ [x] Have .data prefixes make any sense please
+ [x] To and from R0 for better math
+ [ ] Text modes?
+ [ ] Simulate external video card?
+ [x] Interrupts should probably queue...
	+ [x] Nope! Also, get rid of Interupt data - read it in from IO bit of memory!
+ [ ] vfs
	+ [x] ramdisk
	+ [x] mkdir
		+ [x] Clearing child directory flags
		+ [x] Clearing parent directory size
	+ [x] rmdir
	+ [x] touch
	+ [x] rm
		+ [x] Fix recursion bug
	+ [x] ls
	+ [x] subfolder/path handling
	+ [ ] '..'
	+ [ ] Actual file manipulation - file handlers
		+ [x] fopen
			+ [ ] Need more recoverability
		+ [x] fclose
		+ [x] fwrite
		+ [x] fread (hesitantly)
		+ [x] fseek (0xffff is 'end')
		+ [ ] fstat. Same as stat, but takes a file pointer instead of a path
	+ [x] stat (return a stat struct from vfs_stat)
	+ [x] rewrite fs functions to use other subfunctions
	+ [x] fix free page counter
	+ [x] make fs bitmap work right
	+ [x] cat
	+ [ ] maybe unregister fileystem/disk number at some point?
	+ [ ] change disk number command
		+ [ ] Why? I can't remember why this would be needed?
	+ [ ] current disk number command (Integrate into pwd?)
		+ [ ] should absolute paths be disknum:/path/... ? 0:/folders/file.ext ?
+ [x] AHH THE CAPITAL M IS TOO TALL
+ [x] Show registers on simulator's memory monitor
+ [ ] AN EDITOR
+ [ ] path variable
	+ [ ] changable/extensible command table
	+ [ ] loading into the command table from a given folder
	+ [ ] Maybe, instead of having a list of 0 separated string/ptr pairs, we instead have a list of alternating string and function pointers.
		+ [ ] How to have function pointer to executable file? It would have to point to a small function that loads the filename and calls the execute routine?
		+ [ ] This still is inherently limited - how many functions should be allowed?
+ [ ] make stdout a file pointer
+ [x] Memory access
	+ [x] peek
	+ [x] poke
+ [ ] Combine path and directory functions
+ [ ] Handle whitespace better in commands
	+ [x] string trim routine - incrememnt pointer and write zeroes over whitespace
	+ [ ] Do similar in flags command
+ [x] Executables
	+ [ ] How to pass arguments? Lists of strings + number of args, like c? String of args and and length of arguments like other cmds?
	+ [x] Virtual Addressing
		+ [ ] Oh gosh interrupts are broken now aren't they...
			+ [ ] Set AO to zero on interrupts calls? Perhaps push it to the stack? Does this make a case for allowing user-settable interrups?
				+ [ ] Is there even a way to read the AO?
	+ [x] Neither arguments nor interrupts can work unless I can read from the AO
+ [x] cd'ing into a file causes corruption?
+ [x] echo without argument causes stack problems
+ [x] memory leak in ls
+ [x] 'cd bin;mkdir test;ls test;mkdir test;ls test'
+ [x] execute byte?
	+ [x] stat
	+ [x] execute
	+ [x] fsAssembler
	+ [x] commands to add or remove flags
+ [x] Clean code so that mallocs are never in functions and the functions are instead given function pointers from prior mallocs
+ [x] Maybe no spaces in paths? Just make shell parsing *that* much simpler?

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

## I/O / Misc
0x00-0x5f: Interrupt Table
0x60-0xcf: Unused
0xd0-0xdf: IO Data Buffer
0xe0-0xee: Unused
0xef: Display settings
0xf0-0xff: Display Pallet

### Interrupt Table
#### 0x00: Key Status Change
	IO 0: Key Event: (0: up, 1: down)
	IO 1: Key Code: [https://www.libsdl.org/release/SDL-1.2.15/docs/html/sdlkey.html](SDLKEY)
#### 0x01: Mouse Position Change                 NYI
	IO 0: MouseX position in px, absolute to window
	IO 1: MouseY position in px, absolute to window
#### 0x02: Mouse Button Change                   NYI
	IO 0: Button Event (0: up, 1: down)
	IO 1: Button Number
#### 0x4f-5f: User defined, not called by hardware. Convention below.
#### 0x5e: High Res. String Print
	IO 0: String Address
	IO 1: X Start Position
	IO 2: Y Position
	IO 3: Font Address
#### 0x5f: High Res. Character Print
	IO 0: Char Value
	IO 1: X Position
	IO 2: Y Position
	IO 3: Font Address
## Video
Display settings (only lower 2 bits used):
    + 00 Standard: Full color low res       128x128, 16 bit rgb565
    + 01 Mixed: Better res, drgb color      256x256,  4 bit drgb
    + 10 Pallet: Better res, pallet color   256x256,  4 bit pallet
    + 11 Sharp: Best res, no color          512x512,  1 bit pallet
## Stack
0x000 is the stack pointer that points to the end of the stack. A value of 0 means empty, a value of 1 points to
0x001, the first element that grows to a maximum of 0xfff
Stack values can be addresses from a `CALL` or values from a `PSH` instruction