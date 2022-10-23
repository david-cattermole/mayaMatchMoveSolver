# Copyright (C) 2022 David Cattermole.
#
# This file is part of mmSolver.
#
# mmSolver is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# mmSolver is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
#

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds
import maya.mel

import mmSolver.logger
import mmSolver.utils.python_compat as pycompat
import mmSolver.tools.cameracontextmenu.constant as const

LOG = mmSolver.logger.get_logger()


def open_node_in_attribute_editor(node):
    mel_cmd = (
        # 'AttributeEditor;'
        # 'updateAE "{node}";'
        'showEditorExact "{node}";'
    ).format(node=node)
    maya.mel.eval(mel_cmd)
    return


def open_node_in_node_editor(node):
    # TODO: This is not working correctly. The graph is not cleared
    #  when created the second time, the contents of the window are
    #  'remembered' and re-used.
    mel_cmd = '''
string $nodeName = "%s";
select -r $nodeName;

nodeEditorWindow(); // Open window.

// Set all nodes to be 'simple' looking.
string $ned = getCurrentNodeEditor();
select -clear;
nodeEditor -e
    -nodeViewMode "simple"
    $ned;

// Set only mmSolver nodes to be 'custom' displayed.
string $nodes[] = `listHistory -breadthFirst $nodeName`;
string $node;
for ($node in $nodes) {
    string $nodeType = `nodeType $node`;
    if (startsWith($nodeType, "mm") == 1) {
        select -add $node;
    }
}
nodeEditor -e
    -nodeViewMode "custom"
    $ned;

// Graph and frame the nodes.
select -r $nodeName;
nodeEditor -e
    -rootsFromSelection
    -upstream
    -frameAll
    $ned;
'''
    mel_cmd = mel_cmd % node
    maya.mel.eval(mel_cmd)
    return
