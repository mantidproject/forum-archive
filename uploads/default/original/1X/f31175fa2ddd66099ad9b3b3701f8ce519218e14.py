import math
import numpy

# define the histogram-aware function
class HistoAwareLorentzian(IFunction1D):
	def init(self):
		self.declareParameter("Amplitude",1.0)
		self.declareParameter("PeakCentre",1.0)
		self.declareParameter("FWHM",1.0)
	def function1D(self,xpoints):
		xedges=numpy.zeros([len(xpoints)+1])
		xedges[1:-1]=(xpoints[:-1]+xpoints[1:])/2.0
		xedges[0]=(2*xpoints[0]-xpoints[1])
		xedges[-1]=(2*xpoints[-1]-xpoints[-2])
		# formula was Amplitude/pi/((x-PeakCentre)^2+(FWHM/2)^2)*FWHM/2
		# integral is:
		# Amplitude/pi * atan((x-PeakCentre)/(FWHM/2))
		Amplitude=self.getParameterValue("Amplitude")
		PeakCentre=self.getParameterValue("PeakCentre")
		FWHM=self.getParameterValue("FWHM")
		indefInt=Amplitude/math.pi * numpy.arctan((xedges-PeakCentre)*2/FWHM)
		return (indefInt[1:]-indefInt[:-1])/(xedges[1:]-xedges[:-1])
FunctionFactory.subscribe(HistoAwareLorentzian)

# time range for fit
xdata=WorkspaceFactory.create("Workspace2D",XLength=401,YLength=400,NVectors=1)
xdata.dataX(0)[:]=numpy.linspace(-10.0,10.0,401)
xdata.dataY(0)[:]=numpy.random.normal(loc=0.0,scale=0.01,size=400)
xdata.dataE(0)[:]=0.1
AnalysisDataService.addOrReplace("xdata",xdata)
# equivalent fit functions. Built in one uses analytical derivatives while the user one must use numerical differences.
BuiltIn="name=Lorentzian"
#UserVersion="name=UserFunction,Formula=Amplitude/3.141592654/((x-PeakCentre)^2+(FWHM/2)^2)*FWHM/2" # take care to introduce the vars in the same order!
HistoAware="name=HistoAwareLorentzian"
# evaluate the function and add noise
ytheory=EvaluateFunction(Function=BuiltIn+",Amplitude=1.0,PeakCentre=0.0,FWHM=1.0",InputWorkspace=xdata,OutputWorkspace="ytheory")
yexper=Plus(LHSWorkspace=xdata,RHSWorkspace=ytheory,OutputWorkspace="DynamicRange")
Guesses=(0.9,0.1,1.1)
# adjust the X axis and repeat the fits. Print the parameters adjusted back to a line centred at 0.
Results=WorkspaceFactory.createTable()
Results.addColumn("int","Bunching",plottype=1)
Results.addColumn("float","stdAmp",plottype=2)
Results.addColumn("float","stdAmpErr",plottype=5)
Results.addColumn("float","stdCen",plottype=2)
Results.addColumn("float","stdCenErr",plottype=5)
Results.addColumn("float","stdFWHM",plottype=2)
Results.addColumn("float","stdFWHMErr",plottype=5)
Results.addColumn("float","stdCost",plottype=2)
Results.addColumn("float","awareAmp",plottype=2)
Results.addColumn("float","awareAmpErr",plottype=5)
Results.addColumn("float","awareCen",plottype=2)
Results.addColumn("float","awareCenErr",plottype=5)
Results.addColumn("float","awareFWHM",plottype=2)
Results.addColumn("float","awareFWHMErr",plottype=5)
Results.addColumn("float","awareCost",plottype=2)
for bun in range(1,31):
	row=[0.0]*15
	row[0]=bun
	yexp05=Rebunch(InputWorkspace=yexper,NBunch=bun)
	yexp1=Scale(InputWorkspace=yexp05,Factor=1.0/bun,Operation="Multiply",OutputWorkspace="yexp1")
	for i,fn in enumerate((BuiltIn,HistoAware)):
		ffr=Fit(Function=fn+",Amplitude="+str(Guesses[0])+",PeakCentre="+str(Guesses[1])+",FWHM="+str(Guesses[2]),InputWorkspace=yexp1,WorkspaceIndex=1,Output="HistoFit")
		params=ffr[3].column(1)
		errors=ffr[3].column(2)
		row[i*7+1:i*7+8]=[params[0],errors[0],params[1],errors[1],params[2],errors[2],params[3]]
		print bun,params[0],errors[0],params[1],errors[1],params[2],errors[2],params[3]
	Results.addRow(row)
AnalysisDataService.addOrReplace("HistoAwareResults",Results)
