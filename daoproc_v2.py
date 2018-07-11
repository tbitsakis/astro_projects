#!/usr/bin/env python

'''
call: daoproc_v2

purpose: This script is using IRAF packages in Pyraf to perform aperture 
          protometry in astronomical *.fits images. 

inputs: image.fits, telescope/CCD parameters (gain,read-out-noise)
        FWHM of the source.

outputs: it first generates a PSF image using a statistically 
        significant sample of stars. It then creates files containing
        the detections/photometry.

Version: v2 - G. Maravelias, T. Bitsakis
'''


import os, sys, shutil, math, time
from pyraf import iraf
from iraf import noao, digiphot, daophot

# ==================================================
#               PARAMETERS TO BE SET:
# ==================================================

# not known exactly ... 
gain =  6.61         # Individual gain in e/ADU
rdnoise = 0.76       # Read noise in e/px (/read)

Nimages = 1          # Number of images used
N_loops = 4          # Number of loops to execute

# fwhm = 2.50          # FWHM of a star in the image
fwhm = input('Enter FWHM: ')
maxpsfstars = 150    # Number of stars in psf model

sigmabgr = 3.       # Background sigma
datamin = 1.         # Min(sky)-5*sigmabgr
datamax = 28000.     # Maxdata
threshold = 2.       # Detection threshold 

# ==================================================

ans = raw_input('Remove previous files (y/n): ')

if ans == 'y':
        os.system('rm *sub.*')
        os.system('rm *pst.*')
        os.system('rm *final.*')
        os.system('rm *grf.*')
        # os.system('rm *psf.*')
        # os.system('rm *image_of_psf.*')

# ==================================================

# FUNCTION
def transform(infile,outfile):
        alsnm = infile
        coonm = outfile
        #print alsnm, coonm

        c = open(coonm,'w')
        a = open(alsnm,'r')
        lns = a.readlines()
        a.close
        
        for i in range(44,len(lns),2):
                line0 = lns[i].split()
                star_id = line0[0]
                xpos = line0[1]
                ypos = line0[2]
                mag = line0[3]
                line1 = lns[i+1].split()
                sharp = line1[0]
                
#               print '...parsing: '+xpos+' '+ypos+' (star '+star_id+')'
                c.write(xpos+'   '+ypos+'   '+star_id+'\n')
        c.close

        print "\nTrasnformation completed!"



# INPUT FILE
if len(sys.argv)!=2:
        sys.exit('ERROR: please provide a file') 
flnm, flext = os.path.splitext(sys.argv[1])     


# setting parameters
iraf.daofind.unlearn
iraf.phot.unlearn
iraf.allstar.unlearn

iraf.datapars.unlearn
iraf.daopars.unlearn
iraf.findpars.unlearn
iraf.centerpars.unlearn
iraf.fitskypars.unlearn

# EDIT PARAMETERS HERE >>>
iraf.datapars.setParam('fwhmpsf',fwhm)  
iraf.datapars.setParam('sigma',sigmabgr)   
iraf.datapars.setParam('datamin',datamin)         
iraf.datapars.setParam('datamax',datamax)

# this is not probably correct ... 
iraf.datapars.setParam('readnoise',math.sqrt(Nimages)*rdnoise)  
iraf.datapars.setParam('epadu',gain*Nimages)

iraf.datapars.setParam('itime','270')       # 4 to 5 min                    

iraf.findpars.setParam('threshold',threshold)     # detection threshold in sigma above background

iraf.centerpars.setParam('calgori','none')
iraf.centerpars.setParam('cbox',2*fwhm)		
iraf.fitskypars.setParam('salgori','mode')	
iraf.fitskypars.setParam('annulus',4*fwhm)		
iraf.fitskypars.setParam('dannulu',4*fwhm)	
iraf.photpars.setParam('apertur',1*fwhm)		

iraf.daopars.setParam('function','auto')	
iraf.daopars.setParam('varorder','2')
iraf.daopars.setParam('psfrad',4*fwhm+1)			
iraf.daopars.setParam('fitrad',1*fwhm)			
iraf.daopars.setParam('sannulus',4*fwhm)		
iraf.daopars.setParam('wsannulus',4*fwhm)	

times_start = time.ctime()
times_start_float = time.time() 
times = {}

if os.path.exists(flnm+'.sub.0'+flext):
        pass
else:
        shutil.copy(flnm+flext,flnm+'.sub.0'+flext)     # formatting reasons only

for i in range(N_loops):
#for i in range(2):
        initimg = flnm+'.sub.0.fits'
        runnm = flnm+'.sub.'+str(i)
        print "\n>>> Working on",runnm+'.fits',"<<<\n"  

        print "========================================="
        print "...running daofind for", runnm+".fits"
        print "========================================="
        tds = time.time()
        if os.path.exists(runnm+'.coo'):
                print "   File found! skipping this step"
                pass
        else:
                iraf.daofind(image=runnm+'.fits',output=runnm+'.coo', verify='no')
        tde = time.time()
        times[runnm+'_daofind']=tde-tds

        print "========================================="
        print "...running phot for", runnm+".coo"
        print "========================================="
        tps = time.time()
        if os.path.exists(runnm+'.mag'):
                print "   File found! skipping this step"
                pass
        else:
                iraf.phot(image=runnm+'.fits',coords=runnm+'.coo',output=runnm+'.mag', verify='no')     # on subtracted image
        tpe = time.time()
        times[runnm+'_phot']=tpe-tps

        
        # check for psf.fits image and prompt to create if does not exist - only for sub.0
        if not os.path.exists(flnm+'.psf.fits'):
                print " "
                print "========================================="
                print "...creating psf" 
                print "========================================="
                print " 1. Select stars to keep by pressing 'a' or 'd' to delete them."
                print " 2. After the selection is finished, select the ds9 window and press 'w' to force the use of these stars for psf creation."
                print " 3. To quit press 'q' at the ds9 window and again 'q' at the terminal. The program will go on automatically without any human interaction."
                print "  (Hint: you can safely leave office for a beer or coffee.)"                                     
                raw_input('Ready ? ("enter" to continue)')
                                
                iraf.pstselect(image=flnm+'.sub.0.fits',photfile=runnm+".mag",pstfile=flnm+".pst.1",maxnpsf=maxpsfstars,verify="no")
                pstregfl = open(flnm+".pst.1.reg",'w')
                pstregfl.write('global color=green dashlist=8 3 width=1 font="helvetica 10 normal roman" select=1 highlite=1 dash=0 fixed=0 edit=1 move=0 delete=1 include=1 source=1\nphysical\n')

                pstfl = open(flnm+".pst.1",'r')
                pstlns = pstfl.readlines()
                pstfl.close()
                for s in range(65,len(pstlns),1):
                        prts = pstlns[s].split()
                        star_id = prts[0]
                        xpos = prts[1]
                        ypos = prts[2]
                        #print star_id, xpos, ypos
                        pstregfl.write('point('+str(xpos)+','+str(ypos)+') # point=cross text={'+star_id+'}\n')

                pstregfl.close()
		os.system("/usr/local/bin//ds9 "+flnm+'.sub.0.fits'+" -regions "+flnm+".pst.1.reg"+" &")
                tfs = time.time()
                iraf.psf(image=flnm+'.sub.0.fits',photfile=flnm+'.sub.0.mag',pstfile=flnm+'.pst.1',psfimage=flnm+'.psf.fits',
                        opstfile=flnm+'.pst.2',groupfile=flnm+'.grf.psg',interactive="no",showplots="no",verify="no")
                tfe = time.time()
                times[runnm+'_psf']=tfe-tfs
                iraf.seepsf(psfimage=flnm+'.psf.fits', image=flnm+'.image_of_psf.fits')


        if i==0:
                shutil.copy(runnm+'.mag',runnm+'.tot.mag')      # formatting reasons only
        else:
                print "========================================="
                print "...merging phot lists"
                print "========================================="
                iraf.pfmerge(inphotfi=str(flnm+'.sub.'+str(i-1)+'.als'+','+runnm+'.mag'),outphotf=runnm+'.tot.mag')
                iraf.prenumber(runnm+'.tot.mag')


        print "========================================="
        print "...running allstar for", runnm+'.fits'
        print "========================================="
        iraf.daopars.setParam('recenter','yes') 
        tas = time.time()
        iraf.allstar(image=initimg,photfile=runnm+'.tot.mag',psfimage=flnm+'.psf.fits',allstarf=runnm+'.als',rejfile=runnm+'.arj',subimage=flnm+'.sub.'+str(i+1)+'.fits',cache='no',verify='no')        # ALLSTAR on original sub.0
        tae = time.time()
        times[runnm+'_allstar']=tae-tas

        # removing the merged phot file (not needed for analysis)
        os.remove(runnm+'.tot.mag')

        print "\n>>> END OF DAOLOOP #"+str(i)


# Creating the total list of positions for all stars (after running allstar) for input in other routines (e.g. Ha photometry) 
transform(str(runnm)+".als",str(flnm)+".final.list.coo")

# Printing parameters to check
print "\n\nChecking the persistence of parameters:"
print "fwhm:", iraf.datapars.getParam('fwhmpsf')
print "sigma", iraf.datapars.getParam('sigma')  
print "datamin:", iraf.datapars.getParam("datamin")
print "datamax:", iraf.datapars.getParam("datamax")
print "effective gain:", iraf.datapars.getParam('epadu')
print "effective readnoise", iraf.datapars.getParam('readnoise')
print "exposure time:", iraf.datapars.getParam("itime")
print "cbox dimension:", iraf.centerpars.getParam('cbox')
print "psfrad:", iraf.daopars.getParam("psfrad")
print "fitrad:", iraf.daopars.getParam("fitrad")
print "detection threshold:", iraf.findpars.getParam("threshold")
print "phot sky annulus:", iraf.fitskypars.getParam("annulus")
print "psf sky annulus:", iraf.daopars.getParam("sannulus")
print "phot aperture:", iraf.photpars.getParam('apertur')


print "\nTimings, starting on", times_start
for k in sorted(times.iterkeys()):
        print k, ':', "{0:.2f}".format(times[k]), 's'
print "...finishing on", time.ctime(), "-- running for:", "{0:.3f}".format((time.time()-times_start_float)/3600.),"h"

# Removing extra files no needed
for i in range(N_loops-1):
        os.system('rm *sub.'+str(i)+'.*')

print "\nThe DaoProcess has been executed!"

