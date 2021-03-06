try:
    paraview.simple
except:
    from paraview.simple import *

XDMF_temporalFields_xmf = GetActiveSource()

ProgrammableFilter1 = ProgrammableFilter()

ProgrammableFilter1.RequestUpdateExtentScript = ''
ProgrammableFilter1.PythonPath = ''
ProgrammableFilter1.RequestInformationScript = ''

ProgrammableFilter1.Script = """
import paraview
import numpy
import vtk.numpy_interface.dataset_adapter


tensor_components = [
    "StressField_0", "StressField_3", "StressField_4",
    "StressField_3", "StressField_1", "StressField_5",
    "StressField_4", "StressField_5", "StressField_2"]
symmetric = True

##########################################################
output.ShallowCopy(self.GetInputDataObject(0,0))
pd = output.PointData
Tensors = pd["StressField"]
Tensors = Tensors.transpose()

N = Tensors.shape[2]
eigenvalues = numpy.empty((N,3), dtype=numpy.float32)
eigenvectors = numpy.empty((N,3,3), dtype=numpy.float32)
#fractional_anisotropy = numpy.empty((N,1), dtype=numpy.float32)

if symmetric:
    func = numpy.linalg.eigh
else:
    func = numpy.linalg.eig

for i in xrange(N):
    ## How do I speed up this slow loop?
    eigenvalues[i,:], eigenvectors[i,:,:] = func(Tensors[:,:,i])
    idx = eigenvalues[i,:].argsort()
    eigenvalues[i,:] = eigenvalues[i,idx]
    eigenvectors[i,:,:] = eigenvectors[i,:,idx]    

for i in xrange(3):
    pd.AddArray(
    dataset_adapter.numpyTovtkDataArray(
        eigenvalues[:,i], name=("EigVal_%d" % (i+1))))
    pd.AddArray(
        dataset_adapter.numpyTovtkDataArray(
            eigenvectors[:,:,i], name=("EigVec_%d" % (i+1))))


"""
SetActiveSource(ProgrammableFilter1)

DataRepresentation = Show()

Render()

