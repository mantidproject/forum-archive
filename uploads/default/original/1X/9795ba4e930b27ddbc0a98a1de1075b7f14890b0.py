from mantid.simpleapi import *

# load McStas NeXus file
ws = Load('mccode.h5')

# Read the event data. Rebin and TOF conversion
sample = Rebin(ws[0],'10', False)
sample = ConvertUnits(sample, 'Wavelength')
binning = '1.75,0.05,16.5'
sample  = Rebin(sample, binning)

# Read normalizaion data
mcstasMonitor = CloneWorkspace(mtd['Edet0.dat_ws'])
mcstasMonitor = ConvertToHistogram(mcstasMonitor)
mcstasMonitor = rebin(mcstasMonitor, binning)
monitor = CreateWorkspace(mcstasMonitor.dataX(0), mcstasMonitor.dataY(0), mcstasMonitor.dataE(0), UnitX='Wavelength')

# Reduce data to scattering cuvre I(q)
binningMASK = '0.0035,0.001,0.7'
Iq_1D = Q1D(sample, binningMASK, WavelengthAdj='monitor')