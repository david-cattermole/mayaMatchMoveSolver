"""
Build the mmSolver Maya shelf.
"""

import mmSolver.logger
import mmSolver.ui.shelfutils as shelfutils
import mmSolver.tools.mmshelf.constant as const


LOG = mmSolver.logger.get_logger()


def build_shelf():
    """
    Build the 'mmSolver' shelf.
    """
    LOG.info('Building mmSolver Shelf...')
    shelf_parent = shelfutils.get_shelves_parent()
    shelf_name = str(const.SHELF_NAME)
    shelf = shelfutils.create_shelf(
        parent=shelf_parent,
        name=shelf_name
    )
    if shelf is None:
        return

    # Solver UI
    name = 'Solver'
    tooltip = 'Open the MM Solver window.'
    icon = None
    cmd = (
        'import mmSolver.tools.solver.tool;'
        'mmSolver.tools.solver.tool.open_window();'
    )
    shelfutils.create_shelf_button(
        parent=shelf,
        name=name,
        tooltip=tooltip,
        icon=icon,
        cmd=cmd,
    )

    shelfutils.create_shelf_separator(parent=shelf)

    # Create Marker
    name = 'MKR +'
    tooltip = 'Create Marker.'
    icon = None
    cmd = (
        'import mmSolver.tools.createmarker.tool;'
        'mmSolver.tools.createmarker.tool.create_marker();'
    )
    shelfutils.create_shelf_button(
        parent=shelf,
        name=name,
        tooltip=tooltip,
        icon=icon,
        cmd=cmd,
    )

    # Load Marker
    name = 'Load...'
    tooltip = 'Load Marker.'
    icon = None
    cmd = (
        'import mmSolver.tools.loadmarker.tool;'
        'mmSolver.tools.loadmarker.tool.open_window();'
    )
    shelfutils.create_shelf_button(
        parent=shelf,
        name=name,
        tooltip=tooltip,
        icon=icon,
        cmd=cmd,
    )

    shelfutils.create_shelf_separator(parent=shelf)

    # Center 2D on Selected
    name = 'Center'
    tooltip = 'Center 2D on Selected.'
    icon = None
    cmd = (
        'import mmSolver.tools.centertwodee.tool;'
        'mmSolver.tools.centertwodee.tool.center_two_dee();'
    )
    shelfutils.create_shelf_button(
        parent=shelf,
        name=name,
        tooltip=tooltip,
        icon=icon,
        cmd=cmd,
    )

    # Swap Markers / Bundles
    name = 'M<>B'
    tooltip = 'Toggle Markers Bundles.'
    icon = None
    cmd = (
        'import mmSolver.tools.selection.tools as selection_tool;'
        'selection_tool.swap_between_selected_markers_and_bundles();'
    )
    shelfutils.create_shelf_button(
        parent=shelf,
        name=name,
        tooltip=tooltip,
        icon=icon,
        cmd=cmd,
    )

    # Select Markers and Bundles
    name = 'M+B'
    tooltip = 'Select Markers and Bundles.'
    icon = None
    cmd = (
        'import mmSolver.tools.selection.tools as selection_tool;'
        'selection_tool.select_both_markers_and_bundles();'
    )
    shelfutils.create_shelf_button(
        parent=shelf,
        name=name,
        tooltip=tooltip,
        icon=icon,
        cmd=cmd,
    )
    return
