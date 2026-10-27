import numpy
import time

minimisers= [
	'BFGS',
	'Conjugate gradient (Fletcher-Reeves imp.)',
	'Conjugate gradient (Polak-Ribiere imp.)',
	'Damping',
	'Levenberg-Marquardt',
	'Levenberg-MarquardtMD',
	'Simplex',
	'SteepestDescent',
	'FABADA',
	]

#minimisers.remove('FABADA')

funct0='name=ExpDecayOsc,A=%f,Lambda=%f,Frequency=%f,Phi=%f;name=GausDecay,A=%f,Sigma=%f;name=FlatBackground,A0=%f'
trueParams=(0.04,0.02,1.5,-0.2,-0.1,1.0,0.3)
guesses=(0.1,0.01,1.49,0.01,-0.08,1.2,0.2)
#funct='name=ExpDecayOsc,A=0.0067,Lambda=0.024,Frequency=0.57,Phi=-0.38;name=GausDecay,A=-0.018,Sigma=0.95;name=FlatBackground,A0=0.29'
funct=funct0 % guesses

timeBins=numpy.linspace(0.01,10.0,251)
noise=0.0005
errorY=numpy.random.normal(loc=0.0,scale=noise,size=250)

timeBase=CreateWorkspace(DataX=timeBins,DataY=timeBins[:-1],NSpec=1)
data=EvaluateFunction(Function=funct0 % trueParams,InputWorkspace=timeBase,OutputWorkspace="trialData")
data=ExtractSingleSpectrum(InputWorkspace=data,WorkspaceIndex=1)
data.dataY(0)[:] += errorY
data.dataE(0)[:]=noise


tt=WorkspaceFactory.createTable()
tt.addColumn("str","Minimiser",plottype=6)
tt.addColumn("int","Number",plottype=1)
tt.addColumn("int","AllowedIter",plottype=2)
tt.addColumn("str","Status",plottype=6)
tt.addColumn("double","Time",plottype=2)

for j,minim in enumerate(minimisers):
	if(minim=="FABADA"):
		maxiter0=1000 # initial max iter
		maxiter1=110000 # step this far at least
		maxiter9=66000000 # max to step to
	else:
		maxiter0=1 # initial max iter
		maxiter1=1 # step this far at least
		maxiter9=66000 # max to step to
	maxiter=maxiter0
	stat="after"
	print "trying",minim
	while(maxiter<maxiter9 and ("after" in stat or maxiter<maxiter1)):
		tupl=Fit(Function=funct,InputWorkspace=data,Output="fit1",Minimizer=minim,MaxIterations=maxiter)
		if(len(tupl)==5):
			(stat,chisq,cov,par,ws)=tupl
		else:
			(stat,chisq,PDF,cov,par,ws)=tupl # special for FABADA
		print "status:",stat,"chisq:",chisq
		functWFP=funct0 % tuple(par.column(1)[:-1])
		chis=CalculateChiSquared(Function=functWFP,InputWorkspace=data)
		if(tt.columnCount()<=5):
			for i in range(par.rowCount()):
				tt.addColumn("double",par.cell(i,0),plottype=2)
				if(i<par.rowCount()-1):
					tt.addColumn("double",par.cell(i,0)+"_Err",plottype=5)
				else:
					tt.addColumn("double","ChiSqWeighted/DOF",plottype=2)
		runtime=ws.getHistory().getAlgorithmHistory(ws.getHistory().size()-1).executionDuration()
		newrow=[minim,j,maxiter,stat,runtime]
		for i in range(par.rowCount()):
			newrow.append(par.cell(i,1))
			newrow.append(par.cell(i,2))
		newrow[-1]=chis[4] # ChiSqWeighted divided by DOF
		tt.addRow(newrow)
		maxiter=maxiter*2
AnalysisDataService.addOrReplace("FitSummaryTable",tt)
