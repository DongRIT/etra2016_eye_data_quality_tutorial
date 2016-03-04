# -*- coding: utf-8 -*-
"""
Tue Mar 01 2016

@author: D WANG dxw1481@rit.edu
Based on the EDQ script by Sol Simpson and Raimondas Zemblys

convert hdf5 files into numpy array and txt files

"""
from __future__ import division
import numpy as np 
import h5py
import tables
import os
import pdb


# define hdf5file name and path
filepath = '/Users/dongwang/Dropbox/etra_tutorial/'
filename = 'mn_test.hdf5'

# input parameters that cannot be extracted from the simplified experiment
par_display_refresh_rate     = 60
par_eyetracker_model         = 'eyetribe'
par_dot_deg_sz               = 0.5
par_eyetracker_sampling_rate = 30
par_eyetracker_mode 		 = 'BINOCULAR'
par_fix_stim_center_size_pix = 2
par_operator 				 = 'dw'
par_et_model 			     = 'eyetribe'
par_display_width_pix 		 = 1920
par_display_height_pix 		 = 1200
par_exp_date 			     = '2016/3/1'
par_display_width_mm 		 = 530
par_dispay_height_mm		 = 330
par_eye_distance_mm 		 = 600

SAVE_TXT = 1
SAVE_NPY = 1

''' 
define the output data type of the the structrued numpy array
'''
wide_row_dtype = np.dtype([
    ('subject_id', np.uint16),
    ('display_refresh_rate', np.uint8),
    ('eyetracker_model', str, 32),
    ('dot_deg_sz', np.float32),
    ('eyetracker_sampling_rate', np.float32),
    ('eyetracker_mode', str, 16),
    ('fix_stim_center_size_pix', np.uint8),
    ('operator', str, 8),
    ('et_model', str, 16),
    ('display_width_pix', np.uint16),

    ('display_height_pix', np.uint16),
    ('exp_date', str, 16),
    ('screen_width', np.float32),
    ('screen_height', np.float32),
    ('eye_distance', np.float32),
    ('SESSION_ID', np.uint8),
    ('trial_id', np.uint16),
    ('TRIAL_START', np.float32),
    ('TRIAL_END', np.float32),
    ('posx', np.float32),

    ('posy', np.float32),
    ('dt', np.float32),
    ('ROW_INDEX', np.uint8),
    ('BLOCK', str, 6),
    ('session_id', np.uint8),
    ('device_time', np.float32),
    ('time', np.float32),
    ('left_gaze_x', np.float32),
    ('left_gaze_y', np.float32),
    ('left_pupil_measure1', np.float32),

    ('right_gaze_x', np.float32),
    ('right_gaze_y', np.float32),
    ('right_pupil_measure1', np.float32),
    ('status', np.uint8),
    ('target_angle_x', np.float32),
    ('target_angle_y', np.float32),
    ('left_angle_x', np.float32),
    ('left_angle_y', np.float32),
    ('right_angle_x', np.float32),
    ('right_angle_y', np.float32)
    ])


 
def save_as_txt(fname, data):
	'''
	save the structrued numpy array to a text file, 
	with dtype name as the column names.
	'''
	col_count = len(data.dtype.names)
	format_str = "{}\t" * col_count
	format_str = format_str[:-1] + "\n"
	
	header='#'+'\t'.join(data.dtype.names)+'\n'
	
	txtf = open(fname, 'w')
	txtf.write(header)
	for s in data.tolist():
	    txtf.write(format_str.format(*s))
	txtf.close()  



class VisualAngleCalc(object):
    def __init__(self, display_size_mm, display_res_pix, eye_distance_mm=None):
        """
        Used to store calibrated surface information and eye to screen distance
        so that pixel positions can be converted to visual degree positions.

        Note: The information for display_size_mm,display_res_pix, and default
        eye_distance_mm could all be read automatically when opening a ioDataStore
        file. This automation should be implemented in a future release.
        """
        self._display_width = display_size_mm[0]
        self._display_height = display_size_mm[1]
        self._display_x_resolution = display_res_pix[0]
        self._display_y_resolution = display_res_pix[1]
        self._eye_distance_mm = eye_distance_mm
        self.mmpp_x = self._display_width / self._display_x_resolution
        self.mmpp_y = self._display_height / self._display_y_resolution


    def pix2deg(self, pixel_x, pixel_y, eye_distance_mm):
        """
        Stimulus positions (pixel_x,pixel_y) are defined in x and y pixel units,
        with the origin (0,0) being at the **center** of the display, as to match
        the PsychoPy pix unit coord type.

        The pix2deg method is vectorized, meaning that is will perform the
        pixel to angle calculations on all elements of the provided pixel
        position numpy arrays in one numpy call.

        The conversion process can use either a fixed eye to calibration
        plane distance, or a numpy array of eye distances passed as
        eye_distance_mm. In this case the eye distance array must be the same
        length as pixel_x, pixel_y arrays.
        """
        eye_dist_mm = self._eye_distance_mm
        # if eye_distance_mm is not None:
        #     eye_dist_mm = eye_distance_mm
 
        x_mm = self.mmpp_x * pixel_x
        y_mm = self.mmpp_y * pixel_y

        Ah = np.arctan(x_mm, np.hypot(eye_dist_mm, y_mm))
        Av = np.arctan(y_mm, np.hypot(eye_dist_mm, x_mm))

        return np.rad2deg(Ah), np.rad2deg(Av)





def whichtargetsamplebelongs2(target, array):
	'''
	find which target each data sample belongs to
	'''
	idx = np.searchsorted(array,target,side = 'right')
	return idx

	


#################################################################################################

if __name__ == '__main__':

	
	'''
	read in hdf5 files. sample_dataset stores the eye samples. 
	target_dataset stores the target information
	'''
	f = h5py.File(os.path.join(filepath, filename),'r')
	sample_dataset = f['/data_collection/events/eyetracker/BinocularEyeSampleEvent/']
	target_dataset = f['/data_collection/condition_variables/EXP_CV_1/']



	'''
	read target info into numpy arrays
	'''
	TRIAL_START = target_dataset['TRIAL_START']
	TRIAL_END   = target_dataset['TRIAL_END']
	trial_id    = target_dataset['trial_id'] 
	ROW_INDEX   = target_dataset['ROW_INDEX']
	posx 		= target_dataset['posx']
	posy		= target_dataset['posy']
	dt 			= target_dataset['dt']


	pix2deg = VisualAngleCalc([par_display_width_mm, par_display_width_mm], 
								[par_display_width_pix,par_display_height_pix],
                                      par_eye_distance_mm).pix2deg

	pos_angle = pix2deg(posx, posy, par_eye_distance_mm)

	

	
	output = np.empty((len(sample_dataset),), dtype = wide_row_dtype)	

	output['subject_id'] 				 = sample_dataset['experiment_id']
	output['display_refresh_rate']       = par_display_refresh_rate
	output['eyetracker_mode'] 			 = par_eyetracker_model
	output['dot_deg_sz'] 				 = par_dot_deg_sz
	output['eyetracker_sampling_rate']   = par_eyetracker_sampling_rate	
	output['eyetracker_mode']			 = par_eyetracker_mode 		
	output['fix_stim_center_size_pix']   = par_fix_stim_center_size_pix
	output['operator'] 					 = par_operator 				
	output['et_model']                   = par_et_model 			    
	output['display_width_pix'] 		 = par_display_width_pix 	    
	output['display_height_pix'] 		 = par_display_height_pix      		
	output['exp_date'] 					 = par_exp_date 			      
	output['screen_width'] 				 = par_display_width_mm 		     	
	output['screen_height'] 		 	 = par_dispay_height_mm		    	
	output['eye_distance'] 				 = par_eye_distance_mm             
	output['SESSION_ID'] 				 = sample_dataset['session_id']     
	output['BLOCK'] 					 = 'FS'
	output['session_id'] 				 = sample_dataset['session_id'] 
	output['device_time'] 				 = sample_dataset['device_time']
	output['time'] 						 = sample_dataset['logged_time']
	output['left_gaze_x'] 				 = sample_dataset['left_gaze_x']
	output['left_gaze_y'] 				 = sample_dataset['left_gaze_y']
	output['left_pupil_measure1'] 		 = sample_dataset['left_pupil_measure1']
	output['right_gaze_x'] 				 = sample_dataset['right_gaze_x']
	output['right_gaze_y'] 				 = sample_dataset['right_gaze_y']
	output['right_pupil_measure1'] 		 = sample_dataset['right_pupil_measure1']
	output['status'] 					 = sample_dataset['status']
	output['left_angle_x']				 = pix2deg(sample_dataset['left_gaze_x'], sample_dataset['left_gaze_y'],par_eye_distance_mm)[0]
	output['left_angle_y']				 = pix2deg(sample_dataset['left_gaze_x'], sample_dataset['left_gaze_y'],par_eye_distance_mm)[1]
	output['right_angle_x']				 = pix2deg(sample_dataset['right_gaze_x'], sample_dataset['right_gaze_y'],par_eye_distance_mm)[0]
	output['right_angle_y']				 = pix2deg(sample_dataset['right_gaze_x'], sample_dataset['right_gaze_y'],par_eye_distance_mm)[1]



	for i in range (0, len(sample_dataset)):
		
		IDX = whichtargetsamplebelongs2(output['time'][i], TRIAL_START)-1
		output['trial_id'][i]           = trial_id[IDX]
		output['TRIAL_START'][i]  		= TRIAL_START[IDX] 
		output['TRIAL_END'][i]  		= TRIAL_END[IDX]
		output['posx'][i]  				= posx[IDX]
		output['posy'][i]  				= posy[IDX]
		output['dt'][i]  				= dt[IDX]
		output['ROW_INDEX'][i]  		= ROW_INDEX[IDX]
		output['target_angle_x'][i]     = pos_angle[0][IDX]
		output['target_angle_y'][i]		= pos_angle[1][IDX]

	



	if SAVE_TXT:
		txt_file_name = r"%s.txt" % (filename[:-5])  
		save_as_txt(txt_file_name, output)

	if SAVE_NPY:
		np_file_name = r"%s.npy" % (filename[:-5]) 
		np.save(np_file_name, output)
    	
 


	
