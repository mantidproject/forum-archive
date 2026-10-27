import numpy

# create a 2D workspace with a user Y axis
height=20
width=20
scale=0.1
image=numpy.random.normal(loc=0.0,scale=1.0,size=[width,height])
ws=WorkspaceFactory.create("Workspace2D",NVectors=height,XLength=width+1,YLength=width)
ws.setDistribution(True) # always polarisation or similar normalised value, not raw or simulated counts
xaxdat=numpy.linspace(0.0,width*scale,width+1)
yaxdat=numpy.linspace(0.0,(height-1)*scale,height)
for i in range(height):
	ws.dataX(i)[:]=xaxdat
	ws.dataY(i)[:]=image[:,height-1-i]
na = NumericAxis.create(height)
for i in range(height):
	na.setValue(i,yaxdat[i])
lbl=na.setUnit("Label")
lbl.setLabel("height","cm")
ws.replaceAxis(1,na)
lbl=ws.getAxis(0).setUnit("Label")
lbl.setLabel("width","cm")
ws.setYUnitLabel("brightness")

AnalysisDataService.addOrReplace("ws",ws)

# test it

# this works
CloneWorkspace(InputWorkspace="ws",OutputWorkspace="ClonedWS")
print CheckWorkspacesMatch(Workspace1="ws",Workspace2="ClonedWS")

# but this doesn't. Why?
ff="c:/users/jsl28/Desktop/foo.nxs" # somewhere writable
SaveNexus(InputWorkspace="ws",Filename=ff)
LoadNexus(Filename=ff,OutputWorkspace="CopyOfWS")
print CheckWorkspacesMatch(Workspace1="ws",Workspace2="CopyOfWS")

# and what about this
LoadNexus(Filename=ff,OutputWorkspace="AnotherCopy")
print CheckWorkspacesMatch(Workspace1="CopyOfWS",Workspace2="AnotherCopy")
