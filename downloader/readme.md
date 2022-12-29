# GHOST Downloader
This script fetches the current documentation from Notion.so and creates `./instructionSet.py`, `../assembler/assemblerDefs.py`, and `./GHASM.sublime-syntax`
I have included a read-only key to the original document at https://www.notion.so/jimmytech/Ghost-de748728e51a453288c075e56b2c64e3

## Operation
**Requires `Notional` through pip**

**Requires a Notion authentification token in `./NotionAuthKey`**

Runs through the columns of the table given, and collects information to generate the specs fed into the simulator and assembler.
Invalid binary instructions in the first column (ie. with an X on the end) are skipped
Rows that have a valid binary instruction but are missing essential errors throw `IndexError` (TODO)


## Sublime syntax highlighting
Sublime syntax highlighting is accomplished by moving `./GHASM.sublime-syntax` to `C:\Users\...\AppData\Roaming\Sublime Text 3\Packages\User\GHASM`

The GHASM folder can optionally include the file GHASM.sublime-build with the contents
```
{
	"shell_cmd": "python \"C:\\...\\Ghost\\assembler\\main.py\" \"$file\"",
    "selector": "source.ghasm",
}
```
