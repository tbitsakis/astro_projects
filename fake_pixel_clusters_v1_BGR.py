#! /usr/bin/python

'''
/ DESCRIPTION / ----------------------------------------------------------------

This program produces artificial clusters uniformly distributed within an image.
The samplings are as follow:
  o number of clusters                      -> uniform
  o cluster radius                          -> uniform
  o stars in the cluster                    -> uniform
  o location of stars around cluster center -> 2D multinormal gaussian

Modify "CHECK THESE VARIABLES" to tune the parameters.

/ USAGE / ----------------------------------------------------------------------

USAGE: fake_pixel_clusters.py
OUTPUT: o clusters.fits : FITS file where each non-0 pixel represents a star
        o clusters.txt  : log file containing the cluster properties
        o clusters.reg  : ds9 region file showing the generated clusters

/ HISTORY / --------------------------------------------------------------------

12/08/2016: fake_pixel_clusters_v0.py /

16/08/2016: fake_pixel_clusters_v1.py /

> Update:
> Corrected: SNR was lacking a square factor
> Fixed:

/ MEMO / -----------------------------------------------------------------------

> create command line parsing

/ AUTHOR / ---------------------------------------------------------------------

Creator: T. Bitsakis, P. Bonfini

Modify at your own risk!

/ NOTICE / ---------------------------------------------------------------------

> requires pyfits:

  $> pip install pyfits

--------------------------------------------------------------------------------
'''

import numpy as np
import pyfits
import warnings
import random
import os
from math import pi as PI

################################################################################
# CHECK THESE VARIABLES! #######################################################
################################################################################

# Limits of [uniform] sampling of the number of clusters in the whole image:
n_clusters_min = 5
n_clusters_MAX = 5
# NOTE: expecting 20-30 clusters in a 1000x1000 [pixel] image

# Limits of [uniform] sampling of the cluster radius (1-sigma) [pixel]:
r_min = 70
r_MAX = 70

# Limits of [uniform] sampling of the number of stars in the cluster:
#n_stars_min = 15
#n_stars_MAX = 45
# expected: 10 -- 100

NAXIS1 = 1500
NAXIS2 = 1500
# size of image [pixel]
# NOTE: I am SURE that using different sizes requires fixing the arrays indexes
#       because _numpy_ swithces the intuitive x and y axis

pixel_value = 1000.
# pixel value where a star will be located

#-------------------------------------------------------------------------------

noise_level = 0.0009
# To use a direct noise level:
# noise_level = 1000. / (NAXIS1 * NAXIS2)
# background stars in the whole image [stars/pixel^2]

#signal_level_avg = (n_stars_MAX + n_stars_min)/2. / (PI * ((r_MAX + r_min)/2.)**2) 
# average signal level calculated from the average number of stars within the average cluster radius (1-sigma)
#
# NOTE: The stars of a cluster distributed within the 1-sigma radius are only
#       0.6827 of the total.
#       In the way the 2D gaussian is constructed (i.e. by multiplying two
#         one-dimensional gaussians see _np.random.multivariate_normal_), the
#         normalization should be N1 * N2 where N1 and N1 are the normalizations
#         in each direction.
#       Therefore, the 2D 1-sigma enclosed "counts" are:
#           (N1 * 68%) * (N2 * 68%)
#       However, we will input the total normalization n_stars = N1 * N2, so that
#         the enclosed 2D 1-sigma "counts" are:
#           n_stars * (68%)**2

#SNR_avg = signal_level_avg / noise_level
SNR_avg = 1.
# average S/N ratio for the clusters in the image
# This in not the real S/N but rather the Signal-to-Background = Signal-Noise/Noise. 
# The real S/N = (Signal-Noise)*Area/sqrt(Noise*Area)
################################################################################


image        = np.zeros((NAXIS1,NAXIS2))
image_signal = np.zeros((NAXIS1,NAXIS2))
image_noise  = np.zeros((NAXIS1,NAXIS2))

name = 'clusters_reg4'
FITS = name+".fits"
log  = name+".txt"
REG  = name+".reg"

header = "" + \
"# [0]: cluster center x                  [pixel]\n"         + \
"# [1]: cluster center y                  [pixel]\n"         + \
"# [2]: cluster radius (Gaussian 1-sigma) [pixel]\n"         + \
"# [3]: stars in cluster\n"                                  + \
"# [4]: SNR (avg)\n"                                         + \
"# [5]: noise level (avg)                 [stars/pixel^2]\n" + \
"#"

os.system("echo \'" + header + "\' > " + log)


n_clusters = int(round(random.uniform(n_clusters_min,n_clusters_MAX)))
# number of clusters in the whole image

print "Clusters to be generated: " + str(n_clusters)

image_signal = np.zeros((NAXIS1, NAXIS2))

for c in range(n_clusters):
# c = cluster index

#    print "[==> cluster #%s <==]" % (c)

    r = round(random.uniform(r_min,r_MAX) , 1)
    # radius of cluster [pixel]

    #n_stars = int(round(random.uniform(n_stars_min,n_stars_MAX)))
    # number of stars per cluster

    x_c = random.randint(1, NAXIS1)
    y_c = random.randint(1, NAXIS2)
    # x, y center of cluster [pixel]

#    print "o x_c   | ", x_c
#    print "o y_c   | ", y_c
#    print "o r     | ", r
#    print "o stars | ", n_stars
    
    # generating signal --------------------------------------------------------

    image_cluster = np.random.random((r, r))
    # filling signal image with uniformly sampled, random floats between 0 -- 1

    image_cluster[noise_level > image_cluster/SNR_avg] = pixel_value
    image_cluster[((noise_level <= image_cluster/SNR_avg) & (image_cluster != pixel_value))] = 0.
    n_stars = sum(image_cluster[image_cluster == pixel_value] ) / pixel_value
    # Filling image pixels corresponding to stars of current cluster:

    #print int(y_c+r/2.-1)-int(y_c-r/2.-1),int(x_c+r/2.-1)-int(x_c-r/2.-1)
    image_signal[int(y_c-r/2.-1):int(y_c+r/2.-1),int(x_c-r/2.-1):int(x_c+r/2.-1)] = image_cluster
    #---------------------------------------------------------------------------

    # generating noise ---------------------------------------------------------

    image_noise = np.random.random((NAXIS1, NAXIS2))
    # filling noise image with uniformly sampled, random floats between 0 -- 1

    # Substituting _pixel_value_ at pixel position where the probability
    #   to find a star per pixel (i.e. _noise_level_) is higher than the
    #   probability associated to the pixel by random.random
    # This creates an image with 1 where a background star is present, and
    #   0 elsewhere

    image_noise[noise_level > image_noise] = pixel_value
    image_noise[((noise_level <= image_noise) & (image_noise != pixel_value))] = 0.
    #---------------------------------------------------------------------------

    # adding noise and signal images -------------------------------------------

    image = np.add(image_signal,image_noise)

    image[np.where(image > pixel_value)] = pixel_value
    # replacing "star" pixels, since the addition will multiply the value
    #---------------------------------------------------------------------------

    fmt = ["%-4.0f", "%-4.0f", "%-5.1f", "%-5.0f", "%-g", "%-g"]

    np.savetxt("temp_" + log, np.c_[x_c,y_c,r,n_stars,SNR_avg,noise_level], delimiter=' ', fmt=fmt)
    os.system("cat temp_" + log + " >> " + log)
    os.system("rm temp_" + log)

# generating region files for clusters -----------------------------------------
os.system("echo \"global color=red dashlist=8 3 width=1 font=\\\"helvetica 10 normal roman\\\" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\" > " + REG)
os.system("echo \"image\" >> " + REG)
os.system("awk \'{if (($1 !~ \"#\") && ($0 !~ /^$/)) printf \"box(%s,%s,%s,%s) # text={%s stars}\\n\", $1, $2, $3, $3, $4}\' " + log + " >> " + REG)

#-------------------------------------------------------------------------------

# writing image ----------------------------------------------------------------

# suppressing writeto warnings - - - - - - - - - - - - - - - - - - - - - - - - -
warnings.resetwarnings()
warnings.filterwarnings('ignore', category=UserWarning, append=True)
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

pyfits.writeto(FITS, image, clobber=True)
pyfits.writeto('signal.fits', image_signal, clobber=True)
#-------------------------------------------------------------------------------
