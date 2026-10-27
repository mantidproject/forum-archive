from mantid.simpleapi import *
from mantid.api import DataProcessorAlgorithm, AlgorithmFactory, PropertyMode, MatrixWorkspaceProperty, \
                       WorkspaceGroupProperty, FileProperty, FileAction, NumericAxis
from mantid.kernel import StringListValidator, StringMandatoryValidator, IntBoundedValidator, \
                          FloatBoundedValidator, Direction, logger
from mantid import config
import math
import os.path, numpy as np

class LoadInxAscii(DataProcessorAlgorithm):
 
    _instr = 'IN5'
    _input = None
    _e_crop = None
    _e_min = None
    _e_max = None

    def category(self):
        return "Workflow\\MIDAS;PythonAlgorithms"

    def summary(self):
        return "Read nxs file from LAMP"

    def PyInit(self):
        self.declareProperty(FileProperty('File', '', action = FileAction.OptionalLoad,
                                          extensions = [".inx"]),
                             doc = 'File name')
        self.declareProperty(name='Instrument', defaultValue='IN5',
                             doc = 'Instrument name')

    def PyExec(self):
        workdir = config['defaultsave.directory']
        error = self._setup()
        if error:
            return

        path, fname = self._get_FilePath(self._file)
        logger.information('Reading file : ' + path)
        asc = self._loadFile(path)
        len_asc = len(asc)       #number of input lines

        val = self._extract_int(asc[0])
        len_grp = int(val[0])    #number of lines in group
        num_grp = int(val[2])    #group number
        title = asc[1]
        len_tot = num_grp * len_grp   #total number of lines
        logger.information('Number of spectra : ' + str(num_grp))
        if len_tot == len_asc:
            error = ''
        else:
            error = 'file ' + fname + ' should be ' + str(len_tot) + ' lines'
            logger.information('ERROR *** ' + error)
            sys.exit(error)
        xDat = []
        yDat = []
        eDat = []
        ns = 0
        Q = []
        tot = []
        for m in range(num_grp):
            Qq, nd, xd, yd, ed = self._read_inx_group(asc, m, len_grp)
            tot.append(sum(yd))
            logger.information('Spectrum ' + str(m + 1) + ' at Q= ' + str(Qq) + ' ; Total counts = ' + str(sum(yd)))
            Q.append(Qq)
            for n in range(0, nd):
                xDat.append(xd[n])
                yDat.append(yd[n])
                eDat.append(ed[n])
            xDat.append(2 * xd[nd - 1] - xd[nd - 2])
            ns += 1
# create temporary ws for inx data
        temp_ws = '__inx'
        CreateWorkspace(OutputWorkspace=temp_ws,
                        DataX=xDat,
                        DataY=yDat,
                        DataE=eDat,
                        Nspec=ns,
                        UnitX='DeltaE')
# load instrument parameters
        idf_dir = config['instrumentDefinition.directory']
        idf = idf_dir + self._instr + '_Definition.xml'
        LoadInstrument(Workspace=temp_ws, Filename=idf, RewriteSpectraMap=False)
        inst = mtd[temp_ws]
        self._emode = inst.getInstrument().getStringParameter('deltaE-mode')[0]
        logger.information('Instrument %s is %s' % (self._instr, self._emode))
        asc_ws = fname + '_' + self._emode + '_inx'
        logger.information('INX file is %s' % (asc_ws))
        RenameWorkspace(InputWorkspace=temp_ws,
                        OutputWorkspace=asc_ws)
        error = self._instr_paras(asc_ws)
        if error:
            return

# change the detector values using Q & efixed
        self._run_paras(asc_ws, title)
        pi4 = 4.0 * math.pi
        ewave = math.sqrt(81.787 / self._efixed)
        k0 = 4.0 * math.pi / ewave
        theta = []
        for n in range(ns):
            qw = Q[n] / k0
            ang = 2.0 * math.degrees(math.asin(qw))
            theta.append(ang)
        self._change_angles(asc_ws, theta)

        out_ws = fname + '_' + self._emode + '_inx_sqw'
        CloneWorkspace(InputWorkspace=asc_ws,
                       OutputWorkspace=out_ws)
        ws = mtd[out_ws]
        q_values = np.array(Q)
        q_axis = NumericAxis.create(ns)
        ws.setYUnitLabel("Intensity")  # sets the title at the top to Intensity
        q_axis.setUnit("MomentumTransfer")  # sets the unit displayed on the axis
        for i in range(ns):
            q_axis.setValue(i, q_values[i])
        ws.replaceAxis(1, q_axis)
		
    def _setup(self):
        self._file = self.getProperty('File').value
        self._instr = self.getProperty('Instrument').value
        idf = self._instr + '_Definition.xml'
        if os.path.exists(os.path.join(config['instrumentDefinition.directory'], idf)):
            logger.information('IDF is %s' % (idf))
            return False         # no error
        else:
            logger.warning('IDF %s does not exist' % idf)
            return True          #error
   
    def _read_inx_group(self, asc, n, lgrp):  # read ascii x,y,e
        x = []
        y = []
        e = []
        first = n * lgrp
        last = (n + 1) * lgrp
        val = self._extract_float(asc[first + 2])
        Q = val[0]
        for m in range(first + 4, last):
            val = self._extract_float(asc[m])
            x.append(val[0])
            y.append(val[1])
            e.append(val[2])
        npt = len(x)
        return Q, npt, x, y, e  # values of x,y,e as lists

    def _instr_paras(self, ws):
        workdir = config['defaultsave.directory']
        idf_dir = config['instrumentDefinition.directory']
        ipf_name = self._instr + '_' + self._emode + '_inx_Parameters.xml'
        ipf_path = workdir + ipf_name
        inst = mtd[ws].getInstrument()
        if os.path.exists(os.path.join(config['defaultsave.directory'], ipf_name)):
            LoadParameterFile(Workspace=ws, Filename=ipf_path)
            if inst.hasParameter('EFixed'):
                self._efixed = inst.getNumberParameter('EFixed')[0]
                logger.information('Efixed in %s : %f' % (ipf_path, self._efixed))
                return False          #no error
            else:
                logger.warning('Efixed is not defined in IPF %s' % ipf_path)
                return True          #error
        else:
            logger.warning('IPF %s does not exist' % ipf_path)
            return True          #error

    def _change_angles(self, inWS, theta):
        workdir = config['defaultsave.directory']

        ws = mtd[inWS]
        theta = []
        for i in range(ws.getAxis(1).length()):
            theta.append(ws.getAxis(1).getValue(i))
        filename = self._instr + '_angles.txt'
        path = os.path.join(workdir, filename)
        logger.information('Creating angles file : ' + path)
        handle = open(path, 'w')
        head = 'spectrum,theta'
        handle.write(head + " \n")
        for n in range(0, len(theta)):
            handle.write(str(n + 1) + '   ' + str(theta[n]) + "\n")
#            logger.information('Spectrum %i = %f' % ((n + 1), theta[n]))
        handle.close()
        UpdateInstrumentFromFile(Workspace=inWS,
                                 Filename=path, 
                                 MoveMonitors=False,
                                 IgnorePhi=False,
                                 AsciiHeader=head)

    def _run_paras(self, asc_ws, title):
        AddSampleLog(Workspace=asc_ws, LogName='input_file', LogType="String", LogText=self._file)
        AddSampleLog(Workspace=asc_ws, LogName='data_type', LogType="String", LogText='inx')
        AddSampleLog(Workspace=asc_ws, LogName='deltaE-mode', LogType="String", LogText=self._emode)
        AddSampleLog(Workspace=asc_ws, LogName="efixed", LogType="Number", LogText=str(self._efixed))
        AddSampleLog(Workspace=asc_ws, LogName='run_title', LogType="String", LogText=title)
        return

    def _get_FilePath(self, run):
# Get the path to the file
# checks if we already know the path, else
# returns searches of the file based on run number and instrument
        path = None
        fname = None
        if os.path.isfile(run):
        # using full file path
            path = run
        # base name less extension
            base = os.path.basename(path)
            fname = os.path.splitext(base)[0]
        else:
        # using run number
            path = FileFinder.getFullPath(self._instr + "_" + run + '.inx')
            fname = self._instr + "_" + run

        if path:
            return path, fname
        else:
            error = 'ERROR *** Could not find ' + ext + ' file: ' + fname
            sys.exit(error)

    def _loadFile(self, path):
# Load an ascii file
        try:
            handle = open(path, 'U')
            asc = []
            for line in handle:
                line = line.rstrip()
                asc.append(line)
            handle.close()

            return asc
        except RuntimeError:
            error = 'ERROR *** Could not load ' + path
            sys.exit(error)

    def _extract_float(self, data_string):
#    Extract float values from an ASCII string
        values = data_string.split()
        values = [float(v) for v in values]
        return values

    def _extract_int(self, data_string):
#    Extract int values from an ASCII string
        values = data_string.split()
        values = [int(v) for v in values]
        return values

AlgorithmFactory.subscribe(LoadInxAscii)      # Register algorithm with Mantid
