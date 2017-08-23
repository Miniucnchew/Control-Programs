"""measure your JND in orientation using a staircase method"""
from __future__ import print_function

from psychopy import core, visual, gui, data, event
from psychopy.tools.filetools import fromFile, toFile
import time, numpy, random
from subprocess import call

try:#try to get a previous parameters file
    expInfo = fromFile('TestData/FrequencyData/lastParams.pickle')
except:#if not there then use a default set
    expInfo = {'subject ID':'s1_1', 'waveform':1, 'frequency':20, 'starting amplitude':300, 'duration':5, 'max reversals':8}
#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='JND Exp')
if dlg.OK:
    toFile('TestData/FrequencyData/lastParams.pickle', expInfo)#save params to file for next time
else:
    core.quit()#the user hit cancel so exit

#make a text file to save data
fileName = 'TestData/FrequencyData/' + expInfo['subject ID'] 
dataFile = open(fileName+'.txt', 'w')#a simple text file
dataFile.write('Texture 1 Freq | Texture 2 Freq | User Response | Response Correct? | Reversal Point?\n')
#                           14            |           14          |           13          |             17               |             15         
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
message_response = visual.TextStim(win, text = 'If the first texture had a higher frequency, press the left arrow key'
    +' ,if the second texture had a higher frequency, press the right arrow key.'
    +' If you are unsure of which stimulus has a higher frequency, press the down arrow key. \n\n'
    +'If you would like to replay one of the stimuli, press the number key corresponding to the stimulus you would like to return to.')
image_response = visual.ImageStim(win, image = 'PsychExperiment_KeyboardInstructions_Frequency.png', units = 'pix', interpolate = True)#, size = [1440, 1080]), pos = [0, -2])

offset = 1500

def call_texture(stim, setFreq):
    #call c function through command line 
    if stim == 0:
        call(' '.join(["sudo ./parameter_test", str(expInfo['waveform']), str(expInfo['frequency']),
        str(expInfo['starting amplitude']), str(offset), str(expInfo['duration'])]), shell=True)
    elif stim == 1:
        call(' '.join(["sudo ./parameter_test", str(expInfo['waveform']), str(int(setFreq)),
        str(expInfo['starting amplitude']), str(offset), str(expInfo['duration'])]), shell=True)
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
    elif (trial == 3):
        win.setColor('grey')
        win.flip()
        image_response.draw()
        win.flip()
    else:
        pass


resp_corr, reversals = [], []
exit_loop, i = 0, 0
newFreq = expInfo['frequency']*2 + int(numpy.random.random()*10-5) # newAmp starts greater than the constant amplitude
#newAmp = expInfo['starting amplitude']/2 # newAmp starts less than the constant amplitude
response_dict = {0:'Unsure', 1:'1st', 2:'2nd'}


step_size = [8,7,6,5,4,3,2,1] 

while exit_loop == 0: 
    
    stim_order = round(numpy.random.random())
    if stim_order == 0:
        firstFreq = expInfo['frequency']
        secondFreq = newFreq
    else:
        firstFreq = newFreq
        secondFreq = expInfo['frequency']
    
    message_disp(1)
    call_texture(stim_order, int(newFreq))
    
    message_disp(2)
    call_texture((not stim_order), int(newFreq))
    
    core.wait(0.1)
    message_disp(3)
#    win.setColor('grey')
#    win.flip()
#    image_response.draw()
#    win.flip()
#        
    #get response
    thisResp=None
    while thisResp==None:
        allKeys=event.waitKeys()
#        allKeys = iohub.client.keyboard.KeyboardPress()
        for thisKey in allKeys:
            if (thisKey == '1'): 
                message_disp(1)
                call_texture(stim_order, int(newFreq))
                message_disp(3)
            elif (thisKey == '2'):
                message_disp(2)
                call_texture((not stim_order), int(newFreq))
                message_disp(3)
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
    
    oldFreq = newFreq
    
    if ((thisResp == 1) and (firstFreq > secondFreq)) or ((thisResp == 2) and (firstFreq < secondFreq)):
        if (len(step_size) > len(reversals)):
            newFreq -= step_size[len(reversals)] # Correct response - Reduce difference by one step
        else:
            newFreq -= step_size[len(step_size)-1] # Correct response - Reduce difference by one step
        resp_corr += [1]
    elif ((thisResp == 1) and (firstFreq <= secondFreq)) or ((thisResp == 2) and (firstFreq >= secondFreq)):
        if (len(step_size) > len(reversals)):
            newFreq += 3*step_size[len(reversals)] # Incorrect response - Increase difference by 3 steps
        else:
            newFreq += 3*step_size[len(step_size)-1] # Incorrect response - Increase difference by 3 steps
        resp_corr += [0]
    elif (thisResp == 0):
        if (len(step_size) > len(reversals)):
            newFreq += step_size[len(reversals)] # Unsure response - Increase difference by 1 step
        else:
            newFreq += step_size[len(step_size)-1] # Unsure response - Increase difference by 1 step
        resp_corr += [0]
    
    if (newFreq < expInfo['frequency']):
        newFreq = expInfo['frequency']
    elif (newFreq > 100):
        newFreq = 100
    
#    print(resp_corr)
    reversal_point = 'False'
    if (len(resp_corr) > 2):
        if ((resp_corr[i] - resp_corr[i-1]) != 0):
            reversals += [[i, oldFreq]]
            reversal_point = 'True'
        else:
            reversal_point = 'False'
    
    if (len(reversals) >= expInfo['max reversals']):
        exit_loop = 1
        
    write_list = ['{:^13d}'.format(firstFreq), '{:^14d}'.format(secondFreq), '{:^14}'.format(response_dict[thisResp]), '{:^17d}'.format(resp_corr[i]), '{:^15}'.format(reversal_point)]
    
    
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



#with open('s1_4.txt') as file:
#    data = file.readlines()
#data
#data
#data = [x.rstrip('\n') for x in data]
#data
#data = [int(x) for x in data]









