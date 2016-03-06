# -*- coding: utf-8 -*-
"""
Created on Tue Mar 01 20:18:06 2016

@author: marcus

1)  Open 'Monitor Center' in PsychoPy and fill in the numbers
    relevant for your setup (use 'testMonitor').
2) Connect the EyeTribe and start the EyeTribe server
3) Run the 'native' calibration using the EyeTribe UI.
3)  Run this script (Ctrl+r in PsychoPy)

"""

from psychopy import visual, core, data, event, monitors, misc
from psychopy.iohub import launchHubServer


# Set up the geometry for the monitor (can also be done in monitor center)
monitorName = 'default'
monitorRes  = [1920, 1200]
thisMon = monitors.Monitor(monitorName) # Defined in defaults file
thisMon.setWidth(53)    # Width of screen (cm)
thisMon.setDistance(60) # Distance eye / monitor (cm) 
thisMon.setSizePix(monitorRes)

###### Eye tracker integration with ioHub ####


iohub_config={
"psychopy_monitor_name":'default',
"eyetracker.hw.theeyetribe.EyeTracker":{}, # Here you can change to another eye tracker
"experiment_code":'mn_test', 
"session_code":'today'
}

io=launchHubServer(**iohub_config)
tracker=io.devices.eyetracker # Use 'native' calibration procedure in EyeTribe------------------

############################################# 

# create the window to draw in. Tel it to draw in degrees.
win = visual.Window(size = (800,800),fullscr = True, monitor=thisMon,units='deg')
win.setMouseVisible(False)

# Factor to scale coordinates in Excel file
sc_f = 4

#create a stimulus dot
dot         = visual.GratingStim(win,tex=None,mask='circle',color="black",size=0.25)
dot_center  = visual.GratingStim(win,tex=None,mask='circle',color="white",size=0.05)
text_stim   = visual.TextStim(win,text='Fixate the dots \n\n (Press space to continue)',color="white",height=1)


# Read trials from an Excel file
trialList   = data.importConditions('stim_FS.xlsx')
trials      = data.TrialHandler(trialList,1, method='sequential') #1 repetition

# Inform ioHub about the TrialHandler 
io.createTrialHandlerRecordTable(trials)

# Display instruction
text_stim.draw()
win.flip()
event.waitKeys() # Wait for keypress

#########
io.clearEvents("all")   
tracker.enableEventReporting(True)
#########

# Run through the trial in trialList
trial_no = 1
for trial in trials:
    
    # Set position of dot and draw it, and show (flip) it on the screen
    target_x, target_y = trial['posx']*sc_f,trial['posy']*sc_f
    dot.setPos((target_x, target_y))
    dot.draw()
    dot_center.setPos((target_x, target_y))
    dot_center.draw()   
    flip_time = win.flip() 
    
    # Send message about trial
    trial['trial_id']    = trial_no 
    trial['TRIAL_START'] = flip_time   
    trial['posx'] = misc.deg2pix(target_x,thisMon)    # Convert to pixels to match EDQ scripts
    trial['posy'] = misc.deg2pix(target_y,thisMon)    # Convert to pixels to match EDQ scripts

    
    # Show the dot for the duration specified in the Excel sheet
    # (would be more accurate to wait in multiples of the screen refresh rate)
    dot_duration = trial['dt']/1000.0
    core.wait(dot_duration)
    
    trial['TRIAL_END']=flip_time + dot_duration
    
    # Add trial info to iohub
    io.addRowToConditionVariableTable(trial.values()) 
    
    # increment trial number
    trial_no += 1

    # Break if anyone presses escape
    if event.getKeys('escape'): 
            break
        
win.setMouseVisible(True)
win.close()        
###########
io.quit()
###########


core.quit()