"""
GUI tools for the arm simulation demo

(C)2008 by Mark Tomczak (fixermark@gmail.com)

Free for educational and demonstration purposes, and for all uses regarding the
FIRST Robotics competition.

This program was built with Panda3D 1.4.2 (http://www.panda3d.org)
"""

# Graphical User Interface utilities make it easier to create text boxes
# that change the behavior of the simulation when you press return. Most
# of the details in here aren't important to the simulation; you can
# e-mail me at fixermark@gmail.com for more information

from pandac.PandaModules import *
from direct.gui.DirectGui import *

def _numericTransform(numberString,functionToRun):
    functionToRun(float(numberString))

def makeNumericalUpdater(labelText,updateFunc,initialValue=0):
    label=DirectLabel(
        text=labelText,
        text_bg=(0,0,0,0),
        text_fg=(0,0,0,1),
        text_align=TextNode.ARight,
        frameColor=(0,0,0,0)
    )
        
    newUpdater=DirectEntry(
        initialText=str(initialValue),
        width=4,
        cursorKeys=1,
        command=lambda x:_numericTransform(x,updateFunc)
    )

    output=NodePath("Numerical Updater: "+labelText)
    label.reparentTo(output)
    label.setX(-.2)
    newUpdater.reparentTo(output)

    return output
        
                           
