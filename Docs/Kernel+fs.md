Filesystem:
+ mkdir
+ make file
+ rmdir
+ rmfile

Device/Drive:
+ Read
+ Write



GhostFS (Extends ZealFS)

Each page is 128 bytes

Header page
  Magic 'G'
  Version number
  Bitmap size - unused
  Free pages count
  Allocated pages bitmap, 32 bytes (0 is free, 1 is allocated)
  12 bytes of empty
  5 root directory entries

Directory Entry: (16 bytes)
  Flags (Byte 0: Is allocated? Byte 1: Is dir? Byte 2: Is executable?) (Here, byte zero is least significant: 0b0000 0000 0000 0eda)
  Page of contents start
  12 char name padded with 0
  2 byte size of file (Only final byte is used)

File Page:
  Page number of remaining file data, or 0
  Date...
  