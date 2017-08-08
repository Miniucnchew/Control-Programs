from appJar import gui
from subprocess import call

app = gui()

def call_fcn(btn):
    call(["sudo", ("./../C_Control_Programs/PIGPIO/"+btn)])

app.addButton("z_calibrate", call_fcn)
app.addButton("parameter_test", call_fcn)

app.go()
