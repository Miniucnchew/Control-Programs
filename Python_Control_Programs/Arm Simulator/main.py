"""
The main simulation loop for the arm simulation demo

(C)2008 by Mark Tomczak (fixermark@gmail.com)

Free for educational and demonstration purposes, and for all uses regarding the
FIRST Robotics competition.

This program was built with Panda3D 1.4.2 (http://www.panda3d.org)
"""


# IMPORTING LIBRARIES
# these imports are required by Panda3d and bring in the graphics and
# time engines.
import direct.directbase.DirectStart
from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *

# these imports are other code to support the program. Look in
# the corresponding .py files for more information
import geometry
from physicsArm import PhysicsArm
from armController import ArmController
import guiUtils

class World:
    def init(self):

        self.initLighting()

        # We'll start by creating a simple base, which means
        # we want a node to hold the model. This is for the programmer's
        # convenience; I'll attach everything to this base so I can move
        # the model without moving all its parts one-by-one.
        self.modelBase=render.attachNewNode('model base')
        self.modelBase.setPos(0,8,-2)

        # Create a visible grey base and attach it to our base node
        baseGeom=self.modelBase.attachNewNode(geometry.makeCube())
        baseGeom.setScale(4,2,.1)

        # Create the blue arm and attach it to our base node
        towerGeom=self.modelBase.attachNewNode(geometry.makeCube())
        towerGeom.setScale(.1,.1,4)
        towerGeom.setZ(2)
        towerGeom.setColor(0,0,1,1)

        # Create another node to serve as the arm joint
        self.armJoint=self.modelBase.attachNewNode("arm joint")
        self.armJoint.setZ(4)
        self.armJoint.setY(-.1)

        # Create the PhysicsArm, which knows how to apply physics to itself
        self.arm=PhysicsArm()
        self.arm.reparentTo(self.armJoint)

        # The visible model for the (red) physics arm
        armHolder=NodePath("arm")
        armGeom=armHolder.attachNewNode(geometry.makeCube())
        armGeom.setScale(1,.1,.1)
        armHolder.setColor(1,.5,.5,1)

        # give the arm model we created to the PhysicsArm to control
        self.arm.setModel(armHolder)

        # create the ArmController, which knows how to simulate a motor
        # attached to the arm
        self.controller=ArmController(self.arm)
        self.controller.reparentTo(self.armJoint)
        self.controller.setTarget(0)

        # create text fields
        self.initGui()

        # To make sure the scene changes every frame, we give these
        # control functions to Panda's animation engine. This is done
        # by creating a Sequence object, which will run each thing inside
        # it every frame
        self.simulationLoop=Sequence(
            Func(self.controller.step),
            Func(self.arm.stepPhysics)
        )
        # Tell the sequence to run over and over, forever
        self.simulationLoop.loop()

        # And we're done! Panda will now run our loop over and over,
        # so the work is done in the ArmController's step function and
        # the arm's stepPhysics function.

    def initLighting(self):
        """
        Make some simple light. This isn't important for understanding
        the physics; see the manual at
        http://panda3d.org/wiki/index.php/Fog_and_Lighting for more information
        on Panda's lights.
        """
        ambientLight=AmbientLight('ambient')
        ambientLight.setColor(Vec4(.3,.3,.3,1))
        ambientLightNP=render.attachNewNode(ambientLight)
        render.setLight(ambientLightNP)

        directionalLight=DirectionalLight("directional 1")
        directionalLight.setColor(Vec4(.3,.3,.3,1))
        directionalLightNP=render.attachNewNode(directionalLight)
        directionalLightNP.setHpr(75,-30,0)
        render.setLight(directionalLightNP)

        directionalLight=DirectionalLight("directional 2")
        directionalLight.setColor(Vec4(.3,.3,.3,1))
        directionalLightNP=render.attachNewNode(directionalLight)
        directionalLightNP.setHpr(-40,-30,0)
        render.setLight(directionalLightNP)

    def initGui(self):
        """
        Make the GUI text inputs and bind them to functions that use
        the text to change the simulation values. This is pretty
        tedious stuff that doesn't matter to the simulation; for more
        information see the Panda manual at
        http://panda3d.org/wiki/index.php/DirectGUI
        """
        horizontalAlignment=-1.0
        pUpdater=guiUtils.makeNumericalUpdater(
            "kP:",
            self.controller.setKP,
            self.controller.controller.kP
        )
        pUpdater.reparentTo(aspect2d)
        pUpdater.setScale(.07)
        pUpdater.setPos(horizontalAlignment,0,.8)

        iUpdater=guiUtils.makeNumericalUpdater(
            "kI:",
            self.controller.setKI,
            self.controller.controller.kI
        )
        iUpdater.reparentTo(aspect2d)
        iUpdater.setScale(.07)
        iUpdater.setPos(horizontalAlignment,0,.7)

        dUpdater=guiUtils.makeNumericalUpdater(
            "kD:",
            self.controller.setKD,
            self.controller.controller.kD)
        dUpdater.reparentTo(aspect2d)
        dUpdater.setScale(.07)
        dUpdater.setPos(horizontalAlignment,0,.6)

        targetUpdater=guiUtils.makeNumericalUpdater(
            "goal:",
            self.controller.setTarget,
            self.controller.controller.target
        )
        targetUpdater.reparentTo(aspect2d)
        targetUpdater.setScale(.07)
        targetUpdater.setPos(horizontalAlignment,0,.5)

        horizontalAlignment=1.0

        massUpdater=guiUtils.makeNumericalUpdater("mass:",self.arm.setMass,self.arm.mass)
        massUpdater.reparentTo(aspect2d)
        massUpdater.setScale(.07)
        massUpdater.setPos(horizontalAlignment,0,.8)

        inertialUpdater=guiUtils.makeNumericalUpdater(
            "moment of inertia:",
            self.arm.setMomentOfInertia,
            self.arm.momentOfInertia)
        inertialUpdater.reparentTo(aspect2d)
        inertialUpdater.setScale(.07)
        inertialUpdater.setPos(horizontalAlignment,0,.7)

        frictionUpdater=guiUtils.makeNumericalUpdater(
            "joint friction:",
            self.arm.setJointFriction,
            self.arm.jointFrictionCoefficient)
        frictionUpdater.reparentTo(aspect2d)
        frictionUpdater.setScale(.07)
        frictionUpdater.setPos(horizontalAlignment,0,.6)

        lengthUpdater=guiUtils.makeNumericalUpdater(
            "arm length:",
            self.arm.setLength,
            self.arm.length)
        lengthUpdater.reparentTo(aspect2d)
        lengthUpdater.setScale(.07)
        lengthUpdater.setPos(horizontalAlignment,0,.5)


# Here we are at the top-level of the script. This is where we actually create
# our world and go!
w=World()
w.init()
# This last function belongs to Panda and came in from importing DirectStart
# It runs forever, returning only when Panda has determined we want to quit
# the simulation (by closing the window, for example).
run()
