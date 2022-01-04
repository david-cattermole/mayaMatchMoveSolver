# Copyright (C) 2022 Kazuma Tonegawa.
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
"""
This file contains functions to further extend the features of 
Morgan Loomis' tools.
"""

import maya.cmds as mc
from maya import OpenMaya

import ml_convertRotationOrder
from constant import ROTATE_ORDERS

def loadTipsForAll():
    '''
    This is a modified version of the loadTips() method from 
    ml_convertRotationOrder.py file, but this is supposed to 
    print the rotate order status for all selected objects 
    and print them in the Script Editor.
    '''

    selList = mc.ls(sl=True)

    if not selList:
        OpenMaya.MGlobal.displayWarning('Please select at least one object.')
        return
    
    for sel in selList:
        ro = ROTATE_ORDERS[mc.getAttr(sel+'.rotateOrder')]
        
        nodeName = mc.ls(sel, shortNames=True)[0]

        infoText = 'This object is '
        tol = ml_convertRotationOrder.gimbalTolerence(sel)
        if tol < 0.1:
            infoText += 'not currently gimballing'
        else:
            if tol < 0.5:
                infoText += 'only '
            infoText += str(int(tol*100))
            infoText+='% gimballed'


        #test all rotation orders and find the lowest value
        rotOrderTests = ml_convertRotationOrder.testAllRotateOrdersForGimbal(sel)
        lowest = sorted(rotOrderTests)[0]
        #find the lower of the two worldspace options
        lowestWS = 1
        for each in rotOrderTests[2:4]:
            if each < lowestWS:
                lowestWS = each

        #determine if it's a worldspace control
        ws = ml_convertRotationOrder.isWorldSpaceControl(sel)
        if ws:
            infoText += ", and it looks like it's a worldspace control."
        else:
            infoText+='.'
        
        resultingText = '{nodeName} | {ro} -- Current rotate order --'.format(
                                                                nodeName=nodeName,
                                                                ro=ro
                                                                )
        for t, r in zip(rotOrderTests, ROTATE_ORDERS):
            if r == ro:
                continue

            text = '(' + str(int(t*100)) + '%) Gimballed.'

            if ws:
                if r.endswith('y') and t == lowestWS: #lowest worldspace option is reccomended
                    text += '<-- [RECOMMENDED]'
                elif lowest<lowestWS and t==lowest: #if there's a lower non-worldspace option, reccomend that also
                    text += '<-- [NON-WORLDSPACE RECOMMENDATION]'
            else:
                if t == lowest: #lowest test value is reccomended.
                    text += '<-- [RECOMMENDED]'
                elif lowest<lowestWS and t==lowestWS and t < 0.3: #if there's a
                    text += '<-- [RECOMMENDED FOR WORLDSPACE CONTROLS]'

            resultingText += ' | {r} {text}'.format(r=r, text=text)
        
        resultingText += '\n'
        resultingText += '^^ ' + infoText + '\n'
        print(resultingText)
    
    mc.select(selList)
