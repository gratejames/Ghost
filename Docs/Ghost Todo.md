# Simulator
+ [ ] Text modes?
+ [ ] Want a BRKC instruction pls
+ [ ] Add interrupt for stack overflow
## Debugger
+ [x] Highlight
	+ [x] the current PC
	+ [x] the current SP
+ [x] Decode the current PC?
	+ [x] Are the assembly instruction names available?
+ [x] Show the stack
	+ [ ] ~~Just the SP maybe?~~
	+ [x] Peek one of the stack?
	+ [ ] ~~Or maybe a fixed number?~~
+ [x] shortcuts
	+ [x] pg up/down: +/- 0x2000?
	+ [x] Jump to stack page
	+ [x] Jump to PC
		+ [x] Follow the PC?
+ [ ] ~~Debugger encounters condition where PC is mid-instruction~~
	+ [ ] ~~Is this even a problem?~~
	+ [ ] ~~!Performance cost on debugger for fixing?~~
+ [ ] Instructions per second
+ [ ] Frames per second
+ [ ] Hardware breakpoints on read/write
+ [ ] Manipulation of registers

# Assembler
+ [ ] Fix assembler string handler with comments
+ [ ] Make assembler smarter about single quotes
+ [ ] Make assembler handle empty lines in ramdisk.txt
# Shell/OS
+ [ ] Handle whitespace better in commands
	+ [x] string trim routine - increment pointer and write zeroes over whitespace
	+ [ ] Do similar in flags command
+ [ ] Malloc/free links
+ [ ] make stdout a file pointer
	+ [ ] Oooooh maybe both for the debug output and the on-screen output
+ [ ] The keyboard interrupt cobbles DD
+ [ ] Seems there might be a bug in malloc when OOM, where control flow escapes instead of returning a nullptr
+ [ ] '..' virtual directories in fs or in shell? If no symlinks, what are the effective differences?
+ [ ] path variable
	+ [ ] changable/extensible command table
	+ [ ] loading into the command table from a given folder
	+ [ ] Maybe, instead of having a list of 0 separated string/ptr pairs, we instead have a list of alternating string and function pointers.
		+ [ ] How to have function pointer to executable file? It would have to point to a small function that loads the filename and calls the execute routine?
		+ [ ] This still is inherently limited - how many functions should be allowed?
+ [x] Executables
	+ [ ] How to pass arguments? Lists of strings + number of args, like c? String of args and and length of arguments like other cmds?
	+ [x] Virtual Addressing
		+ [x] Oh gosh interrupts are broken now aren't they...
			+ [x] Set AO to zero on interrupts calls? Perhaps push it to the stack?
				+ [x] Is there even a way to read the AO?
		+ [x] Does this make a case for allowing user-settable interrups?
			+ [x] With register args?
			+ [ ] Ideas
				+ [ ] Screen clear
				+ [ ] File ops
				+ [ ] Malloc/free
				+ [x] Fetch CWD
				+ [x] Set Keyboard Interrupt
	+ [x] Neither arguments nor interrupts can work unless I can read from the AO
	+ [ ] Have the shell store the amount of used memory before and after, alert the user if it doesn't match the amount of used memory *after*
# Lang
+ [ ] Syntax highlighting for ghasm in g?
+ [x] types - get ChatGPT to generate a bunch of test cases?
	+ [x] lists
		+ [x] Heap? No, stack
+ [ ] Syntax
	+ [x] &
	+ [x] \*
	+ [x] \[\]
		+ [x] array type should nest
			+ [x] so should pointers actually
		+ [x] array should extend pointer
		+ [ ] Should array subscript extend identifier? Should identifiers be pointers???
+ [x] Rename stuff in constructor to dunders
+ [ ] backslash escaping
+ [ ] Function prototypes don't need variable names
+ [ ] Block-quotes
+ [ ] Flaws revealed by testing:
	+ [ ] Scoping for for-loops is incorrect. See chapter 8/valid/for_shadow . The inner scope should include the loopiness.
		+ [ ] Create intermediate scope
	+ [x] Allow empty segments in for loop: `for (int i = 0; i < 10;) {}`
	+ [ ] Switch/case
	+ [ ] goto/labels
	+ [ ] Constructor doesn't validate function arguments
		+ [x] Length
		+ [ ] Types
	+ [ ] Function parameters and body should be in the same scope
	+ [ ] Literal Integers are broken now. Add 'value' field
+ [x] Use exceptions in AST
	+ [x] Replace all return None's with exceptions
+ [x] Fix ASM capturing (Patched but still ad-hoc)
+ [ ] Add 'blame' method to all AST Nodes
+ [ ] semantic checking
# Programs
### Editor
+ [ ] Format path from inside executable
+ [ ] Exiting causes executable to be unrunable, but only from script (sh s)
+ [ ] handle no argument
	+ [ ] make interrupts for shell printing, so that the program can print it's own error messages
+ [ ] Maybe copy Blue's ED first?
### Program Ideas:
- [ ] Testing Framework
- [ ] Snake
# VFS
+ [ ] maybe unregister fileystem/disk number at some point?
+ [ ] change disk number command
+ [ ] current disk number command (Integrate into pwd?)
	+ [ ] should absolute paths be disknum:/path/... ? 0:/folders/file.ext ?
+ [ ] Actual file manipulation - file handlers
	+ [x] fopen
		+ [ ] Need better recovery
	+ [x] fclose
	+ [x] fwrite
	+ [x] fread (hesitantly)
	+ [x] fseek (0xffff is 'end')
	+ [ ] fstat. Same as stat, but takes a file pointer instead of a path
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
+ [x] stat (return a stat struct from vfs_stat)
+ [x] rewrite fs functions to use other subfunctions
+ [x] fix free page counter
+ [x] make fs bitmap work right
+ [x] cat

# Done
+ [x] AHH THE CAPITAL M IS TOO TALL
+ [x] Show registers on simulator's memory monitor
+ [x] cd'ing into a file causes corruption?
+ [x] echo without argument causes stack problems
+ [x] memory leak in ls
+ [x] Bug: 'cd bin;mkdir test;ls test;mkdir test;ls test'
+ [x] execute byte?
	+ [x] stat
	+ [x] execute
	+ [x] fsAssembler
	+ [x] commands to add or remove flags
+ [x] Clean code so that mallocs are never in functions and the functions are instead given function pointers from prior mallocs
+ [x] Maybe no spaces in paths? Just make shell parsing *that* much simpler?
+ [x] Memory access
	+ [x] peek
	+ [x] poke
+ [x] Combine path and directory functions
+ [x] Add project to git(hub)
+ [x] An actual debugger UI instead of just keyboard shortcuts? A menubar?
+ [x] Have .data prefixes make any sense please
+ [x] To and from R0 for better math
+ [x] FIX ASSEMBLER SO YOU CAN HAVE A ':' CHAR
+ [x] ~~Simulate external video card?~~
	+ [x] ~~Immitate N64 - interrupt on each scanline? Nah, would have to sync the render and logic threads~~
+ [x] Interrupts should probably queue...
	+ [x] Nope! Also, get rid of Interupt data - read it in from IO bit of memory!