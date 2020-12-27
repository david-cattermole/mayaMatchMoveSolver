# Configuration

The JSON files in this directory are installed with mmSolver,
and are loaded with the Python `mmSolver.utils.config` module.

# Maya Shelves and Menus

For mmSolver, shelves and menus in Maya are generated automatically each time
Maya starts using the following files:

```
functions.json
menu.json
shelf.json
shelf_minimal.json
 ```

## functions.json

The `functions.json` file defines the individual user-accessible "functions"
that can be run by a user.

These functions are available to all users, even when
[customising][https://david-cattermole.github.io/mayaMatchMoveSolver/configuration.html#overriding-the-mmsolver-shelf-and-menus] to
create their own custom shelves and menus.

Here is an example of a single "function" definition:
```json
"name_of_function": {
    "name": "Name shown to the user",
    "name_shelf": "Name shown to the user in shelves only",
    "name_menu": "Name shown to the user in menus only",
    "tooltip": "A brief description of the function.",
    "icon_shelf": "theIconNameForAShelf_32x32.png",
    "command": [
        "import mmSolver.tools.tool_name_here.tool as tool;",
        "tool.open_window();"
    ]
}
```

Have a look at the `functions.json` file to see all the functions already
available. Copy and paste to make a new one - just make sure it's formatted
as valid JSON.

## How to add a new function

To add a shelf button or menu we need need to know two things:
1) What a button or menu does?
2) Where is the button or menu located?

The `functions.json` file answers number 1.
The `menu.json`, `shelf.json` and `shelf_minimal.json` files (known as
the "layout" files) answer number 2.

The layout files define how to lay out the functions into a shelf or menu.
A list of items (file-path-like strings) are used to define the order of
when to add a "function". The list of items is added from the top of the
file to the bottom. Parent items are assumed to have been created before
children.

Here is a short example of the items:
```json
"name_of_function",
"name_of_parent/---My Popup Menu Separator",
"name_of_parent/child_function",
"name_of_parent/child_function/another_child_function",
```

In a shelf, this would create two buttons, `name_of_function`, and
`name_of_parent`. The button `name_of_parent` will contain a pop-up menu
named `child_function` and will have a menu item `another_child_function`.

Any item entry starting with `---` is used to create a separator.
If there is text after `---`, then the text is turned into a label.

The layout files also have the ability to add custom "functions" for their
own shelf or menu. If there is a conflicting name for a function, the function
is overridden.  This allows us to add special pop-menus and tools, specific
to a shelf or menu. For example, users could customise their `shelf.json` file
and to run non-mmSolver functions and place the file in their home directory, see this
[page][https://david-cattermole.github.io/mayaMatchMoveSolver/configuration.html#overriding-the-mmsolver-shelf-and-menus]
for more details.

[https://david-cattermole.github.io/mayaMatchMoveSolver/configuration.html#overriding-the-mmsolver-shelf-and-menus]: customising
[https://david-cattermole.github.io/mayaMatchMoveSolver/configuration.html#overriding-the-mmsolver-shelf-and-menus]: page
