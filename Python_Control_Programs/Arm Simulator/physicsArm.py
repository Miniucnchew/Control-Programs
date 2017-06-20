"""
Core arm simulator for the arm simulation demo

(C)2008 by Mark Tomczak (fixermark@gmail.com)

Free for educational and demonstration purposes, and for all uses regarding the
FIRST Robotics competition.

This program was built with Panda3D 1.4.2 (http://www.panda3d.org)
"""

from pandac.PandaModules import *

class PhysicsArm(NodePath):
    """
    Simulates a uniform-density arm and joint upon which physics can be
    applied. This contains the rules for drawing the arm in 3D space as
    well as the rules for moving the arm under the influence of physical
    forces applied to the arm.

    Most of the physics here is simple Newtonian mechanics; we don't go
    into a lot of detail and all the operations are assumed to be perfect.
    """
    # A Panda node (point in space) that will be used later for calculating
    # gravity
    GRAVITY_NODE=NodePath('gravity')
    def __init__(self):
        """
        Automatic constructor to build a PhysicsArm

        PhysicsArms are NodePaths (Panda nodes), so they can be put into
        the scene.
        """
        NodePath.__init__(self,"physics arm")
        # make a node to hold the arm model later.
        self.armHolder=self.attachNewNode("arm holder")
        # we just need armModel to be something, so create a dummy node
        self.armModel=NodePath("dummy model")
        # center-of-mass node
        self.comNode=NodePath("center of mass")
        self.comNode.reparentTo(self.armHolder)

        # Load a model to use as the sphere for the center of mass. This
        # is wrappedin a Try block because the model might be missing from
        # the "models/smiley.egg" location. If it is, we just won't ever
        # draw the center-of-mass.
        #
        # The model should always be available under Windows, but I haven't
        # tested it yet under Linux.
        try:
            comModel=loader.loadModel("models/smiley")
            comModel.setScale(.15)
            comModel.setRenderModeWireframe()
            comModel.setColor(1,0,0,1)
            comModel.setTextureOff(3)
            comModel.setLightOff()
            comModel.reparentTo(self.comNode)
        except Exception:
            pass

        # The physical properties
        # Time step: How much time progresses every frame. We set this
        # to 1/10th of a second by default.
        self.deltaT=.1
        # Length of the arm, in feet.
        self.length=3
        # Mass of the arm, in pounds.
        self.mass=1
        # Joint friction coefficient: What proportion of velocity is
        # lost every second to heat energy as the joint grinds back and forth
        # in its socket.
        self.jointFrictionCoefficient=0.1
        # The moment of inertial along the axis of joint rotation
        self.momentOfInertia=10
        # Percentage along the arm at which the center of mass is located.
        # For an arm of perfectly uniform density, this is .5, or 50%
        self.comOffset=.5
        # Starting angular velocity, which is zero,
        self.angularVelocity=0
        # using the gravity acceleration for US units, ft/second^2
        # NOTE: This is the only physical constant in the simulation (besides
        # time-step), so if you want to simulate using metric units, all
        # you need to do is change this value to 9.8, which is the acceleration
        # due to gravity in meters/second.
        self.gravity=32.

        # The total torque that will act on the arm this frame. Starts at
        # zero
        self.torqueAccumulator=0
        

    def setModel(self,newModel):
        """
        Sets the model that is used to represent the arm
        """
        self.armModel=newModel
        self._resizeArmModel()

    def setLength(self,newLength):
        """
        Sets the length of the arm
        """
        self.length=newLength
        self._resizeArmModel()

    def setMass(self,newMass):
        """
        Sets the mass of the arm
        """
        self.mass=newMass

    def setMomentOfInertia(self,newMoment):
        """
        Sets the arm's moment of inertia
        """
        self.momentOfInertia=newMoment

    def setJointFriction(self,newFriction):
        """
        Sets the friction in the arm's joint.
        """
        self.jointFrictionCoefficient=newFriction

    def _resizeArmModel(self):
        """
        Re-positions and scales the arm model appropriately. This is
        a "helper function" and no-one but the arm's code should ever
        need to call it directly (i.e. the rule is "If you need to change
        the arm's length, ask the arm to do so by using setLength; the arm
        will handle re-sizing the draw and center-of-mass pieces for you."
        """
        self.armModel.setScale(self.length,1,1)
        self.armModel.reparentTo(self.armHolder)
        self.armModel.setPos(self.length/2.,0,0)

        self.comNode.setX(self.length*self.comOffset)

    def applyTorque(self,torque):
        """
        Applies a torque to the arm from an external source. Torques get
        'used up' in stepPhysics and must be re-applied every frame to
        be continuous.

        torque: Torque to apply this frame, in foot-pounds
        """
        self.torqueAccumulator += torque

    def stepPhysics(self):
        """
        This function is called by Panda's animation engine every frame to
        move the arm as a result of the physics applied to it.
        """
        # First, apply gravity and friction to the arm
        self._stepGravity()
        self._stepFriction()

        # Now, change the arm's velocity as a result of angular acceleration,
        # which is a result of the torques acting upon it.
        # Sources of torque for the arm: gravity (pulls it down), friction
        # (slows it down), motor (tries to push the arm to get to the goal).
        #
        # Acceleration is resisted by the moment of inertia. The higher the
        # moment of inertia, the more torque is needed to change velocity.
        #
        # Finally, we multiply by the timestep, which runs the simulation
        # more accurately at the cost of doing everything a little more
        # slowly.
        self.angularVelocity += (self.torqueAccumulator /
                                 self.momentOfInertia *
                                 self.deltaT)
        # We applied all the torques, so clear the accumulator.
        self.torqueAccumulator=0

        # finally, apply the angular velocity by changing the rotation on
        # the arm!
        #
        # NOTE: There is probably a slight mistake here: setR expects
        # the value to be in degrees, but the angular velocity is in radians
        # per time step. We probably want to do a degree/radian conversion here!
        self.setR(self.getR() - self.angularVelocity)

    def _stepGravity(self):
        """
        Applies the effect of gravity on the arm

        This uses a little Panda trickery to find the gravity effect.
        It's not strictly necessary to understand how it works, but the
        basic idea is that we put the GRAVITY_NODE on the center of mass.
        Then, we push it down along the gravity vector to put the node
        at a distance from the center-of-mass equal to gravity's force
        on the center of mass. Finally, we switch and look at the position
        in the frame-of-reference of the arm---in that frame, the Z-axis
        of the GRAVITY_NODE's position is the component of the gravity force
        that acts perpendicular to the arm (and thus is applying torque).
        """
        # 1) Switch to the arm's frame of reference and put the gravity
        #    node on top of the center of mass
        self.GRAVITY_NODE.reparentTo(self.comNode)
        self.GRAVITY_NODE.setPos(0,0,0)
        self.GRAVITY_NODE.setHpr(0,0,0)
        self.GRAVITY_NODE.setScale(1,1,1)

        # 2) Switch to the global frame of reference and drop the gravity
        #    node along the gravity vector
        self.GRAVITY_NODE.wrtReparentTo(render)
        self.GRAVITY_NODE.setZ(self.GRAVITY_NODE.getZ()-self.gravity)

        # 3) Switch back to the arm's frame of reference and get the
        #    gravity's force on the arm at the center-of-mass.
        self.GRAVITY_NODE.wrtReparentTo(self)
        torqueNewtons=self.GRAVITY_NODE.getZ()

        # Torque is a force times lever arm length, so multiply by the
        # center-of-mass's distance from the joint
        torque=torqueNewtons*self.comNode.getX()

        # Apply the gravity torque to the arm
        self.applyTorque(torque)

    def _stepFriction(self):
        """
        Applies the effect of friction in the joint on the arm
        """
        # Friction is a fairly simple effect---it just resists the motion
        # of the joint more the faster the joint is rotated.
        friction=-self.angularVelocity*self.jointFrictionCoefficient
        self.applyTorque(friction)

