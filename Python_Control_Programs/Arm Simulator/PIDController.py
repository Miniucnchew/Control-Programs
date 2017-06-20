"""
PID Controller for the arm simulation demo

(C)2008 by Mark Tomczak (fixermark@gmail.com)

Free for educational and demonstration purposes, and for all uses regarding the
FIRST Robotics competition.

This program was built with Panda3D 1.4.2 (http://www.panda3d.org)
"""

# A PID controller (proportional, integral, derivative) is an error-based
# control system that is great for simulating smooth motion. There is evidence
# to suggest that the human body's joints and muscles are controlled by
# activity in the brain that is not entirely unlike a PID controller!
#
# Essentially, a PID controller has five important values:
#
# TARGET -- The input value we want to receive. When the input value matches
# the target and the system is steady, the controller doesn't need to make
# any changes!
#
# ERROR -- The amount by which the input differs from the target. Higher
# errors warrant more corrective action.
#
# kP -- The proportional gain. Determines how much the proportional model
# matters.
#
# kI -- The integral gain. Determines how much the integral model matters.
#
# kD -- The derivative gain. Determines how much the derivative model matters.
#
# These values are used in three control models, which are summed together to
# get an output result (the value that the controller thinks can be used to
# modify the system so the error decreases).
#
# PROPORTIONAL
# kP * e
#
# The easiest model to understand, proportional control is one simple rule:
# "The larger the error, the more we correct."  Mathematically, it is like
# a spring: When you pull or push a spring, it tugs harder the further you
# move it away from its resting position. But like a spring, a P control
# system can easily overshoot, forever oscillating around the goal value.
#
# DERIVATIVE
# kD * de/dt
#
# While proportional deals with the current error, derivative deals with the
# change from the previous error (i.e. if the error is an error of position,
# derivative control looks at velocity). Derivative control tries to avoid
# overshooting the goal by decreasing the control response an amount
# proportional to how quickly the error is changing. Mathematically, it is
# like friction: The faster the controller is homing in on the correct value,
# the more this model resists further changes.
#
# INTEGRAL
# kI * SUM(e,time)
#
# While proportional and derivative control can make very smooth motion,
# it is possible for them to reach a "steady state" in which the output value
# is perfectly balanced every cycle by external forces (such as the constant
# pull of gravity), but the goal has not been reached. This is called "steady
# state error," and can be a problem if very accurate control is needed.
#
# The integral model is intended to eliminate steady state error. It does
# so by accumulating all the error that hasn't been eliminated over time.
# If an erroneous steady state occurs, the integral model will continue
# to grow, eventually overriding the external forces and causing the system
# to reach the goal. Having higher values of kI will cause the system
# to take less time to reach steady state at the goal.
#
# While this model can be very useful for perfecting the behavior of the
# controller, it must be used carefully. Having a kI too high can cause
# this component to dominate the other two, eventually throwing the
# arm into an out-of-control situation where it oscillates itself further
# and further from the goal state. To avoid this instability, keep kI very
# small. A lot of systems can actually ignore the kI term and use only the
# kP and kD terms; these are called PD controllers and are immune to
# feedback instability.


class PIDController:
    def __init__(self,p,i,d):
        self.kP=p
        self.kI=i
        self.kD=d
        self.target=0

        self.lastError=0
        self.integrator=0

    def setTarget(self,newTarget):
        self.target=newTarget
        self.integrator=0

    def step(self,currentValue):
        """
        Calculates the error and derives a desired output value.
        """
        # determine the error by simply looking at the difference between
        # current value and target value.
        error=currentValue-self.target

        # Build the output by summing the contributions of the
        # proportional, integral, and derivative models.
        output= (self.kP * error
                 + self.kI * self.integrator
                 + self.kD * (error - self.lastError)
                 )

        # Remember the error for the derivative model
        self.lastError=error
        # Add the error to the integral model
        self.integrator+=error

        return output
