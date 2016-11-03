#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Year anomolies for a given test statistic.

Usage:
  yr_anomoly.py [options] <location> <example> <stat> <output>

Options:
     -h --help                   show help
     --year <year>		 Index of year in file name
     <output>			 Prefix for output
     <stat>			 Statistic to calculate anomoly
     <example>			 Example image
     

Notes:
  Stats will be added as needed. Initially it is only mean NDVI. 

"""



from docopt import docopt
import gdal, ogr, osr, os
import numpy as np
import os
import rasterio
from gdalconst import *

gdal.AllRegister()

def main():
    """ Read in the arguments """

    location = args['<location>']
    outpu = args['<output>']
    example_img = args['<example>']

    filelist=[]
    yearlist=[]
    rowlist=[]

    #Get list of files
    for subdir, dirs, files in os.walk(location, followlinks=True):
        for file in files:
            filepath = subdir + os.sep + file
            if filepath.endswith("npz"): 
                filelist.append(filepath)
		row=file.split("_")[1][1:]
		rowlist.append(int(row))

    #Open first file and get years
    all_ids = np.load(filelist[0])['image_IDs']
    for file in all_ids:
        year = int(file[9:13])
	yearlist.append(year)
    years = np.unique(yearlist)
    yearnum = len(years)

    #Get image attributes
    imnum= np.load(filelist[0])['Y'].shape[1]
    cols = np.load(filelist[0])['Y'].shape[2]
    rows = max(rowlist)


    #Prep the output image
    # open the image to get attribtues again. TODO: remove this - redundant
    inDs = gdal.Open(example_img,gdal.GA_ReadOnly)
    import pdb; pdb.set_trace()


    # read in the crop data and get info about it
    band1 = inDs.GetRasterBand(1)

    # create the output image
    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(outpu,
                           cols, rows, yearnum,
                           gdal.GDT_Int16)
    out_ds.SetGeoTransform(inDs.GetGeoTransform())
    out_ds.SetProjection(inDs.GetProjection())

    out_ds = None

    #Initiate arrays
    count=0

    yearlist = np.array(yearlist)
    imagelist = np.array(imagelist)

    mean=np.zeros((shape[1],shape[2]))

    #First get the average
    for row in range(shape[1]):
	print row
        stack=np.zeros((imnum,2,shape[2]))
        m_stack=np.ma.zeros((imnum,shape[2]))
            with rasterio.open(n, 'r+') as r:
                full_row = r.read(window=((row,row+1),(0,shape[2])))
                stack[count,0,:] = do_transform('ndvi',full_row)
                stack[count,1,:] = full_row[7,0,:]
            	m_stack[count,:]=np.ma.masked_where(stack[count,1,:]>1,stack[count,0,:])
                count+=1
        mean=np.ma.mean(m_stack,axis=0)
        import pdb; pdb.set_trace()

    #Loop over columns
    for q, y in enumerate(years):
        mean=np.zeros((shape[1],shape[2]))
	y_indices = np.where(yearlist == y)[0]
	y_images = imagelist[y_indices]
        for row in range(shape[1]):
            stack=np.zeros((imnum,2,shape[2]))
            m_stack=np.ma.zeros((imnum,2,shape[2]))
            mask=np.zeros((2,shape[2]))
            for n in y_images:
                with rasterio.open(n, 'r+') as r:
                    full_row = r.read(window=((row,row+1),(0,shape[2])))
                    stack[count,row,:,:] = do_transform('NDVI',full_row)
                    count+=1
    out_ds.GetRasterBand(1).WriteArray(mean[0,:,:])

def do_transform(transform, row):
    """ Transform the data to a spectral index if desired """

    if transform == 'ndvi':
	nir = row[2,0,:]
	red = row[3,0,:]
        ndvi = (nir - red) / (nir + red)

    return ndvi


if __name__ == '__main__':
    args = docopt(__doc__, version='0.1.0')
    main()






