"""measure your JND in orientation using a staircase method"""
from __future__ import print_function

from psychopy import core, visual, gui, data, event
from psychopy.tools.filetools import fromFile, toFile
import time, numpy, random
from subprocess import call

try:#try to get a previous parameters file
    expInfo = fromFile('TestData/lastParams.pickle')
except:#if not there then use a default set
    expInfo = {'observer':'ods7', 'waveform':1, 'frequency':20, 'starting amplitude':1000, 'offset':0, 'duration':5}
expInfo['dateStr']= data.getDateStr() #add the current time
#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='JND Exp', fixed=['dateStr'])
if dlg.OK:
    toFile('TestData/lastParams.pickle', expInfo)#save params to file for next time
else:
    core.quit()#the user hit cancel so exit

#make a text file to save data
fileName = 'TestData/' + expInfo['observer'] + expInfo['dateStr']
dataFile = open(fileName+'.csv', 'w')#a simple text file with 'comma-separated-values'
dataFile.write('amp_increment,difference_judgement\n')

#create the staircase handler
staircase = data.StairHandler(startVal = expInfo['starting amplitude'],
                          stepType = 'lin', stepSizes=10 ,#[8,4,4,2,2,1,1],
                          nUp=1, nDown=1,  #will home in on the 80% threshold
                          nTrials=10, minVal = 0, maxVal = 1000)

#create window and stimuli
win = visual.Window([800,600],allowGUI=True, monitor='testMonitor', units='cm', fullscr=True)
#and some handy clocks to keep track of time
globalClock = core.Clock()
trialClock = core.Clock()

#display instructions and wait
message1 = visual.TextStim(win, pos=[0,+3], text = 'This experiment will measure your ability to notice a change in the provided texture simulation.')
message2= visual.TextStim(win, pos=[0,-3],
    text="Press up if the amplitude of the texture differs  from  the given reference amplitude," + 
    " and down if no difference can be detected")
message3 = visual.TextStim(win, pos=[-2, -7], text='Hit a key when ready.')
message1.draw()
message2.draw()
message3.draw()
#fixation.draw()
win.flip()#to show our newly drawn 'stimuli'
#pause until there's a keypress
event.waitKeys()

message_stim1_wait = visual.TextStim(win, text = 'Stimulus 1 will begin in 1 second')
message_stim1 = visual.TextStim(win, text = 'Stimulus 1')
message_stim2_wait = visual.TextStim(win, text = 'Stimulus 2 will begin in 1 second')
message_stim2 = visual.TextStim(win, text = 'Stimulus 2')
message_response = visual.TextStim(win, text = 'If the two stimuli are identical press the left arrow key'
    +' , otherwise press the right arrow key. \n\n'
    +'If you would like to replay one of the stimuli, press the number key corresponding to the stimulus you would like to return to.')

def call_texture(stim, setAmp):
    #call c function through command line 
    if stim == 0:
        call(' '.join(["sudo ./parameter_test", str(expInfo['waveform']), str(expInfo['frequency']),
        str(expInfo['starting amplitude']), str(expInfo['offset']), str(expInfo['duration'])]), shell=True)
    elif stim == 1:
        call(' '.join(["sudo ./parameter_test", str(expInfo['waveform']), str(expInfo['frequency']),
        str(int(setAmp)), str(expInfo['offset']), str(expInfo['duration'])]), shell=True)
    else:
        pass

def message_disp(trial):
    if (trial == 1):
        message_stim1_wait.draw()
        win.flip()
        core.wait(1)
        message_stim1.draw()
        win.flip()
    elif (trial == 2):
        message_stim2_wait.draw()
        win.flip()
        core.wait(1)
        message_stim2.draw()
        win.flip()
    else:
        pass


exit_loop, i = 0, 0
while (quit == 0): #will step through the staircase
    
    stim_order = round(numpy.random.random())
    
    message_disp(1)
    call_texture(stim_order, int(thisIncrement))
    
    message_disp(2)
    call_texture((not stim_order), int(thisIncrement))
    
    core.wait(0.5)
    
    message_response.draw()
    win.flip()
    #get response
    thisResp=None
    while thisResp==None:
        allKeys=event.waitKeys()
        for thisKey in allKeys:
            if (thisKey == '1'): 
                call_texture(stim_order, int(thisIncrement))
            elif (thisKey == '2'):
                call_texture((not stim_order), int(thisIncrement))
            elif (thisKey == 'left'):
                thisResp = 1#correct
            elif (thisKey=='right'):
                thisResp = 0#incorrect
            elif thisKey in ['q', 'escape']:
                core.quit()#abort experiment
            else:
                pass
        event.clearEvents() #must clear other (eg mouse) events - they clog the buffer

    #add the data to the staircase so it can calculate the next level
    staircase.addResponse(thisResp)
    dataFile.write('%.3f,%i\n' %(thisIncrement, thisResp))
    core.wait(1)

#staircase has ended
dataFile.close()
staircase.saveAsPickle(fileName) #special python binary file to save all the info

#give some output to user in the command line in the output window
print('reversals:')
print(staircase.reversalIntensities)
print('mean of final 6 reversals = %.3f' %(numpy.average(staircase.reversalIntensities[-6:])))

#give some on screen feedback
feedback1 = visual.TextStim(win, pos=[0,+3],
    text='mean of final 6 reversals = %.3f' %
(numpy.average(staircase.reversalIntensities[-6:])))
feedback1.draw()
#fixation.draw()
win.flip()
event.waitKeys() #wait for participant to respond

win.close()
core.quit()
