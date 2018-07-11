#! /usr/bin/python

'''
 = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
 PURPOSE:
 	The code creates artificial clusters from the theoretical isochrones of Bruzual&Charlot and 
 	then estimates their luminosity functions.
 
 INPUTS:
 	Provide the isochrone file and the path to that directory. Also the Schechter function 
 	parameters.

 OUTPUTS:
 	The luminosity function of the cluster and and the corresponding Schechter function

 DEPENDENCIES:
   Numpy, Astropy, pip install CosmoloPy

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
# =================================================================================================

# Schechter Parameters ============================================================================
phiStar = 0.001
MStar = -22.
alpha = -1.3
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

# ############################### Create random catalog of N-stars ################################
Ncumul = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

for j in range(0,100):

	indexList = random.sample(dataIndex,numberStars) # Randomly choses numberStars elements from the dataIndex array

	B2_artStar = np.take(B2_Total,indexList) # Choses the B2 with corresponding index
	Col_artStar = np.take(ColmagTotal,indexList) # Choses the Colour with corresponding index

	B2_artStar_ABS = B2_Total-5.0*log(DistModulus*100) # Make absolute mag at distance modulus

	binlist = [-26,-23,-21,-20,-19,-18.5,-18,-17.5,-17,-16.5,-16] # varying bins
	lumHist = np.histogram(B2_artStar_ABS,bins=15)

	for i in range(0,len(lumHist[0])):
		Ncumul += lumHist[0]

Ncumul = Ncumul*1./max(Ncumul) # cumulative distribution of 100 repeatetions

# # ############################## Bin and create Luminosity Function ################################

# Make it to loop many times and sum the results
# save the result to eps
# fit some distribution or overplot the schechter functions etc


histBin = lumHist[1]
y = np.log10(Ncumul)
x = []

for i in range(len(histBin)-1):
	x.append((histBin[i+1]+histBin[i])*0.5)

# ################################# Schechter Luminosity Function ##################################

x_s = np.arange(-25,-15.9,0.1)

y_s = LumF.schechterM(x_s, phiStar, alpha, MStar)

y_s = np.log10(y_s*1./max(y_s))

# ######################################## Saving Results ###########################################
if IsochroneFile_B2 == 1:
	filt = 'U'
elif IsochroneFile_B2 == 2:
	filt = 'B'
elif IsochroneFile_B2 == 3:
	filt = 'V'
elif IsochroneFile_B2 == 4:
	filt = 'I'

print 'Saving Results!'
save_file =  'LFs/'+IsochroneFile+'_'+filt+'_'+str(numberStars)+'_LF.cat' 
file = open(save_file,'w')
file.write('# Bin_med         logN\n')
for i1, i2 in zip(x,y):
	file.write('{}  {}\n'.format(i1,i2))


# ################################ Plotting the Luminosity Function ################################
print 'Plotting!'
plt.plot(x,y,label="Data")
plt.plot(x_s,y_s,label="Schechter function")
plt.xlim(-16,-26)
plt.ylim(-2.2,0.3)
# plt.yscale('log', nonposy='clip')
plt.xlabel('M$_{abs}$ [mag]',fontsize=16)
plt.ylabel(r'$log_{10}$ N/N$_{max}$',fontsize=16)
plt.legend()
name_eps = 'LFs/'+IsochroneFile+'_'+filt+'_'+str(numberStars)+'_LF.eps'
plt.savefig(name_eps,format='eps')
# plt.show()















print '================================== END ========================================'
print("--- %s seconds ---" % (time.time() - start_time))
print ' '
