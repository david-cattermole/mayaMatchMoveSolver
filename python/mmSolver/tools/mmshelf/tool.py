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
    icon = 'menuIconWindow.png'
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
    name = 'Create'
    tooltip = 'Create Marker.'
    icon = 'createMarker_32x32.png'
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
    icon = 'menuIconFile.png'
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

    # Create Bundle
    name = 'Create'
    tooltip = 'Create Bundle.'
    icon = 'createBundle_32x32.png'
    cmd = (
        'import mmSolver.tools.createbundle.tool;'
        'mmSolver.tools.createbundle.tool.create_bundle();'
    )
    shelfutils.create_shelf_button(
        parent=shelf,
        name=name,
        tooltip=tooltip,
        icon=icon,
        cmd=cmd,
    )

    shelfutils.create_shelf_separator(parent=shelf)

    # Link Marker + Bundle
    name = 'Link'
    tooltip = 'Link the selected Marker and Bundle together.'
    icon = None
    cmd = (
        'import mmSolver.tools.linkmarkerbundle.tool as link_mb_tool;'
        'link_mb_tool.link_marker_bundle();'
    )
    shelfutils.create_shelf_button(
        parent=shelf,
        name=name,
        tooltip=tooltip,
        icon=icon,
        cmd=cmd,
    )

    # Unlink Marker from Bundle
    name = 'Unlink'
    tooltip = 'Unlink all selected Markers from their Bundle.'
    icon = None
    cmd = (
        'import mmSolver.tools.linkmarkerbundle.tool as link_mb_tool;'
        'link_mb_tool.unlink_marker_bundle();'
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

    shelfutils.create_shelf_separator(parent=shelf)

    # Triangulate Bundle (current frame)
    name = 'Frnt'
    tooltip = 'Push in Front.'
    icon = None
    cmd = (
        'import mmSolver.tools.triangulate.tool;'
        'mmSolver.tools.triangulate.tool.main();'
    )
    shelfutils.create_shelf_button(
        parent=shelf,
        name=name,
        tooltip=tooltip,
        icon=icon,
        cmd=cmd,
    )

    # # Triangulate Bundle (multiple frames)
    # name = 'Frnt'
    # tooltip = 'Push in Front.'
    # icon = None
    # cmd = (
    #     'import mmSolver.tools.triangulate.tool;'
    #     'mmSolver.tools.triangulate.tool.main();'
    # )
    # shelfutils.create_shelf_button(
    #     parent=shelf,
    #     name=name,
    #     tooltip=tooltip,
    #     icon=icon,
    #     cmd=cmd,
    # )

    # Ray Cast Marker
    name = 'RCM'
    tooltip = 'Ray Cast Marker.'
    icon = None
    cmd = (
        'import mmSolver.tools.raycastmarker.tool;'
        'mmSolver.tools.raycastmarker.tool.main();'
    )
    shelfutils.create_shelf_button(
        parent=shelf,
        name=name,
        tooltip=tooltip,
        icon=icon,
        cmd=cmd,
    )

    shelfutils.create_shelf_separator(parent=shelf)

    # Triangulate Bundle (current frame)
    name = 'ChSen'
    tooltip = 'Channel sensitivity UI.'
    icon = None
    cmd = (
        'import mmSolver.tools.channelsen.tool;'
        'mmSolver.tools.channelsen.tool.main();'
    )
    shelfutils.create_shelf_button(
        parent=shelf,
        name=name,
        tooltip=tooltip,
        icon=icon,
        cmd=cmd,
    )

    name = 'TglBnd'
    tooltip = 'Toggles bundle lock .'
    icon = None
    cmd = (
        'import mmSolver.tools.togglebundlelock.tool as tglbndlock;'
        'tglbndlock.toggle_bundle_lock();'
    )
    shelfutils.create_shelf_button(
        parent=shelf,
        name=name,
        tooltip=tooltip,
        icon=icon,
        cmd=cmd,
    )

    return
