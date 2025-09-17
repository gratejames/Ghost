# GHOST
What is it?
GHOST is a 'fantasy CPU'. Think a 'fantasy console' except it's just a CPU architecture.

This project has many components, each in their own folder.

# Simulator
This is the heart of the projects. It steps through given programs and executes them, drawing on the screen, and handling other IO. It also includes a debugger, with breakpoints, and a full memory and register inspector that also helps parse the hardware stack pointers. Features such as: break on access of a certain memory location, manually editing registers, and arbitrary jumps are planned, but not yet implemented.

# Assembler
This is the go-to home for development for GHOST. It takes the custom assembly language, and converts it to bytes for the simulator to execute. See the docs for the instruction set, and other notes on the architecture such as memory layout.

# Programs
Various assembly programs, including:
+ Memory management
+ A full ram-based filesystem
+ A WIP shell
+ Text graphics routines

# Lang
The beginnnings of a C compiler, built in python, targeting GHOST

# Hmm
This is a WIP circuit-level logisim model of the GHOST computer. As of the most recent change, I believe many core instructions are implemented. However I haven't added interrupts yet, and graphics might be impractical, given the speed of the simulation.

# Docs
Documentation, including to-do lists, system architecture notes, IO notes, memory layout notes, instruction set notes, program notes, and more scattered notes. Also contains various helper files: sublime syntax highlighting for the assembly, sublime build system for assembly, a script to read the instruction set from the docs and parse it into cpp code, then inject it into the simulator source code.