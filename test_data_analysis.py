# -*- coding: utf-8 -*-

import re
import matplotlib.pyplot as plt
import numpy as np


with open("dist_test_computer.txt") as file:
    comp_txt = file.readlines()
    
with open("dist_test_human_NoFeedback.txt") as file:
    human_nfb_txt = file.readlines()
    
with open("dist_test_human_Feedback.txt") as file:
    human_fb_txt = file.readlines()
    


comp_dist = re.findall(r'Dist: (\d+)', str(comp_txt))
hum_nfb_dist = re.findall(r'Dist: (\d+)', str(human_nfb_txt))
hum_fb_dist = re.findall(r'Dist: (\d+)', str(human_fb_txt))


comp_z = re.findall(r'Z: (\d+)', str(comp_txt))
hum_nfb_z = re.findall(r'Z: (\d+)', str(human_nfb_txt))
hum_fb_z = re.findall(r'Z: (\d+)', str(human_fb_txt))


plt.plot(comp_z, comp_dist, label = 'computer')
plt.plot(hum_nfb_z, hum_nfb_dist, label = 'human nfb')
plt.plot(hum_fb_z, hum_fb_dist, label = 'human fb')

plt.legend()
plt.xlabel('Z')
plt.ylabel('Optical Distance')

comp_z_dist = np.array([comp_z, comp_dist])
hum_nfb_z_dist = np.array([hum_nfb_z, hum_nfb_dist])
hum_fb_z_dist = np.array([hum_fb_z, hum_fb_dist])

a = np.unique(comp_z_dist, axis=1)
b = np.unique(hum_nfb_z_dist, axis=1)
c = np.unique(hum_fb_z_dist, axis=1)
d,d_idx = np.unique(c[0,...], return_index=True)
d = [[d],[c[1,d_idx]]]
d = np.array(d)
d = np.squeeze(d)


fig2 = plt.figure()
plt.plot(a[0,...],a[1,...])
plt.plot(b[0,...],b[1,...])
plt.plot(d[0,...],d[1,...])

plt.legend(['Computer', 'Human NFB', 'Human FB'])
