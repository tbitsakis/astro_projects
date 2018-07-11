#! /usr/bin/python
"""
 = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
 PURPOSE:
   This code is fitting a list of observed cluster CMDs to theoretical isochrones from  
   Bruzual & Charlot (2003) and generates a likelihood distribution of the ages for each cluster.
   The basic idea originates from Walmswell+13, Method 2.
 
 INPUTS:
   The input file must contain a list with cluster stars identified by a common identity, per 
   cluster (string or numerical), the bands to be fitted, and a membership probability (for the 
   corresponding star to belong to the cluster; see Mighel+96)

   A directory containing all the isochrones from Bruzual & Charlot (2003)

   In the parameter section select the numbers that correspond to the correct coloumns of the input
   files (both cluster and isochrones)

 OUTPUTS:
   A file that contains the results of the fitting (one line per cluster). It contains the age
   that correspond to the maximum of the likelihood distribution, the uncertainty (estimated from
   the FWHM), the value of the maximum probability, and the number of stars in each cluster before 
   and after the selection.

   A file containing all the likelihood values, per cluster, in order to plot the distribution. 

 DEPENDENCIES:
   Astropy

 HISTORY:
   Created by:  Theodoros Bitsakis (Instituto de Radioastronomia y Astrofisica/UNAM, Mexico)
                Grigoris Maravelias (Astronomical Institute, Czech Academy of Sciences, Czechia )

 MODIFICATIONS:
    MultiSigmasInv instead of 1 changed to 1/(sigma_x * sigma_y)
    Shifting isochrones in N positions (loop in line 213) 
    Remove useless parameters not used by the model (e.g. SigmaPorRedondeo, SigmaGlobal, SigmaExt)
    It also reads all the necessary the parameters/inputs from the screen
 = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
 """
import sys, operator, time, glob
from math import pi, log, e
import numpy as np
start_time = time.time()
# =================================================================================================

# #################################################################################################
# ################################### EDIT BELOW THIS POINT #######################################
# #################################################################################################

# INPUT/OUTPUT FILES ==============================================================================
print '================================================================================'
print '                       Cluster Age Determination Algorithm                      '
print '                                                                                '
print '================================= INPUTS ======================================='
print '                                                                                '
InputClusterFile = raw_input('Input deconaminated cluster star catalogue: ') # InputClusterFile = 'test_in_cut.dat'            # INPUT FILE
OutputBestAges = raw_input('Output results catalogue: ') # OutputBestAges = 'results_out_test.dat'               # OUTPUT FILE
OutputIsochroneProbs = raw_input('Output likelihood catalogue: ') # OutputIsochroneProbs = 'results_likelihood_test.dat'  # OUTPUT FILE
print '                                                                                '
# =================================================================================================


# CLUSTER FILE ====================================================================================
MagObs1 = 3     # column that corresponds to 1-band (STARTS FROM [0])
Sigma1 = 4      # column that corresponds to the uncertainty 2-band (STARTS FROM [0])
MagObs2 = 5     # column that corresponds to 1-band (STARTS FROM [0])
Sigma2 = 6      # column that corresponds to the uncertainty 2-band (STARTS FROM [0])
ProbMember = 7  # column that corresponds to the membership probability (STARTS FROM [0])
cutoff = input('Cut-off magnitude: ') # cutoff = 21.0   # Y-axis mag cut-off
cut_prob = input('Cut-off membership probability: ') # cut_prob = 0.80 # membership prob. cut-off
# =================================================================================================


# ISOCHRONE FILE ==================================================================================
print '                                                                                '
IsochronesPath = "../all_isochrones/my_isoc_random_10k/*.cmd"
IsochroneFileVmagColID = input('Isochrone, 1-band (1:U, 2:B, 3:V, 4:I) ') # IsochroneFileVmagColID = 2  # column that corresponds to 1-band (STARTS FROM [0])
IsochroneFileImagColID = input('Isochrone, 1-band (1:U, 2:B, 3:V, 4:I) ') # IsochroneFileImagColID = 3  # column that corresponds to 2-band (STARTS FROM [0])
IsochroneFileAgeColID = 0    # column that corresponds to age (STARTS FROM [0])
DistModulus = 18.5           # Distance Modulus of our galaxy 
# =================================================================================================
print '                                                                                '
print '================================= Running ======================================'

# OTHER PARAMETERS ================================================================================
Umbral = 0.00001
# =================================================================================================

# #################################################################################################
# ################################ DO NOT EDIT BELOW THIS POINT ###################################
# #################################################################################################

# ################## Retrieve all theoretical values of V/I from isochrones files #################
isochrones_list = sorted(glob.glob(IsochronesPath))

outputages = open(OutputBestAges,'w')
outputages.write('#Cluster_ID   Age   Unc_low    unc_high   Probability   Nstars   Shift_Col\n')
outputprobs = open(OutputIsochroneProbs,'w')
outputprobs.write('#Cluster_ID   Age   Probability\n')

VmagTotal = []
ImagTotal = []
ColmagTotal = []

for isochronefile in isochrones_list:
#    print " ... reading", isochronefile
    V, I = np.loadtxt(isochronefile, comments='#', unpack=True,
           usecols=(IsochroneFileVmagColID,IsochroneFileImagColID))
    VmagTotal.extend(V+DistModulus) # Adding distance modulus to modify generic isochrone mags to desirable redshift
    ImagTotal.extend(I+DistModulus) # Adding distance modulus to modify generic isochrone mags to desirable redshift
    ColmagTotal.extend(V-I) # ISOCHRONE COLOUR - no need to add distance modulus

colyarr=np.asarray(ImagTotal)    # Y-axis, I-band
colxarr=np.asarray(ColmagTotal)  # X-axis, colour
nsetmod=len(ImagTotal)


# ################################## Read the input cluster file ##################################

datosobs2 = np.genfromtxt(InputClusterFile, dtype=None, comments='#')
arregloobs2 = []
cluster_list = []

for dato in datosobs2:
    sigmaHor=(dato[Sigma1]**2+dato[Sigma2]**2)**0.5 # Colour uncertainty
    if sigmaHor ==0: sigmaHor=0.1
    DosSigmaxCua=-2*sigmaHor**2 # See Walmswell+13, eq. 18
    
    Sigma2dat=dato[Sigma2] # 2-band uncertainty
    if Sigma2dat == 0: Sigma2dat=0.1
    DosSigmayCua=-2*Sigma2dat**2 # See Walmswell+13, eq. 18

    MultiSigmasInv=1./(2*pi*Sigma2dat*sigmaHor) 

    # We add the colour in the line below dato[MagObs1]-dato[MagObs2]
    arregloobs2.append([dato[MagObs1]-dato[MagObs2],DosSigmaxCua,dato[MagObs2],DosSigmayCua,MultiSigmasInv,dato[ProbMember],dato[0]])  

    cluster_list.append(dato[0])

cluster_list = list(set(cluster_list))



# ################################## Run analysis for each cluster #################################

# # In this block, the likelihood for all the stars of a given cluster to belong to all isochrones
# # is calculated simultaneously.
# # The reason is to find the stars with very low likelihoods and exclude them.
# # The actual calculation of likelihood as in Walmswell, is performed in the next block.

for cluster in cluster_list:             #cluster_list: 
    print "> Working on", cluster

    number_of_stars_in_cluster = [star for star in arregloobs2 if star[-1]==cluster]
    stars_of_cluster = [star for star in arregloobs2 if star[-1]==cluster and star[2]<cutoff and star[5]>cut_prob]

    if len(stars_of_cluster) < 10: continue #Skips all clusters with less than n-stars remaining after selection

    cluster_stars_initial = len(number_of_stars_in_cluster)


# ############################# Read isochrones and find likelihoods #############################

#    print "\n  STEP 2\n"
    arreglo2, arreglolikes2, arreglodist2 = [], [], []
    for isochronefile in isochrones_list:
        Vmag, Imag, age = np.loadtxt(isochronefile, comments='#', unpack=True,
                          usecols=(IsochroneFileVmagColID,IsochroneFileImagColID,IsochroneFileAgeColID))

        Imag_limit = max([s[2] for s in stars_of_cluster])+0.2     # Imagnitude cut 

        edad1 = age[0]
        colyarr2, colxarr2 = [], []
        for y, x in zip(Imag,Vmag):

            if y< Imag_limit:
                y_mod2=y+DistModulus    # Adding distance modulus to modify generic isochrone mags to desirable redshift
                col2=x-y                # ISOCHRONE COLOUR - no need to add distance modulus
                colyarr2.append(y_mod2)
                colxarr2.append(col2)           

        distanceProbs = []
        colShifts = [-0.25,-0.15,0.0,0.15,0.25] # Shift in the mag-axis to readjust for distance modulus effects
        for distCol in colShifts:
            likearray2b = []
            for star in stars_of_cluster:
    
                Pintegrada=0
                x0=star[0]  
                y0=star[2]
                Proba=star[5]
                DosSigmaxCua=star[1]
                DosSigmayCua=star[3]       
                MultiSigmasInv=star[4]
            
                Pcol=(MultiSigmasInv*np.exp(((((colxarr2-x0)**2)/(DosSigmaxCua)+((colyarr2-(y0-distCol))**2)/(DosSigmayCua)))))
                
                n_Pcol=len(Pcol) # Number of isochrone points eventually used for each star

                Pintegrada=sum(Pcol)*Proba/(n_Pcol^2) # Normalizing with Pcol length (number of points in isochrone used) and multiply by P_membership 
                if Pintegrada == 0: Pintegrada = 1e-50 # for very small numbers
                likelihood=log(Pintegrada)
                likearray2b.append(likelihood)
                # array of log of integrals (in dx0 dy0; see eq. 18), NOT likelihoods, for each star, associated to the current isochrone
    
            #likelihood2 = sum(likearray2b)
            likelihood2 = (1.0/len(likearray2b))*sum(likearray2b)
            # likelihood as in Eq.18 (note that it is a sum)
            # This is normalized by the number of stars
            # Is this normalization used to account for where there are more stars?
            # But all isochrones will be fit using the same number of stars, so it is useless, as the creator
            likelinealsinBoot2=e**likelihood2   
            distanceProbs.append(likelinealsinBoot2)
        maxlikelihood = max(distanceProbs)
        maxdist = colShifts[distanceProbs.index(maxlikelihood)]


        arreglo2.append(edad1)
        # filling the array with the age for each isochrone
        arreglolikes2.append(maxlikelihood)
        arreglodist2.append(maxdist)
        # filling the array containing likelihoods for each isochrone

    Norm2 = sum(arreglolikes2)
    arreglolikesNorm2 = [i/Norm2 for i in arreglolikes2]
    # normalizing likelihoods for all isochrones by the sum of all likelihoods
#    print arreglolikesNorm2.index(max(arreglolikesNorm2)), max(arreglolikesNorm2)

    max_arreglolikesNorm2 = max(arreglolikesNorm2)
    max_index = arreglolikesNorm2.index(max_arreglolikesNorm2)
    maxdistfinal = arreglodist2[max_index]

    maxim2=arreglo2[max_index]

    arrregfin2 = []
    for v1, v2 in zip(arreglo2, arreglolikesNorm2):
        vl = [v1]*int(round(v2*1000))
        arrregfin2.extend(vl)

#    standardeviacion=np.std(arrregfin2)
    unc_low=np.percentile(arrregfin2,16)
    unc_high=np.percentile(arrregfin2,84)

    print " --> For {}: best age {} with unc_low {} and unc_high {}, probability {} and shift {}".format(cluster, maxim2, unc_low, unc_high, max_arreglolikesNorm2, maxdistfinal)

    # save results:     QUESTION what else is needed?
    outputages.write('{}   {}   {}   {}   {}   {}  {}\n'.format(
        cluster, maxim2, unc_low,unc_high, max_arreglolikesNorm2, cluster_stars_initial,maxdistfinal))

#    outputprobs.write('#Cluster_ID   {}\n'.format('   '.join(isochrones_list)))
#    outputprobs.write('{} {} {}\n'.format(cluster, ' '.join(str(v) for v1,v2 in zip(arreglo2,arreglolikesNorm2)))
    for age, prob in zip(arreglo2, arreglolikesNorm2):
        outputprobs.write('{} {} {}\n'.format(cluster, age, prob))

outputages.close()
outputprobs.close()
print '================================= OUTPUTS ====================================='
print ' '
print 'Writing', OutputBestAges, OutputIsochroneProbs
print ' '
print '================================== END ========================================'
print("--- %s seconds ---" % (time.time() - start_time))
print ' '