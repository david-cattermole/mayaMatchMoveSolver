# 3DEqualizer Python Scripts

The files in this directory reduce as much code duplication as
possible by splitting code into individual re-usable Python modules,
that can be used by multiple 3DEqualizer scripts.

The issue with using multiple Python modules is that 3DEqualizer's
ScriptDB does not support installing multiple Python modules for each
tool.

As a result, the files in this directory need to be packaged into
singular files so they can be distributed via 3DEqualizer's ScriptDB.

## Updating Files

Some of the files in this directory are not specific to 3DEqualizer,
but are reused in the Maya python directory as `<project
root>/python/`.

Therefore to simplify the update of the files in this directory (and
to avoid using Symbolic-Links - because they may not be OS-portable) a
script has been provided `update_files.bash`.

Run the file like this:
```
$ cd <project root>
$ bash ./share/3dequalizer/python/update_files.bash
```
