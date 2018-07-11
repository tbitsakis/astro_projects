#!/usr/bin/env python
"""
skirt.py - SKinakas IR Reduction Tool 

Description /
 A PyRAF script to reduce IR observations from Skinakas. 
 From raw images the script performs dark subtraction, flat-fielding to all object images. Then the sky is subtracted by taking the difference of all available images (creating the *_df.fit images) and with the IRAF's imexamine command the user selects the star to use for alignment of the images. After the alignment all shifted images (the _*sh.fit images) are combined in a single final image (*_comb.fit). 

Usage / 
 Copy all raw data in a directory, using one directory for each object (the script add keys in the headers).
 All images must be named accordingly: Dark_* for darks, Flat_* for flats, Objectname1_objectname2_filter_obsnumber.fit for objects.
 Open ds9 in the background.
 Copy script inside the directory and make it executable: chmod +x skirt.py
 Run the script: ./skirt.py
 Select if you want to remove the intermediate steps (*df.fit, *sh.fit, iraf lists).

TODO/ 
 dither or on-off ? check option and sky subtraction accordingly
 open ds9 automatically!! 
 remove intermediate steps at the beginning also
 divide by total number for counts/s? (for photometry?)
 checking if names correct...if list index out of range (at rname) print an error
 *combine parameters ?
 make a serious log
 flat images: random light images, option to select randomly from data
 acquairing image dimensions? or setting outside?
 group or not unlearn? unlearn(iraf.ccdhedit, ...)
 better cleaning procedure at the end (from what it is now...)
 imexamine loads automatically? no packages needed for this
 imcalc needs import only for stsdas (/toolbox/imgtools/ not needed?)
"""

# Importing necessary stuff
import glob,os
from pyraf import iraf
from iraf import unlearn
from iraf import noao,imred,ccdred # packages needed for image redution 
from iraf import stsdas # packages needed of imcalc 
import datetime

# log keeping
#scrilog = 't.log'
#if os.path.isfile(scrilog):
#	os.remove(scrilog)
#l = open(scrilog,'w')
#print datetime(now)
#l.write("testing...\n")
#l.close()

# welcome message
print "\n\t\t Welcome to SKIRT! \n"
#l.write('\nWelcome! \n')

# checking of correct names and selecting root name:
drk = []
flt = []
obj = []
data = []
for img in glob.glob('*.fit'):
	imgnm = img.split('_')
	if imgnm[0]=='Dark':
		drk.append(img)
	elif imgnm[0]=='Flat':
		flt.append(img)
	else:
		data.append(img)
		rname = imgnm[0]+"_"+imgnm[1]+"_"+imgnm[2]
		obj.append(rname)
# error checking
if len(drk)==0:
	print "ERROR: hmmm, you forgot to supply the DARK frames..."
	print "Please include them before running the script again. Bye!\n"
	raise SystemExit
elif len(flt)==0:
	print "ERROR: hmmm, you forgot to supply the FLAT frames..."
	print "Please include them before running the script again. Bye!\n"
	raise SystemExit
elif len(drk)==0 and len(flt)==0:
	print "ERROR: well, you forgot to supply DARK and FLAT frames..."
	print "Please include them before running the script again. Bye!\n"
	raise SystemExit
elif len(obj)==0:
	print "ERROR: well, what can we do without any OBJECT image ?"
	print "Please include them before running the script again. Bye!\n"
	raise SystemExit
elif len(drk)==0 and len(flt)==0 and len(obj)==0:
	print "ERROR: loool! No data no results!"
	print "Please include SOMETHING before running the script again. Bye!\n"
	raise SystemExit
elif len(set(obj))!=1:
	print "ERROR: too many objects! Include one only. Bye!\n"
else:
	print "So using", len(drk), "dark,",len(flt),"flat and",len(obj),"objects images, with object's rootname:",rname

getout = raw_input("Is everything ok? Press 'enter' to continue, 'e' to exit.\t")
# option to exit
if getout=='e' or getout=='E':
	print "\nexiting then... Bye!\n"
	raise SystemExit 

# preparing header fields (input of imagetyp, exptime/darktime) 
print "> preparing the image headers" 
#l.write("\n> preparing the image headers")
unlearn(iraf.ccdhedit)
iraf.ccdhedit("Dark*.fit",  parameter="imagetyp", value="dark")
iraf.ccdhedit("Flat*.fit",  parameter="imagetyp", value="flat")
iraf.ccdhedit(rname+"_*.fit",  parameter="imagetyp", value="object")
for im in glob.glob('*.fit*'):
	unlearn(iraf.imgets)
	iraf.imgets(im, param="inttime")
	iraf.hedit(im, fields="exptime", value=iraf.imgets.value, add="no", addonly="yes", delete="no", verify="no", show="no", update="yes") 
for im in glob.glob("Dark*.fit"): 
	unlearn(iraf.imgets)
	iraf.imgets(im, param="inttime")
	iraf.hedit(im, fields="darktime", value=iraf.imgets.value, add="no", addonly="yes", delete="no", verify="no", show="no", update="yes") 

# creating master dark
unlearn(iraf.darkcombine) 
print "> creating master dark image"
iraf.darkcombine("Dark*.fit", output="master_dark.fits", combine="average", reject="none", ccdtype="dark", scale="none", process="no")

# creating master flat
unlearn(iraf.flatcombine) 
print "> creating master flat image"
iraf.flatcombine("Flat*.fit", output="master_flat_temp.fits", combine="median", reject="crreject", ccdtype="flat", process="no", delete="no", scale="median")
# removing 0s and negative values with standard ones (-9.0)
iraf.imcalc("master_flat_temp.fits", output="master_flat.fits", equals="if (im1.le.0.0) then -9.0 else im1", verbose="no")

# creating the necessary lists for dark and flat processing 
rd = open('rawdata.irafl','w')
cd = open('cordata.irafl','w')

for im in data:
#	print im
	name, ext = os.path.splitext(im)
# 	print name, ext
	rd.write(name+ext+"\n")
	cd.write(name+'_cor'+ext+'\n')
#	print name+'_cor'+ext+'\n'

rd.close()
cd.close()

# perfoming dark and flat correction 
unlearn(iraf.ccdproc) 
print "> processing the images with the master dark and flat"
iraf.ccdproc(images="@rawdata.irafl", output="@cordata.irafl", ccdtype="object", noproc="no", fixpix="no", oversca="no", trim="no", zerocor="no", darkcor="yes", flatcor="yes", illumco="no", fringec="no", readcor="no", scancor="no", dark="master_dark.fits", flat="master_flat.fits")	


# sorting corrected images to perform the sky subtraction, CAUTION: based on naming rules
# unix style for sorting according to 4rt column: ls NGC*cor.fit | sort -n -t_ -k 4
# custom way:
ones = []
twos = []
threes = []
for o in glob.glob('*cor.fit'):
#	print o.strip('_cor.fit').split('_')[3]		# observation number
	if len(o.strip('_cor.fit').split('_')[3])==1:
#		print "its one!"
		ones.append(o)
	elif len(o.strip('_cor.fit').split('_')[3])==2:
#		print "its two!"
		twos.append(o)
	elif len(o.strip('_cor.fit').split('_')[3])==3:
#		print "its three"
		threes.append(o)
	else:
		print "WARNING: more than 999 observations! [adjust script...]"

cordatals = []
for o in sorted(ones):
	cordatals.append(o)
for o in sorted(twos):
	cordatals.append(o)
for o in sorted(threes):
	cordatals.append(o)

#print "final list"
#for i in cordatals:
#	print i

imimlst = open('imexamine_image.irafl','w')	# preparing list
# subtracting sky
print "> processing the images for sky subtraction"
for i in range(0, len(cordatals),1):
	print i, cordatals[i], len(cordatals), cordatals[len(cordatals)-1]
	if i==len(cordatals)-1:
#		print "final step ", i, cordatals[i], cordatals[i-2]
		op1 = cordatals[i].split('_')[3]
		op2 = cordatals[i-2].split('_')[3]
		print "\tfinal step:"
	else:
#		print "normal step ", i, cordatals[i]
		op1 = cordatals[i].split('_')[3]
		op2 = cordatals[i+1].split('_')[3]
		print "\tnormal step:"
	print '  subtracting', rname+'_'+op1+'_cor.fit'+'-'+rname+'_'+op2+'_cor.fit', 'to create:', rname+'_'+op1+'-'+op2+'_df.fit' 
	iraf.imarith(operand1=rname+'_'+op1+'_cor.fit', op="-", operand2=rname+'_'+op2+'_cor.fit', result=rname+'_'+op1+'-'+op2+'_df.fit')
	imimlst.write(rname+'_'+op1+'-'+op2+'_df.fit'+'\n')
imimlst.close()

# setting display parameters and imexamine (<<< select star to align)
print "> displaying images to select the star used for alignment"
iraf.set(stdimage="imt1024")	
iraf.imexamine("@imexamine_image.irafl", frame=1, logfile="imexamine.irafl", keeplog="yes")

# preparation and manipulation of lists and align/shift processes
shimlst1 = open('images_to_shift.irafl','w')
shimlst22 = open('shifted_images.irafl','w')
imlog = open("imexamine.irafl", "r")	# selecting the x,y values only
lines = imlog.readlines()
imlog.close()

x = []
y = []
for lin in lines:
	lin.split(' ')
	if lin.split()[0]!="#":
		print lin.split()[0], lin.split()[1]
		x.append(float(lin.split()[0]))
		y.append(float(lin.split()[1]))

for i in range(0,len(lines),1):		# selecting only the images that have values of x,y, CAUTION:how to remove duplicates?
#	print i, lines[i]
	if lines[i].split()[1]=='COL':
		img = lines[i-1].split()[2]
		print "writing..." , img, img.replace('_df.fit','_sh.fit') 
		shimlst1.write(img+'\n')
		shimlst22.write(img.replace('_df.fit','_sh.fit')+'\n')
shimlst1.close()
shimlst22.close()

xave = sum(x)/len(x)
yave = sum(y)/len(y)
#print x,y sum(x)/len(x), sum(y)/len(y), xave,yave

# shifting of images
print "> shifting images"
iraf.lintran("imexamine.irafl", x1=xave, y1=yave, angle=180, Stdout="shiftlis.irafl")	# angle set for SKinakas IR
iraf.imshift("@images_to_shift.irafl", output="@shifted_images.irafl", shifts_file="shiftlis.irafl", boundary_type="constant", constant=0.0)

# creating the final image
print "> creating the final combined image,", rname+'_comb.fits' 
iraf.imcombine("@shifted_images.irafl", output=rname+'_comb.fit', combine="median")

# cleaning ...
rmvoption = raw_input('Would you like to remove all intermediate steps? [press "n" for no, else "enter"]\t')
if rmvoption=="n" or rmvoption=="N":
	print "\n Enjoy! ;)\n"
else:
	print "> removing"
	for l in glob.glob('*.irafl'):
		print " ...", l
		os.remove(l)
	for imc in glob.glob('*cor.fit'):
		print " ...", imc
		os.remove(imc)
	for imd in glob.glob('*df.fit'):
		print " ...", imd
		os.remove(imd)
	for ims in glob.glob('*sh.fit'):
		print " ...", ims
		os.remove(ims)
	for imf in glob.glob('*.fits'):
		print " ...", imf
		os.remove(imf)
	print "\n Enjoy! ;)\n"
		
