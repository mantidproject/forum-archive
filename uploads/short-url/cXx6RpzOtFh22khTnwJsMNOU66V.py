# import mantid algorithms, numpy and matplotlib
from mantid.simpleapi import *
import matplotlib.pyplot as plt
import numpy as np

firstLoad = True #set this to True when you need to load and preprocess the data

#----------------------------------------------------------------------------
  #flux and solid angle data are loaded
#----------------------------------------------------------------------------
calDir = '/SNS/TOPAZ/IPTS-30595/shared/calibration/'
flux = calDir + 'flux_1p8-18.nxs'
solidAngle = calDir + 'solid_angle_1p8-18.nxs'
if( firstLoad ):
    Load(Filename = flux, OutputWorkspace = 'flux.nxs')
    Load(Filename = solidAngle, OutputWorkspace = 'solidAngle.nxs')
#----------------------------------------------------------------------------


#--- workspace names defined ---------
eventsName = 'TOPAZ_48446.nxs_event'
mdName = 'TOPAZ_48446.nxs_md'
peaksName = 'TOPAZ_48446.nxs_peaks'
#-------------------------------------

#----------------------------------------------------------------------------
  # nexus file from run 48446 is loaded to eventsName, bad pulses filtered
  # IsawDetCal is loaded to eventsName
  # eventsName converted to MD, MD output to mdName
  # peaks found in mdName, peaks output to peaksName
#----------------------------------------------------------------------------
nexusDir = '/SNS/TOPAZ/IPTS-30595/nexus/'
if( firstLoad ):
    Load(Filename = nexusDir + 'TOPAZ_48446.nxs.h5', OutputWorkspace = eventsName, FilterByTofMin=500, FilterByTofMax=16666)
    FilterBadPulses(InputWorkspace = eventsName, OutputWorkspace = eventsName, LowerCutoff=25)

    LoadIsawDetCal(InputWorkspace = eventsName, Filename = calDir + 'TOPAZ_2023B_CG.DetCal')

    ConvertToMD(InputWorkspace = eventsName, QDimensions='Q3D', dEAnalysisMode='Elastic', Q3DFrames='Q_sample', LorentzCorrection=True, OutputWorkspace = mdName, MinValues='-25,-25,-25', MaxValues='25,25,25', SplitInto='2', SplitThreshold=50, MaxRecursionDepth=13, MinRecursionDepth=7)
    FindPeaksMD(InputWorkspace = mdName, PeakDistanceThreshold=0.3768, MaxPeaks=200, DensityThresholdFactor=100, OutputWorkspace = peaksName)
#----------------------------------------------------------------------------

#----------------------------------------------------------------------------
  # UB matrix loaded into peaksName ( the UB was found earlier and known to be accurate. found using FindUBUsingFFT, SelectCellOfType, FindPeaksMD, FindUBUsingFFT, SelectCellOfForm, OptimizeLatticeForCellType )
  # peaks indexed
#----------------------------------------------------------------------------
UBdir = '/SNS/TOPAZ/IPTS-30595/shared/UBmatricesDefaultLocation/'
if( firstLoad ):
    LoadIsawUB( InputWorkspace = peaksName, FileName = UBdir + 'TOPAZ_48446_Optimize.mat' )

    IndexPeaks(PeaksWorkspace = peaksName, Tolerance=0.12, RoundHKLs=False)
    CopySample(InputWorkspace = peaksName, OutputWorkspace = mdName, CopyName=False, CopyMaterial=False, CopyEnvironment=False, CopyShape=False)
    CopySample(InputWorkspace = peaksName, OutputWorkspace = eventsName, CopyName=False, CopyMaterial=False, CopyEnvironment=False, CopyShape=False)
#----------------------------------------------------------------------------

mdHistoName = 'TOPAZ_48446.nxs_md_HKL_Histo'

#'''

#'''
#----------------------------------------------------------------------------
  # ConvertQtoHKLMDHisto -10 to 10 step 0.1
  # it appears that this function uses the following binning:
  #   min + ( max - min ) / (2N) + (n-1)( max-min ) / N
  #        or
  #   min + ( max – min )(  1 / (2N) + ( n – 1 ) / N  )

#----------------------------------------------------------------------------
hklExtents = 10.05 * np.array([ -1,1,-1,1,-1,1 ])
bins = 201 * np.array( [ 1, 1, 1 ] )
ConvertQtoHKLMDHisto(
    InputWorkspace = mdName,
    PeaksWorkspace = peaksName,
    Extents = hklExtents,
    Bins = bins,
    OutputWorkspace = mdHistoName )
#----------------------------------------------------------------------------
#'''

#'''
#----------------------------------------------------------------------------
  # IntegratePeaksMDHKL on mdHistoName
  # it appears that this function uses the following binning:
  #   min + (n-1)( max-min )/N
  # I am thinking the discrepency in binning is leading to runding
  # I think rounding might be leading to "Error in execution of algorithm IntegrateMDHistoWorkspace: Error making MDHistoDimension. Cannot have dimension with min > max" )
#----------------------------------------------------------------------------
IntegratePeaksMDHKL( 
    InputWorkspace = 'TOPAZ_48446.nxs_md_HKL_Histo',
    DeltaHKL = 0.3,
    GridPoints = 201,
    FluxWorkspace = 'flux.nxs',
    SolidAngleWorkspace = 'solidAngle.nxs',
    PeaksWorkspace = 'TOPAZ_48446.nxs_peaks',
    OutputWorkspace = 'TOPAZ_48446.nxs_peaks_int'
    )
#----------------------------------------------------------------------------
#'''

SaveHKL( InputWorkspace = 'TOPAZ_48446.nxs_peaks_int', FileName = '/SNS/TOPAZ/IPTS-30595/shared/hklFromMantidDefaultLocation/48446_normed.hkl' )
