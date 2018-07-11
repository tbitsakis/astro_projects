#! /usr/bin/python

'''
 = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
 PURPOSE:
 	The code creates artificial clusters from the theoretical isochrones of Bruzual&Charlot and 
 	then saves a table that will be used as an input for DAOPHOT>addstar to create an artificial
 	image of a cluster.
 
 INPUTS:
 	Provide the isochrone file and the path to that directory. Also the bands and the number of 
 	stars.

 OUTPUTS:
 	A table containing coordinates and magnitudes

 DEPENDENCIES:
   Numpy

 HISTORY:
   Created by: Theodoros Bitsakis (Instituto de Radioastronomia y Astrofisica/UNAM, Mexico)

 MODIFICATIONS:
	None
 = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
'''
import numpy as np
import sys, operator, time, glob
from math import pi, log, e
import random
import matplotlib.pyplot as plt
import cosmolopy.luminosityfunction as LumF

# #################################################################################################
# ################################### EDIT BELOW THIS POINT #######################################
# #################################################################################################

# ISOCHRONE FILE ==================================================================================
print '                                                                                '
IsochronesPath = "/Users/TB/Documents/Astro_Work/Studying_StarClusters/Data/LMC/Analysis/8_Fit_CMDs/all_isochrones/my_isoc_random_5k/"
IsochroneFile_B1 = input('Isochrone, 1-band (1:U, 2:B, 3:V, 4:I): ') # column that corresponds to 1-band 
IsochroneFile_B2 = input('Isochrone, 1-band (1:U, 2:B, 3:V, 4:I): ') # column that corresponds to 2-band 
DistModulus = 18.5           # Distance Modulus of our galaxy 
IsochroneFile = raw_input('Please provide the desirable isochrone file: ')
numberStars = input('Please provide the number of stars in the artificial cluster: ')
imageSize = [200,200]
# =================================================================================================

print '                                                                                '
print '================================= Running ======================================'

# #################################################################################################
# ################################ DO NOT EDIT BELOW THIS POINT ###################################
# #################################################################################################
start_time = time.time()

# ##################### Retrieve all theoretical values from isochrones files #####################
isochrones_list = sorted(glob.glob(IsochronesPath))

B1_Total = []
B2_Total = []
ColmagTotal = []
dataIndex = []

IsochroneFile_path = IsochronesPath+IsochroneFile

B1, B2 = np.loadtxt(IsochroneFile_path, comments='#', unpack=True,
       usecols=(IsochroneFile_B1,IsochroneFile_B2))
B1_Total = B1+DistModulus # Adding distance modulus to modify generic isochrone mags to desirable redshift
B2_Total = B2+DistModulus # Adding distance modulus to modify generic isochrone mags to desirable redshift
ColmagTotal.extend(B1-B2) # ISOCHRONE COLOUR - no need to add distance modulus

for i in range(len(B1_Total)):
	dataIndex.append(i)

# # ############################### Create random catalog of N-stars ################################

indexList = random.sample(dataIndex,numberStars) # Randomly choses numberStars elements from the dataIndex array
B2_artStar = np.take(B2_Total,indexList) # Choses the B2 with corresponding index
Col_artStar = np.take(ColmagTotal,indexList) # Choses the Colour with corresponding index

mu = [imageSize[0]/2.,imageSize[1]/2.] # mean value of the two axis of image
sigma = imageSize[0]/8. # sigma value (the smallest axis fraction)

PosX=[]
PosY=[]
for i in range(numberStars):
	PosX.append(random.gauss(mu[0],sigma)) # gaussian random for x
	PosY.append(random.gauss(mu[1],sigma)) # gaussian random for y

# ######################################## Saving Results ###########################################
if IsochroneFile_B1 == 1 and IsochroneFile_B2 == 2:
	filt = 'UB'
elif IsochroneFile_B1 == 1 and IsochroneFile_B2 == 3:
	filt = 'UV'
elif IsochroneFile_B1 == 2 and IsochroneFile_B2 == 3:
	filt = 'BV'
elif IsochroneFile_B1 == 3 and IsochroneFile_B2 == 4:
	filt = 'VI'
else:
	filt = 'NaN'

print 'Saving Results!'
save_file =  'Artificial_Clusters/'+IsochroneFile+'_'+filt+'_'+str(numberStars)+'_clust.cat' 
file = open(save_file,'w')
file.write('# x_pixel         y_pixel       Mag        '+filt+'\n')
for i1, i2, i3, i4 in zip(PosX,PosY,B2_artStar,Col_artStar):
	file.write('{}  {}  {}  {}\n'.format(i1,i2,i3,i4))


# ################################# Plotting the Luminosity Function ################################
print 'Plotting!'
plt.figure(1)
area = (22.-B2_artStar)*5
plt.scatter(PosX,PosY,s=area)
# plt.plot(x_s,y_s,label="Schechter function")
plt.xlim(0,imageSize[0])
plt.ylim(0,imageSize[1])
# # plt.yscale('log', nonposy='clip')
plt.xlabel('x [pixel]',fontsize=16)
plt.ylabel('y [pixel]',fontsize=16)
# plt.legend()
name_eps = 'Artificial_Clusters/'+IsochroneFile+'_'+filt+'_'+str(numberStars)+'_clust.eps'
plt.savefig(name_eps,format='eps')

# Plotting the CMD
plt.figure(2)
plt.scatter(Col_artStar,B2_artStar)
plt.xlabel(filt,fontsize=16)
plt.ylabel('m [mag]',fontsize=16)
plt.ylim(22,13)
plt.show()











print '================================== END ========================================'
print("--- %s seconds ---" % (time.time() - start_time))
print ' '
