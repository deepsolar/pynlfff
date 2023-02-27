"""
Purpose:   [1] plot the nlfff product (hdf or bin format) to picture

Usage:     This code depends on the numpy vtk
           The first librarie is in the standard Anaconda distribution.
           The h5py matplotlib library can be obtained from pip
           This code is compatible with python 3.7.x.

Examples:  None Now

Adapted:   Xinze Zhang (zhangxinze17@mails.ucas.ac.cn) Edit Python (2022)

"""

import os
import numpy as np
from PIL import Image,ImageDraw
import vtk
from vtkmodules.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray


def hmiPreprocess(data):
    return (np.clip(data,-200,200)+200)/400*255

def genVtkImage(data):
    nz,ny,nx=data.shape
    volume=numpy_to_vtk(data.flatten())
    vtkImage=vtk.vtkImageData()
    vtkImage.SetDimensions(nx,ny,nz)
    vtkImage.GetPointData().SetScalars(volume)
    return vtkImage

def genVolume(id=3):
    volumeMapper=vtk.vtkFixedPointVolumeRayCastMapper()

    volumeProperty=vtk.vtkVolumeProperty()
    volumeProperty.ShadeOn()

    opacityTransferFunction = vtk.vtkPiecewiseFunction()
    opacityTransferFunction.AddPoint(0, 1.0)
    opacityTransferFunction.AddPoint(127.5, 0.0)
    opacityTransferFunction.AddPoint(255,1.0)
    volumeProperty.SetScalarOpacity(opacityTransferFunction)

    volumeColor=vtk.vtkColorTransferFunction()
    for idx in range(0,256):
        if id==0:
            volumeColor.AddRGBPoint(idx,idx/255,0,0)
        elif id==1:
            volumeColor.AddRGBPoint(idx,0,idx/255,0)
        elif id==2:
            volumeColor.AddRGBPoint(idx,0,0,idx/255)
        else:
            volumeColor.AddRGBPoint(idx,*[idx/255]*3)

    volumeProperty.SetColor(volumeColor)

    volume=vtk.vtkVolume()
    volume.SetMapper(volumeMapper)
    volume.SetProperty(volumeProperty)

    return volume,volumeMapper

def genVolumeRen(axis_idx=3):
    ren= vtk.vtkRenderer()
    ren.SetBackground(0.0, 0.0, 0.0)  
    ren.SetGradientBackground(1)
    
    ren.volume,ren.volumeMapper=genVolume(axis_idx)
    ren.AddVolume(ren.volume)

    return ren

def genCutPlaneRen():
    ren = vtk.vtkRenderer()
    ren.SetBackground(0.0, 0.0, 0.0)  
    ren.SetGradientBackground(1)

    cutPlane=vtk.vtkPlane()
    cutPlane.SetOrigin( 0.0, 0.0, 0.001*2000 )
    cutPlane.SetNormal( 0.0, 0.0, 1.0 )
    cutter=vtk.vtkCutter()
    cutter.SetCutFunction( cutPlane )

    ren.cutter=cutter

    cutterMapper=vtk.vtkPolyDataMapper()
    cutterMapper.SetInputConnection( cutter.GetOutputPort() )
    cutterMapper.SetScalarRange(0, 255.0)
  
    colorTable = vtk.vtkLookupTable()
    colorTable.SetNumberOfTableValues(256)
    for idx in range(0,256):
        colorTable.SetTableValue(idx,*[idx/255]*3,1.0)
    cutterMapper.SetLookupTable(colorTable)

    cutterActor=vtk.vtkActor()
    cutterActor.SetMapper( cutterMapper )

    ren.AddActor(cutterActor)

    return ren,cutPlane

def genAuxComp():
    camera=vtk.vtkCamera()

    axesActor=vtk.vtkAxesActor()
    axesActor.SetPosition(0, 0, 0)
    axesActor.SetTotalLength(2, 2, 2)
    axesActor.SetShaftType(0)
    axesActor.SetCylinderRadius(0.02)

    cubeAxesActor = vtk.vtkCubeAxesActor()
    cubeAxesActor.SetCamera(camera)
    cubeAxesActor.SetFlyMode(3)
    cubeAxesActor.SetXTitle("x")
    cubeAxesActor.SetYTitle("y")
    cubeAxesActor.SetZTitle("z")
    cubeAxesActor.SetUse2DMode(1)
    cubeAxesActor.SetZAxisVisibility(1)
    cubeAxesActor.SetDrawXInnerGridlines(1)
    cubeAxesActor.SetDrawYInnerGridlines(1)
    cubeAxesActor.SetDrawZInnerGridlines(1)

    return camera,axesActor,cubeAxesActor

def setRen(ren,viewport,camera,cubeAxesActor):
    ren.SetViewport(viewport)
    ren.AddActor(cubeAxesActor)
    ren.SetActiveCamera(camera)
    ren.ResetCamera()

def genImg(data,percentage,value_name='bz',axis_name='z',withFn=False):
    nx,ny,nz=data.shape
    if axis_name=='x':
        x=int(nx*percentage/100.0)
        x=0 if x<0 else (x if x<nx else nx-1)
        fn,img='%s_x_%d_%d'%(value_name,percentage,x),Image.fromarray(data[x,:,:]).transpose(Image.ROTATE_90)
    elif axis_name=='y':
        y=int(ny*percentage/100.0)
        y=0 if y<0 else (y if y<ny else ny-1)
        fn,img='%s_y_%d_%d'%(value_name,percentage,y),Image.fromarray(data[:,y,:]).transpose(Image.ROTATE_90)
    else:
        z=int(nz*percentage/100.0)
        z=0 if z<0 else (z if z<nz else nz-1)
        fn,img='%s_z_%d_%d'%(value_name,percentage,z),Image.fromarray(data[:,:,z]).transpose(Image.FLIP_TOP_BOTTOM)

    if withFn:
        draw = ImageDraw.Draw(img)
        draw.text((4,4), fn, fill='black')

    return fn,img

def main_draw_3d_body(dataBout,out_dir,axis_name=['bx','by','bz','bnorm2'],bar="auto"):
    # dataBout=pic4d.copy()
    # out_dir="/home/zander/Desktop/draw"
    dataBout=hmiPreprocess(dataBout)
    dataBout=np.concatenate((dataBout,np.expand_dims(np.linalg.norm(dataBout,axis=0,ord=2)/3,axis=0)),axis=0)
    axis_num,nx,ny,nz=dataBout.shape
    
    screenSizeX=1600
    screenSizeY=1600  

    for axis_idx in range(0,axis_num):
        if bar=="auto":
            ren0=genVolumeRen(axis_idx)
        else:
            ren0=genVolumeRen(3)
        camera,axesActor,cubeAxesActor=genAuxComp()
        setRen(ren0,[0.0, 0.0, 1.0, 1.0],camera,cubeAxesActor)

        textActor = vtk.vtkTextActor()
        textActor.GetTextProperty().SetColor(1.0, 0.0, 0.0)
        textActor.GetTextProperty().SetFontSize(32)

        renWin = vtk.vtkRenderWindow()
        renWin.OffScreenRenderingOn()
        renWin.AddRenderer(ren0)
        renWin.SetSize(screenSizeX, screenSizeY)
        renWin.Render()

        vtkWriter = vtk.vtkJPEGWriter()
        windowto_image_filter = vtk.vtkWindowToImageFilter()
        vtkWriter.SetInputConnection(windowto_image_filter.GetOutputPort())
        windowto_image_filter.SetInputBufferTypeToRGBA()
        windowto_image_filter.SetInput(renWin)

        cubeAxesActor.SetBounds(0,nx*1.2,0,ny*1.2,0,nz*1.2)
        cubeAxesActor.SetXAxisRange(0, nx*1.2)
        cubeAxesActor.SetYAxisRange(0, ny*1.2)
        cubeAxesActor.SetZAxisRange(0, nz*1.2)

        camera.SetViewUp(0, 0, 1)
        camera.SetFocalPoint (0, 0, 0)
        camOffset=0.0
        camPos=max([nx,ny,nz])*4.0
        camera.SetPosition (camPos+camOffset, camPos-camOffset, camPos)
        camera.SetFocalPoint (camOffset, -camOffset, camPos*0.1)
        camera.ComputeViewPlaneNormal()


        data=dataBout[axis_idx].swapaxes(0, 2)
        vtkImagenlfff3D=genVtkImage(data)
        ren0.volumeMapper.RemoveAllInputs()
        ren0.volumeMapper.SetInputData(vtkImagenlfff3D)
        ren0.ResetCamera()
        renWin.Render()
        windowto_image_filter.Modified()
        outFn=os.path.join(out_dir,axis_name[axis_idx]+'_cube.jpg')
        print(outFn)
        vtkWriter.SetFileName(outFn)
        vtkWriter.Write()
