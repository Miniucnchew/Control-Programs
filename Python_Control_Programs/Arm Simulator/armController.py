"""
Mechanism for controlling the arm in the arm simulation demo

(C)2008 by Mark Tomczak (fixermark@gmail.com)

Free for educational and demonstration purposes, and for all uses regarding the
FIRST Robotics competition.

This program was built with Panda3D 1.4.2 (http://www.panda3d.org)
"""
from pandac.PandaModules import *
from PIDController import PIDController

class ArmController(NodePath):
    """
    A class that simulates a motor that is controlled by a PID controller
    driving a robotic arm. It is a child of a NodePath, meaning it can
    be put into the Panda scene.
    """
    def __init__(self,controlledArm):
        """
        Automatic function that builds an ArmController

        controlledArm: A PhysicsArm that we will control. Note that
        unlike in C or Java, this function doesn't have to know
        what a PhysicsArm contains (i.e. we didn't import anything
        or include a header that contains PhysicsArm). That's just
        how the Python programming language works; you can pass
        any value into a function and it figures it out on-the-fly.
        """
        NodePath.__init__(self,"arm controller")
        # remember my arm
        self.arm=controlledArm
        self.armHolder=self.attachNewNode("arm holder")
        # reference the look of the arm we control to the holder, so that
        # our green control bar has the same shape as the arm
        self.arm.armHolder.instanceTo(self.armHolder)
        # make the arm green and transparent
        self.armHolder.setColor(0,1,0,.4,3)
        self.armHolder.setTransparency(1)

        # create a controller. By default, all its gains are zero
        self.controller=PIDController(0,0,0)

    # the "setWhatever" functions set the P, I, and D values of the controller,
    # as well as the target angle the controller wants to reach
    def setKP(self,newKP):
        self.controller.kP=newKP

    def setKI(self,newKI):
        self.controller.kI=newKI
        self.controller.integrator=0

    def setKD(self,newKD):
        self.controller.kD=newKD

    def setTarget(self,newTarget):
        self.controller.setTarget(newTarget)
        # Changing the target rotates the green goal bar
        self.setR(newTarget)

    def step(self):
        """
        Run one simulation step. This is given to Panda by the main code
        to be run every frame.
        """
        # Get the arm's current rotation. This simulates a perfect sensor.
        currentR=self.arm.getR()

        # having gotten the arm's rotation, give it to the controller
        # and get the torque we desire from the result
        outputTorque=self.controller.step(currentR)

        # simulate a "perfect" motor by applying the torque straight to the
        # arm. If you want a more complicated motor simulation, this is
        # where you should put it.
        self.arm.applyTorque(outputTorque)
