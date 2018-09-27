#!/usr/bin/env python
"""
 = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
 PURPOSE:
   This code is performing completeness tests by adding random stars in the images of clusters, 
   then performs photometry using daophot, and finally compares the catalogs and outputs the 
   completeness per magnitude and iteration.
 
 INPUTS:
   A list with the clusters for consideration, input parameters such as the magnitude range, 
   number of stars and iterations, and the photometry.

 OUTPUTS:
   A file containing the completeness parameters, per cluster, magnitude and iteration.

 DEPENDENCIES:
   Astropy, pyraf (to use this script bash > source activate iraf27)

 HISTORY:
   Created by:  Theodoros Bitsakis (Instituto de Radioastronomia y Astrofisica/UNAM, Mexico)

 MODIFICATIONS:
 = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
 """

# Importing Libraries ===================================================================================
import os, sys, shutil, math, time
import numpy as np 
from pyraf import iraf
from iraf import noao, digiphot, daophot, addstar

print("WARNING: To use this script bash > source activate iraf27\n")
start_time = time.time()

# Defining the necessary functions ===========================================================================
def addstar_function(in_image_name,in_image_psf,out_image_name,min_mag_range,max_mag_range,nstar,fwhm):
	'''
	This function is using the NOAO/DIGIPHOT/DAOPHOT/ADDSTAR
	module in IRAF to add a number of stars of some mangitude
	at random positions all over the fits image.
	'''
	iraf.addstar.unlearn # set default params
	iraf.daopars.setParam('psfrad',4*fwhm+1)					

	iraf.addstar(image=in_image_name,photfile='',psfimage=in_image_psf,addimage=out_image_name,
					minmag=min_mag_range,maxmag=max_mag_range,nstar=nstar,verify='no',verbose='no')	


def daoproc(cluster,out_image_name,fwhm):
	'''
	This function is executing the daophot process to perform
	aperture photometry at each image produced by addsstar.
	'''
	# setting parameters
	gain =  6.61         # Individual gain in e/ADU
	rdnoise = 0.76       # Read noise in e/px (/read)
	Nimages = 1          # Number of images used
	# N_loops = 4          # Number of loops to execute
	# fwhm = 2.50          # FWHM of a star in the image
	# maxpsfstars = 150    # Number of stars in psf model
	sigmabgr = 3.        # Background sigma
	datamin = 1.         # Min(sky)-5*sigmabgr
	datamax = 28000.     # Maxdata
	threshold = 2.       # Detection threshold 

	iraf.daofind.unlearn
	iraf.phot.unlearn
	iraf.allstar.unlearn
	iraf.datapars.unlearn
	iraf.daopars.unlearn
	iraf.findpars.unlearn
	iraf.centerpars.unlearn
	iraf.fitskypars.unlearn

	iraf.datapars.setParam('fwhmpsf',fwhm)  
	iraf.datapars.setParam('sigma',sigmabgr)   
	iraf.datapars.setParam('datamin',datamin)         
	iraf.datapars.setParam('datamax',datamax)
	iraf.datapars.setParam('readnoise',math.sqrt(Nimages)*rdnoise)  
	iraf.datapars.setParam('epadu',gain*Nimages)
	iraf.datapars.setParam('itime','270')       # 4 to 5 min                    
	iraf.daopars.setParam('function','auto')	
	iraf.daopars.setParam('varorder','2')
	iraf.daopars.setParam('psfrad',4*fwhm+1)			
	iraf.daopars.setParam('fitrad',1*fwhm)			
	iraf.daopars.setParam('sannulus',4*fwhm)		
	iraf.daopars.setParam('wsannulus',4*fwhm)	
	iraf.daopars.setParam('recenter','yes')
	iraf.photpars.setParam('apertur',1*fwhm)		
	iraf.findpars.setParam('threshold',threshold)    
	iraf.centerpars.setParam('calgori','none')
	iraf.centerpars.setParam('cbox',2*fwhm)		
	iraf.fitskypars.setParam('salgori','mode')	
	iraf.fitskypars.setParam('annulus',4*fwhm)		
	iraf.fitskypars.setParam('dannulu',4*fwhm)	

	# Running DAOPHOT
	out_image_namein = out_image_name + '[0]'
	iraf.daofind(image=out_image_namein,output=out_image_name + '.coo', verify='no')
	iraf.phot(image=out_image_namein,coords=out_image_name + '.coo',output=out_image_name +'.mag', verify='no')
	iraf.allstar(image=out_image_name,photfile=out_image_name+'.mag',psfimage=cluster+'_b_wcs.psf.fits',
					allstarf=out_image_name+'.als',rejfile=out_image_name+'.arj',subimage=out_image_name+'.sub.fits',
					cache='no',verify='no')    

    # Removing unecessary files
	os.system('rm -rf outputs/*sub.*')
	os.system('rm -rf outputs/*coo')
	os.system('rm -rf outputs/*.mag')    
	os.system('rm -rf outputs/*.arj')    
	os.system('rm -rf outputs/*pst.*')
	os.system('rm -rf outputs/*final.*')
	os.system('rm -rf outputs/*grf.*')
	os.system('rm -rf outputs/*.fits')


def check_compl(out_image_name):
	'''
	This function reads the output files of the addstar (containing all the artificial stars)
	and the daoproc (containing all the stars from the photometry) and checks the completeness
	'''
	art_ra, art_dec, art_mag = np.loadtxt(out_image_name+'.art', comments='#', unpack=True,usecols=(1,2,3))
	art_ra = np.around(art_ra,1)
	art_dec = np.around(art_dec,1)


	als = open(out_image_name+'.als','r')
	als_ra = []
	als_dec = []
	als_mag = []
	lines = als.read().split('\n')
	for line in lines[44::2]: # skip the comments and read every two lines (see format)
		if len(line.split()) == 8:
			als_ra.append(round(float(line.split()[1]),1))
			als_dec.append(round(float(line.split()[2]),1))
			als_mag.append(round(float(line.split()[3]),1))

	als.close()

	# os.system('rm -rf outputs/*.als')
	# os.system('rm -rf outputs/*.art')

	# Matching the arrays
	# matches = np.isin(zip(art_ra,art_dec),zip(als_ra,als_dec))
	matches = 0
	for i1 in range(len(art_ra)):
		for i2 in range(len(als_ra)):
			if (art_ra[i1] == als_ra[i2]) and (art_dec[i1] == als_dec[i2]):
				matches += 1
	return matches


# Running the code ===========================================================================================
input_list = open("cluster_list.dat","r")
clusters = input_list.read().split("\n")
mag_range = np.arange(24.,19.,-0.5)

for cluster in clusters:

	file_compl = open('outputs/' + cluster + '_compl.dat','w')
	file_compl.write('# Cluster  mag  iter  compl  nstar\n')
	for mag in mag_range:
		for i in range(5):

			in_image_name = cluster + '_b.fits'
			in_image_psf = cluster + '_b_wcs.psf.fits'
			out_image_name = 'outputs/' + cluster + '_' + str(i+1) + '_' + str(mag) + '_out.fits'
			min_mag_range = mag
			max_mag_range = mag
			nstar = 10
			fwhm = 2.3

			addstar_function(in_image_name,in_image_psf,out_image_name,min_mag_range,max_mag_range,nstar,fwhm)
			daoproc(cluster,out_image_name,fwhm)

			matching = check_compl(out_image_name)
			file_compl.write('{} {} {} {} {}\n'.format(cluster,mag,i,matching,nstar))

			print('>>>>>>>>>>>>>>>>> ' + cluster + ' mag=' + str(mag) + ' loop=' + str(i+1) + ' <<<<<<<<<<<<<<<<<<<<<')
	file_compl.close()

print("\n")
print("-------------- Time elapsed: %s minutes ------------------" % (round((time.time() - start_time)/60.,2)))

input_list.close()
	










