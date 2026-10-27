import numpy
# time range for fit
xdata=WorkspaceFactory.create("Workspace2D",XLength=500,YLength=500,NVectors=1)
xdata.dataX(0)[:]=numpy.linspace(-5.0,5.0,500)
xdata.dataY(0)[:]=numpy.random.normal(loc=0.0,scale=0.1,size=500)
xdata.dataE(0)[:]=0.1
AnalysisDataService.addOrReplace("xdata",xdata)
# equivalent fit functions. Built in one uses analytical derivatives while the user one must use numerical differences.
BuiltIn="name=Lorentzian"
UserVersion="name=UserFunction,Formula=Amplitude/3.141592654/((x-PeakCentre)^2+(FWHM/2)^2)*FWHM/2" # take care to introduce the vars in the same order!
# evaluate the function and add noise
ytheory=EvaluateFunction(Function=BuiltIn+",Amplitude=1.0,PeakCentre=0.0,FWHM=1.0",InputWorkspace=xdata,OutputWorkspace="ytheory")
yexper=Plus(LHSWorkspace=xdata,RHSWorkspace=ytheory,OutputWorkspace="DynamicRange")
Guesses=(0.9,0.1,1.1)
# adjust the X axis and repeat the fits. Print the parameters adjusted back to a line centred at 0.
for fn in BuiltIn,UserVersion:
	print fn
	for p1 in range(0,20):
		yexp1=ScaleX(InputWorkspace=yexper,Factor=2.0**p1,Operation="Add",OutputWorkspace="yexp1")
		Guesses1=(Guesses[0],Guesses[1]+2.0**p1,Guesses[2])
		ffr=Fit(Function=fn+",Amplitude="+str(Guesses1[0])+",PeakCentre="+str(Guesses1[1])+",FWHM="+str(Guesses1[2]),InputWorkspace=yexp1,WorkspaceIndex=1,Output="DynamicRange")
		params=ffr[3].column(1)
		errors=ffr[3].column(2)
		print 2.0**p1,params[0],errors[0],params[1]-2.0**p1,errors[1],params[2],errors[2],params[3]
