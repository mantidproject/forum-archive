# Algorithm Family
class ParentAlg(PythonAlgorithm):
	def PyInit(self):
		self.declareProperty("N",10)
		self.declareProperty("P",0.5)
		self.declareProperty("Intermediate","")
		self.declareProperty("FinalTable","")
		
	def PyExec(self):

		fch=self.createChildAlgorithm("FirstChildAlg")
		fch.setProperty("Number",self.getProperty("N").value)
		fch.setPropertyValue("OutputTab",self.getProperty("Intermediate").value)
		fch.setChild(False)
		fch.execute()

		ch=self.createChildAlgorithm("ChildAlg")
		ch.setPropertyValue("InputTab",self.getProperty("Intermediate").value)
		ch.setProperty("Power",self.getProperty("P").value)
		ch.setPropertyValue("OutputTab",self.getProperty("FinalTable").value)
		ch.setChild(False)
		ch.execute()
		
AlgorithmFactory.subscribe(ParentAlg)

class FirstChildAlg(PythonAlgorithm):
	def PyInit(self):
		self.declareProperty("Number",8)
		self.declareProperty(ITableWorkspaceProperty("OutputTab","",direction=Direction.Output))
	
	def PyExec(self):
		N=self.getProperty("Number").value
		tt=WorkspaceFactory.createTable()
		tt.addColumn("int","N")
		tt.addColumn("double","factorial")
		f=1.0
		for i in range(N):
			tt.addRow([i,f])
			f=f*(i+1)
		self.setProperty("OutputTab",tt)

AlgorithmFactory.subscribe(FirstChildAlg)

class ChildAlg(PythonAlgorithm):
	def PyInit(self):
		self.declareProperty(ITableWorkspaceProperty("InputTab","",direction=Direction.Input))
		self.declareProperty("Power",1.0)
		self.declareProperty(ITableWorkspaceProperty("OutputTab","",direction=Direction.Output))
	
	def PyExec(self):
		P=self.getProperty("Power").value
		inter=self.getProperty("InputTab").value
		tt=WorkspaceFactory.createTable()
		tt.addColumn("int","N")
		tt.addColumn("double","factorial to power P")
		f=1.0
		for interrow in inter:
			tt.addRow([interrow["N"],interrow["factorial"] ** P])
		self.setProperty("OutputTab",tt)
		
AlgorithmFactory.subscribe(ChildAlg)

