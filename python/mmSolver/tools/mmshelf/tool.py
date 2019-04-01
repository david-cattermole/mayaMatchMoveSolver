"""
Build the mmSolver Maya shelf.
"""

import mmSolver.logger
import mmSolver.ui.shelfutils as shelfutils
import mmSolver.tools.mmshelf.constant as const


LOG = mmSolver.logger.get_logger()


def _create_solver_menu(menu):
    # Open Solver...
    name = 'Open Solver...'
    tooltip = 'Open the MM Solver window.'
    cmd = (
        'import mmSolver.tools.solver.tool;'
        'mmSolver.tools.solver.tool.open_window();'
    )
    shelfutils.create_menu_item(
        parent=menu,
        name=name,
        tooltip=tooltip,
        cmd=cmd,
    )

    # Run Solver
    name = 'Run Solver'
    tooltip = 'Run solver on currently active Collection.'
    cmd = (
        'import mmSolver.tools.solver.tool as tool;'
        'tool.run_solve();'
    )
    shelfutils.create_menu_item(
        parent=menu,
        name=name,
        tooltip=tooltip,
        cmd=cmd,
    )

    # Run Solver on the current frame
    name = 'Run Solver (Current Frame)'
    tooltip = 'Run solver on currently active Collection on the current frame.'
    cmd = (
        'import mmSolver.tools.solver.tool as tool;'
        'tool.run_solve_on_current_frame();'
    )
    shelfutils.create_menu_item(
        parent=menu,
        name=name,
        tooltip=tooltip,
        cmd=cmd,
    )
    return


def _create_bundle_tools_menu(menu):
    # Toggle bundle lock
    name = 'Toggle Bundle Lock-State'
    tooltip = 'Toggle the Bundle node attribute Lock State.'
    cmd = (
        'import mmSolver.tools.togglebundlelock.tool as tglbndlock;'
        'tglbndlock.toggle_bundle_lock();'
    )
    shelfutils.create_menu_item(
        parent=menu,
        name=name,
        tooltip=tooltip,
        cmd=cmd,
    )

    # Re-Project a Bundle
    name = 'Re-Project Bundle'
    tooltip = 'Re-Project Bundle on top of Marker.'
    cmd = (
        'import mmSolver.tools.reprojectbundle.tool;'
        'mmSolver.tools.reprojectbundle.tool.main();'
    )
    shelfutils.create_menu_item(
        parent=menu,
        name=name,
        tooltip=tooltip,
        cmd=cmd,
    )

    # # Triangulate Bundle (multiple frames)
    # name = 'Triangulate Bundle'
    # tooltip = 'Use Marker to triangulate a 3D position for Bundle.'
    # cmd = (
    #     'import mmSolver.tools.triangulate.tool;'
    #     'mmSolver.tools.triangulate.tool.main();'
    # )
    # shelfutils.create_menu_item(
    #     parent=menu,
    #     name=name,
    #     tooltip=tooltip,
    #     cmd=cmd,
    # )

    # Ray Cast Marker
    name = 'Ray-Cast Marker'
    tooltip = 'Ray Cast Marker onto geometry.'
    cmd = (
        'import mmSolver.tools.raycastmarker.tool;'
        'mmSolver.tools.raycastmarker.tool.main();'
    )
    shelfutils.create_menu_item(
        parent=menu,
        name=name,
        tooltip=tooltip,
        cmd=cmd,
    )

    # Aim At Camera Screen-Space Z
    name = 'Aim At Camera (Screen Z)'
    tooltip = 'Screen-space Z.'
    cmd = (
        'import mmSolver.tools.screenzmanipulator.tool;'
        'mmSolver.tools.screenzmanipulator.tool.main();'
    )
    shelfutils.create_menu_item(
        parent=menu,
        name=name,
        tooltip=tooltip,
        cmd=cmd,
    )

    return


def _create_marker_tools_menu(menu):
    # Duplicate Marker
    name = 'Duplicate Marker'
    tooltip = 'Duplicate marker from selection.'
    cmd = (
        'import mmSolver.tools.duplicatemarker.tool;'
        'mmSolver.tools.duplicatemarker.tool.main();'
    )
    shelfutils.create_menu_item(
        parent=menu,
        name=name,
        tooltip=tooltip,
        cmd=cmd,
    )

    # Average Marker
    name = 'Average Markers'
    tooltip = 'Average marker from selection.'
    cmd = (
        'import mmSolver.tools.averagemarker.tool;'
        'mmSolver.tools.averagemarker.tool.main();'
    )
    shelfutils.create_menu_item(
        parent=menu,
        name=name,
        tooltip=tooltip,
        cmd=cmd,
    )
    return


def _create_link_tools_menu(menu):
    # Link Marker + Bundle
    name = 'Link'
    tooltip = 'Link the selected Marker and Bundle together.'
    cmd = (
        'import mmSolver.tools.linkmarkerbundle.tool as link_mb_tool;'
        'link_mb_tool.link_marker_bundle();'
    )
    shelfutils.create_menu_item(
        parent=menu,
        name=name,
        tooltip=tooltip,
        cmd=cmd,
    )

    # Unlink Marker from Bundle
    name = 'Unlink'
    tooltip = 'Unlink all selected Markers from their Bundle.'
    cmd = (
        'import mmSolver.tools.linkmarkerbundle.tool as link_mb_tool;'
        'link_mb_tool.unlink_marker_bundle();'
    )
    shelfutils.create_menu_item(
        parent=menu,
        name=name,
        tooltip=tooltip,
        cmd=cmd,
    )
    return


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
    btn = shelfutils.create_shelf_button(
        parent=shelf,
        name=name,
        tooltip=tooltip,
        icon=icon,
        cmd=cmd,
    )

    # Create Menu Pop-Up (for both left mouse button)
    menu_rmb = shelfutils.create_popup_menu(parent=btn, button=3)
    _create_solver_menu(menu_rmb)

    shelfutils.create_shelf_separator(parent=shelf)

    # Create Marker
    name = 'Create'
    tooltip = 'Create Marker.'
    icon = 'createMarker_32x32.png'
    cmd = (
        'import mmSolver.tools.createmarker.tool;'
        'mmSolver.tools.createmarker.tool.main();'
    )
    shelfutils.create_shelf_button(
        parent=shelf,
        name=name,
        tooltip=tooltip,
        icon=icon,
        cmd=cmd,
    )

    # Convert to Marker
    name = 'Convrt'
    tooltip = 'Convert 3D Transform to Marker.'
    icon = 'createMarker_32x32.png'
    cmd = (
        'import mmSolver.tools.convertmarker.tool;'
        'mmSolver.tools.convertmarker.tool.main();'
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
        'mmSolver.tools.createbundle.tool.main();'
    )
    shelfutils.create_shelf_button(
        parent=shelf,
        name=name,
        tooltip=tooltip,
        icon=icon,
        cmd=cmd,
    )

    shelfutils.create_shelf_separator(parent=shelf)

    # Marker Tools
    name = 'MTools'
    tooltip = 'Marker Tools.'
    icon = 'createMarker_32x32.png'
    cmd = 'pass'
    btn = shelfutils.create_shelf_button(
        parent=shelf,
        name=name,
        tooltip=tooltip,
        icon=icon,
        cmd=cmd,
    )

    # Create Menu Pop-Up (for both left and right mouse buttons)
    menu_lmb = shelfutils.create_popup_menu(parent=btn, button=1)
    menu_rmb = shelfutils.create_popup_menu(parent=btn, button=3)
    _create_marker_tools_menu(menu_lmb)
    _create_marker_tools_menu(menu_rmb)

    # Bundle Tools
    name = 'BTools'
    tooltip = 'Bundle Tools.'
    icon = 'createBundle_32x32.png'
    cmd = 'pass'
    btn = shelfutils.create_shelf_button(
        parent=shelf,
        name=name,
        tooltip=tooltip,
        icon=icon,
        cmd=cmd,
    )

    # Create Menu Pop-Up (for both left and right mouse buttons)
    menu_lmb = shelfutils.create_popup_menu(parent=btn, button=1)
    menu_rmb = shelfutils.create_popup_menu(parent=btn, button=3)
    _create_bundle_tools_menu(menu_lmb)
    _create_bundle_tools_menu(menu_rmb)

    shelfutils.create_shelf_separator(parent=shelf)

    # Swap Markers / Bundles
    name = 'M / B'
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
    name = 'M + B'
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

    # Marker Bundle Rename
    name = 'MBRena'
    tooltip = 'Rename Selected Marker And Connected Bundles.'
    icon = None
    cmd = (
        'import mmSolver.tools.markerbundlerename.tool;'
        'mmSolver.tools.markerbundlerename.tool.main();'
    )
    shelfutils.create_shelf_button(
        parent=shelf,
        name=name,
        tooltip=tooltip,
        icon=icon,
        cmd=cmd,
    )

    # Marker bundle link and unlink Tools
    name = 'MBLnk'
    tooltip = 'Marker bundle link and unlink Tools.'
    icon = None
    cmd = 'pass'
    btn = shelfutils.create_shelf_button(
        parent=shelf,
        name=name,
        tooltip=tooltip,
        icon=icon,
        cmd=cmd,
    )

    # Create Menu Pop-Up (for both left and right mouse buttons)
    menu_lmb = shelfutils.create_popup_menu(parent=btn, button=1)
    menu_rmb = shelfutils.create_popup_menu(parent=btn, button=3)
    _create_link_tools_menu(menu_lmb)
    _create_link_tools_menu(menu_rmb)

    shelfutils.create_shelf_separator(parent=shelf)

    # Center 2D on Selected
    name = 'Center'
    tooltip = 'Center 2D on Selected.'
    icon = None
    cmd = (
        'import mmSolver.tools.centertwodee.tool;'
        'mmSolver.tools.centertwodee.tool.main();'
    )
    shelfutils.create_shelf_button(
        parent=shelf,
        name=name,
        tooltip=tooltip,
        icon=icon,
        cmd=cmd,
    )

    # Channel sensitivity UI
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

    # Smooth Selected Keyframes
    name = 'Smooth'
    tooltip = 'Smooth Selected Keyframes.'
    icon = None
    cmd = (
        'import mmSolver.tools.smoothkeyframes.tool;'
        'mmSolver.tools.smoothkeyframes.tool.main();'
    )
    shelfutils.create_shelf_button(
        parent=shelf,
        name=name,
        tooltip=tooltip,
        icon=icon,
        cmd=cmd,
    )
    return
