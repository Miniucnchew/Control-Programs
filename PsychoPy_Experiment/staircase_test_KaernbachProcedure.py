"""measure your JND in orientation using a staircase method"""
from __future__ import print_function

from psychopy import core, visual, gui, data, event
from psychopy.tools.filetools import fromFile, toFile
import time, numpy, random
from subprocess import call

try:#try to get a previous parameters file
    expInfo = fromFile('TestData/lastParams.pickle')
except:#if not there then use a default set
    expInfo = {'subject ID':'s1_1', 'waveform':1, 'frequency':20, 'starting amplitude':300, 'duration':5, 'max reversals':8}
#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='JND Exp')
if dlg.OK:
    toFile('TestData/lastParams.pickle', expInfo)#save params to file for next time
else:
    core.quit()#the user hit cancel so exit

#make a text file to save data
fileName = 'TestData/' + expInfo['subject ID'] 
dataFile = open(fileName+'.txt', 'w')#a simple text file
dataFile.write('Texture 1 Amp | Texture 2 Amp | User Response | Response Correct? | Reversal Point?\n')
#                           13            |           13          |           13          |             17               |             15         
#create window and stimuli
win = visual.Window([1600,1200],allowGUI=False, monitor='testMonitor', units='cm', fullscr=True)
win.mouseVisible = False
#and some handy clocks to keep track of time
globalClock = core.Clock()
trialClock = core.Clock()

#display instructions and wait
message1 = visual.TextStim(win, pos=[0,+3], text = 'This experiment will measure your ability to discriminate between two texture simulations.')
#message2= visual.TextStim(win, pos=[0,-3],
#    text="Press the left arrow key if the first textureis stronger," + 
#    " and the right arrow key if the second texture is stronger. If you are unsure, press the down arrow key.")
message3 = visual.TextStim(win, pos=[-2, -7], text='Hit any key to continue.')
message1.draw()
#message2.draw()
message3.draw()
#fixation.draw()
win.flip()#to show our newly drawn 'stimuli'
#pause until there's a keypress
event.waitKeys()

message_stim1_wait = visual.TextStim(win, text = 'Texture 1 will begin in 1 second')
message_stim1 = visual.TextStim(win, text = 'Texture 1')
message_stim2_wait = visual.TextStim(win, text = 'Texture 2 will begin in 1 second')
message_stim2 = visual.TextStim(win, text = 'Texture 2')
message_response = visual.TextStim(win, text = 'If the first texture was stronger, press the left arrow key'
    +' ,if the second texture was stronger, press the right arrow key.'
    +' If you are unsure of which stimulus is stronger, press the down arrow key. \n\n'
    +'If you would like to replay one of the stimuli, press the number key corresponding to the stimulus you would like to return to.')
image_response = visual.ImageStim(win, image = 'PsychExperiment_KeyboardInstructions.png', units = 'pix', interpolate = True)#, size = [1440, 1080]), pos = [0, -2])

offset = 1500

def call_texture(stim, setAmp):
    #call c function through command line 
    if stim == 0:
        call(' '.join(["sudo ./parameter_test", str(expInfo['waveform']), str(expInfo['frequency']),
        str(expInfo['starting amplitude']), str(offset), str(expInfo['duration'])]), shell=True)
    elif stim == 1:
        call(' '.join(["sudo ./parameter_test", str(expInfo['waveform']), str(expInfo['frequency']),
        str(int(setAmp)), str(offset), str(expInfo['duration'])]), shell=True)
    else:
        pass

def message_disp(trial):
    if (trial == 1):
        win.setColor('blue')
        win.flip()
        message_stim1_wait.draw()
        win.flip()
        core.wait(1)
        message_stim1.draw()
        win.flip()
    elif (trial == 2):
        win.setColor('green')
        win.flip()
        message_stim2_wait.draw()
        win.flip()
        core.wait(1)
        message_stim2.draw()
        win.flip()
    else:
        pass


resp_corr, reversals = [], []
exit_loop, i = 0, 0
newAmp = expInfo['starting amplitude']*2 + int(numpy.random.random()*100-50) # newAmp starts greater than the constant amplitude
#newAmp = expInfo['starting amplitude']/2 # newAmp starts less than the constant amplitude
response_dict = {0:'Unsure', 1:'1st', 2:'2nd'}

#step_size = [int(newAmp*(1./2.)**n) for n in [2,3,3,4,4,5,5,6,6]]
#step_size = [100, 100, 75, 50, 50, 25, 25]
#step_size = [100, 80, 60, 50, 40, 25, 15]
step_size = [110, 75, 40, 30, 20, 15, 10] 

while exit_loop == 0: 
    
    diff = expInfo['starting amplitude'] - newAmp
    
    stim_order = round(numpy.random.random())
    if stim_order == 0:
        firstAmp = expInfo['starting amplitude']
        secondAmp = newAmp
    else:
        firstAmp = newAmp
        secondAmp = expInfo['starting amplitude']
    
    message_disp(1)
    call_texture(stim_order, int(newAmp))
    
    message_disp(2)
    call_texture((not stim_order), int(newAmp))
    
    core.wait(0.5)
    win.setColor('grey')
    win.flip()
    image_response.draw()
    win.flip()
    
    #get response
    thisResp=None
    while thisResp==None:
        allKeys=event.waitKeys()
#        allKeys = iohub.client.keyboard.KeyboardPress()
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
                thisResp = None 
        event.clearEvents() #must clear other (eg mouse) events - they clog the buffer
    
#    print(thisResp)
    
    oldAmp = newAmp
    
    if ((thisResp == 1) and (firstAmp > secondAmp)) or ((thisResp == 2) and (firstAmp < secondAmp)):
        if (len(step_size) > len(reversals)):
            newAmp -= step_size[len(reversals)] # Correct response - Reduce difference by one step
        else:
            newAmp -= step_size[len(step_size)-1] # Correct response - Reduce difference by one step
        resp_corr += [1]
    elif ((thisResp == 1) and (firstAmp <= secondAmp)) or ((thisResp == 2) and (firstAmp >= secondAmp)):
        if (len(step_size) > len(reversals)):
            newAmp += 3*step_size[len(reversals)] # Incorrect response - Increase difference by 3 steps
        else:
            newAmp += 3*step_size[len(step_size)-1] # Incorrect response - Increase difference by 3 steps
        resp_corr += [0]
    elif (thisResp == 0):
        if (len(step_size) > len(reversals)):
            newAmp += step_size[len(reversals)] # Unsure response - Increase difference by 1 step
        else:
            newAmp += step_size[len(step_size)-1] # Unsure response - Increase difference by 1 step
        resp_corr += [0]
    
    if (newAmp < expInfo['starting amplitude']):
        newAmp = expInfo['starting amplitude']
    elif (newAmp > 1000):
        newAmp = 1000
    
#    print(resp_corr)
    reversal_point = 'False'
    if (len(resp_corr) > 2):
        if ((resp_corr[i] - resp_corr[i-1]) != 0):
            reversals += [[i, oldAmp]]
            reversal_point = 'True'
        else:
            reversal_point = 'False'
    
    if (len(reversals) >= expInfo['max reversals']):
        exit_loop = 1
        
    write_list = ['{:^13d}'.format(firstAmp), '{:^13d}'.format(secondAmp), '{:^13}'.format(response_dict[thisResp]), '{:^17d}'.format(resp_corr[i]), '{:^15}'.format(reversal_point)]
    
    
    dataFile.write(' | '.join(str(e) for e in write_list) + '\n')
    core.wait(1)
    i += 1
#    print(i)
#    print(str(reversals)+'\n')
#staircase has ended

#data_params = [ 
dataFile.close()

#give some output to user in the command line in the output window
print('reversals:')
print([l[1] for l in reversals])
#print('mean of final 6 reversals = %.3f' %(numpy.average(staircase.reversalIntensities[-6:])))
print('mean of reversal intensities = ' + str(numpy.average([l[1] for l in reversals])))
#give some on screen feedback
feedback1 = visual.TextStim(win, pos=[0,+3],
    text='mean of final 6 reversals = ' + str(numpy.average([l[1] for l in reversals])))
feedback1.draw()
#fixation.draw()
win.flip()
event.waitKeys() #wait for participant to respond

win.close()
core.quit()
