import h5py
import numpy as np
from mantid.simpleapi import CreateMDHistoWorkspace
from mantid.simpleapi import DeltaPDF3D
from mantid.simpleapi import SaveMD
import matplotlib.pyplot as plt

fld0 = 'C:/Users/Gebruiker/Desktop/hdf5/'
fname = 'reconstruction_199_201_203.h5'
 
f = h5py.File(fld0+fname,'r')

dx = np.array(f['data'][()])
                           
input = CreateMDHistoWorkspace(Dimensionality=3,
    Extents='-8,8,-8,8,-8,8',
    SignalInput=dx,
    ErrorInput=np.ones(dx.shape),
    NumberOfBins='199,201,203',                         
    Names=('[H,0,0]','[0,K,0]','[0,0,L]'),
    Units='rlu,rlu,rlu',Frames='HKL,HKL,HKL')
    
fig, ax = plt.subplots()
im = ax.imshow(input.getSignalArray()[:,:,0])
fig.show()