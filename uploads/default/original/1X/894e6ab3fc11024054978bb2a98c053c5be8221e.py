from mantid import config
from scipy.interpolate import interp1d

instrum = 'IRIS'
runs = [74945]
path = 'C:/Users/gqz43167/Documents/Calorimetry/SP'
config['default.instrument'] = '%s' % instrum

########################################################################################################################
def TableOut(t):
    """Writes out tables as tab separated .dat file for other graphing programmes"""
    runname=str(runno)
    if not os.path.exists('%s/%s' % (path, runname)):
        os.makedirs('%s/%s' % (path, runname))

    header = mtd[t].getColumnNames()
    FileOut = open('%s/%s/interp.txt' % (path, runname), 'w')
    for column in range(mtd[t].columnCount()):
        title = header[column]
        FileOut.write(str(title))
        FileOut.write('\t')
    FileOut.write('\n')    
    for row in range(mtd[t].rowCount()):
        for column in range(mtd[t].columnCount()):
            value = mtd[t].cell(row, column)
            FileOut.write(str(value))
            FileOut.write('\t')
        FileOut.write('\n')
    FileOut.close()
    print "File written: %s/%s/interp.txt" % (path, runname)
########################################################################################################################


for runno in runs:
    print "Loading data..."
    ws = Load('%s' % runno)
    run = ws.getRun()
    types = ['RT','RB','ST','SB','RH','SH','CL','CR','TLCCR']
    type_names = {'RT' : 'Ref_top','RB' : 'Ref_bot','ST' : 'Sample_top','SB' : 'sample_bot','RH' : 'Ref_heater_output','SH' : 'Sample_heater_output','CL' : 'CURRENT_LEFT','CR' : 'CURRENT_RIGHT','TLCCR' : 'TLCCR'}


    print "Setting interpolation settings from Ref_top..."
    # create array from Ref_top
    RT = ExportTimeSeriesLog(InputWorkspace = 'ws', LogName='Ref_top', IsEventWorkspace=False)
    x = RT.readX(0)
    y = RT.readY(0)
    firstdata = np.array([x,y])
    firsttime = np.array(firstdata[0:1, 0:].flatten(), dtype=float)
    firstval= np.array(firstdata[0:,1:].flatten(), dtype=float)

    # Using time limits to create the adjusted time axis, with same number of points, but linearly spaced
    start = np.amin(firsttime)
    end = np.amax(firsttime)
    points = np.shape(firsttime)[0]*5
    adj_time = np.linspace(start, end, points, endpoint=True)
    #print adj_time

    print "Setting up table..."
    vallist=[]
    ianterp = CreateEmptyTableWorkspace()
    ianterp.addColumn(type = "float", name = "time", plottype = 1)
    
    for type in types:
        print "Adding %s column" % type_names[type]
        ianterp.addColumn(type = "float", name = "%s" % type, plottype = 2)    
        logdata = ExportTimeSeriesLog(InputWorkspace = 'ws', LogName=type_names[type], IsEventWorkspace=False)
        x = logdata.readX(0)
        y = logdata.readY(0)
        data = np.array([x,y])
    #    print np.shape(data)

        print "Interpolating %s data" % type_names[type]
        interp_linear = interp1d(x, y, kind='linear', bounds_error=False, fill_value=0)
        interp_val = interp_linear(adj_time)
        vallist.append(interp_val)
        RenameWorkspace(InputWorkspace = 'logdata', OutputWorkspace=type)
    #    print vallist

    print "Filling table:"
    for pt in range(points):
        print "row %s" % pt
        newrow =[]
        newrow.append(adj_time[pt])
        for foo in range(len(types)):
            param = vallist[foo][pt]
            newrow.append(param)
        ianterp.addRow(newrow)

    print "Writing output..."

    TableOut('ianterp')

    print "Done!"