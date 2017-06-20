"""
ROBOT ARM SIMULATION

(C)2008 by Mark Tomczak (fixermark@gmail.com)

Free for educational and demonstration purposes, and for all uses regarding the
FIRST Robotics competition.

This program was built with Panda3D 1.4.2 (http://www.panda3d.org)
"""

"""
ABOUT THE ARM DEMO

To use the demo, you will first need to install Panda3D 1.4.2, which can be
found at http://panda3d.org/download.php. Once you have done so, Windows
users can double-click on the "run.bat" script to start the program. Users
of Mac OS or various Linux distros can execute the main.py Python script using
the version of Python bundled in the Panda installation.

This program is a simple simulation of a robot arm controlled via a PID
feedback controller. The grey slab and blue bar represent the robot's body,
while the red bar with the sphere at the center of mass represents the robot's
arm. The green transparent bar is a target angle (specified via the "goal"
value) that the arm should travel to.

On the left are inputs for the controller itself---proportional, integral, and
derivative---as well as a goal rotation (in degrees clockwise from
horizontal). On the right are properties of the arm configuration---mass,
moment of inertia, friction in the joint, and the length of the arm.
All units are assumed to be American standard (feet, pounds, seconds).

When the demo starts, the green bar will show a goal of holding the arm
horizontally, while the red bar swings freely like a pendulum---the controller
is providing zero power. To use the demo, change the values on the left and
right by clicking on them, deleting the previous value, entering a new one,
and hitting the "enter" key on your keyboard to update the value. You can also
use the mouse to move around in the simulation---left click translates the
camera, right-click zooms in and out, and middle-click rotates the camera.
"""

"""
QUESTIONS

* How good is this simulation? Does it really do what an actual arm like this
  would do?
  
The simulation is not extremely accurate and is intended to serve mostly
as a visual demonstration of how a PID controller would affect a system
such as this. But if you want, you can extend the simulation to be more
accurate! Some inaccuracies the author is aware of:

- There are a few mistakes in the physics calculations in armController.py.
  The documentation in that function goes into detail on them.
- The time-step is constant and does not adjust for framerate, so the simulation
  is not real-time (i.e. the period of the pendulum is not correct, time
  estimates made based on the simulation would be wrong, etc). There are a
  couple of ways to fix this, but I would sacrifice realtime behavior for
  accuracy. Changing the deltaT (in physicsArm.py) based on framerate can lead
  to non-deterministic behavior that ends up being pretty unrealistic. If you
  want to use the simulator to predict how an actual robot would behave, add
  a clock display and go with the times the simulation calculates.
- The motor in armController.py is a perfect motor, which has infinite free
  speed and torque. This is, of course, never true. A much more realistic
  motor model could be the single greatest improvement to this simulation.
- The integrator used in the PID controller is a simple accumulator. There
  are better models with different resulting design issues.

* I want to use PID control on my robot! How do I do that?

While the simulator isn't highly accurate, the core concepts behind PID
control are universal. The documentation in PIDController.py goes into some
detail on them; if you want to use them on the robot, they should be
re-creatable in C.

* This isn't written in EasyC! What is this strange language?

Python is a relatively modern scripting language that includes high-level
features (such as lists, objects, and dictionaries) built-in to the language
itself. It is used by the Panda3D game and graphics engine for controlling
the drawing, input, sound, physics, and other rules of the system. The language
has its own integrated debugger and code editor and is designed to be as
simple to use as possible.

Personally, I'm a huge fan of Panda for projects like this; I was able to write about
80% of the code over three hours on a Sunday, and the rest of the work was
mostly writing comments and fine-tuning. If you're interested in learning
a new language, you can find more information about Python at their website
(http://python.org). Panda3D's information can be found at their website
(http://www.panda3d.org).

One note about Python that often confuses new programmers: unlike most
programming languages, Python uses whitespace as a "syntactically significant"
element. What this means is that you have to structure your code blocks a
certain way for Python to understand them. For example, whereas in C an
if-then block can look like this:

if(condition) {
    doThing1();
    doSomethingElse();
}
doMoreThings();

... or this...

if(condition) {doThing1(); doSomethingElse(); }
doMoreThings();

... in Python, an if-then-else block must look like this:

if condition:
    doThing1()
    doSomethingElse()
doMoreThings()

The four-space indentation before "doThing1()" tells Python that doThing1 is
inside the if-block, and every line after that starts with four spaces is still
inside the if-block. If you delete or change the whitespace, Python won't know
that doSomethingElse() is inside the if-block but doMoreThings() is not.

This design feature can be a real headache if you try to use a conventional text
editor to write Python code---especially since four spaces is different from
one tab but can look the same. I geerally recommend a smart text editor for
writing Python (you can find examples using Google or at python.org). But if
you want to get started immediately, you can use IDLE, the editor built into
Python. To do so, try the following on the command line (this example shows
Windows, but a similar process works in other operating systems):

C:\> ppython
Python 2.4.4 (#71, Oct 18 2006, 08:34:43) [MSC v.1310 32 bit (Intel)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> from idlelib import idle

This will bring up IDLE's shell, and you can use the "File" menu to open a .py
file.

* Typing in numbers is boring. Could I control this with a joystick?

Joystick support isn't impossible, but you'd have to add a bit more Python code.
My recommendation would be to use the pygame library (http://pygame.org/) and
integrate its joystick control features. See the forums on Panda's website
for more information on how to do this.

Once you have the joystick integrated, simply add another animation to read
the current joystick value and put it into the controller every frame.

* Hey, I found a bug!
Thank you! I'm sorry that snuck by me; this was a quick project so I'm sure
there are several. If you let me know at fixermark@gmail.com, I will create
a fix.

* I have additional questions!
You can feel free to write the original author of this demo at
fixermark@gmail.com

Enjoy the demo, and best of luck with the competition!

Sincerely,
Mark Tomczak, Pittsburgh, PA
Alumnus, Team 422 "The Mech Techs," Richmond, VA
"""
