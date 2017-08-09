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
dataFile.write('new_amp,user_resp, resp_correct\n')

#create window and stimuli
win = visual.Window([800,600],allowGUI=True, monitor='testMonitor', units='cm', fullscr=True)
#and some handy clocks to keep track of time
globalClock = core.Clock()
trialClock = core.Clock()

#display instructions and wait
message1 = visual.TextStim(win, pos=[0,+3], text = 'This experiment will measure your ability to notice a change in the provided texture simulation.')
message2= visual.TextStim(win, pos=[0,-3],
    text="Press the left arrow key if the two stimuli are identical," + 
    " and the right arrow key if they are different. If you are unsure, press the down arrow key.")
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
message_response = visual.TextStim(win, text = 'If the first stimulus was stronger, press the left arrow key'
    +' ,if the second stimulus was stronger, press the right arrow key.'
    +' If you are unsure of which stimulus is stronger, press the down arrow key. \n\n'
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


resp_corr, reversals = [], []
exit_loop, i = 0, 0
newAmp = expInfo['starting amplitude']
while exit_loop == 0: 
    
    step_size = 10
    
    diff = abs(expInfo['starting amplitude'] - newAmp)
    
    stim_order = round(numpy.random.random())
    if stim_order == 0:
        firstAmp = expInfo['starting amplitude']
    else:
        firstAmp = newAmp
    
    message_disp(1)
    call_texture(stim_order, int(newAmp))
    
    message_disp(2)
    call_texture((not stim_order), int(newAmp))
    
    core.wait(0.5)
    
    message_response.draw()
    win.flip()
    #get response
    thisResp=None
    while thisResp==None:
        allKeys=event.waitKeys()
        for thisKey in allKeys:
            if (thisKey == '1'): 
                call_texture(stim_order, int(newAmp))
            elif (thisKey == '2'):
                call_texture((not stim_order), int(newAmp))
            elif (thisKey == 'left'):
                thisResp = 1
            elif (thisKey== 'right'):
                thisResp = 2
            elif (thisKey == 'down'):
                thisResp = 0
            elif thisKey in ['q', 'escape']:
                core.quit()#abort experiment
            else:
                pass
        event.clearEvents() #must clear other (eg mouse) events - they clog the buffer
    
    oldAmp = newAmp
    
    if ((thisResp == 1) and (firstAmp > expInfo['starting amplitude'])) or ((thisResp == 2) and (firstAmp > expInfo['starting amplitude'])):
        newAmp = expInfo['starting amplitude']-(diff-step_size) # Correct response - Reduce difference by one step
        resp_corr += [1]
    elif ((thisResp == 1) and (firstAmp < expInfo['starting amplitude'])) or ((thisResp == 1) and (firstAmp < expInfo['starting amplitude'])):
        newAmp = expInfo['starting amplitude']-(diff+3*step_size) # Incorrect response - Increase difference by 3 steps
        resp_corr += [0]
    elif (thisResp == 0):
        newAmp = expInfo['starting amplitude']-(diff+step_size) # Unsure response - Increase difference by 1 step
        resp_corr += [0]
    
    if (len(resp_corr) > 2):
        if ((resp_corr[i+1] - resp_corr[i]) != 0):
            reversals += [i, oldAmp]
    
    if (len(reversals) > 3):
        exit_loop = 1
    write_list = [newAmp, thisResp, resp_corr[i]]
    dataFile.write(','.join(str(e) for e in write_list))
    core.wait(1)
    i += 1

#staircase has ended
dataFile.close()

#give some output to user in the command line in the output window
print('reversals:')
print([l[1] for l in reversals])
#print('mean of final 6 reversals = %.3f' %(numpy.average(staircase.reversalIntensities[-6:])))
print('mean of reversal intensities = ' + str(numpy.average([l[1] for l in reversals])))
#give some on screen feedback
feedback1 = visual.TextStim(win, pos=[0,+3],
    text='mean of final 6 reversals = %.3f' + str(numpy.average([l[1] for l in reversals])))
feedback1.draw()
#fixation.draw()
win.flip()
event.waitKeys() #wait for participant to respond

win.close()
core.quit()
