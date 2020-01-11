#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import packages
import codecs
import json
import numpy
import networkx
import rasterio
import rasterio.mask
import rasterio.plot
from rtree import index
from shapely.geometry import Point, Polygon
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.colors import Normalize
import matplotlib.pyplot as pyplot


# defien function to clip raster using buffer polygon
def clip_circle(bg, p, radius, nodata=numpy.nan):
'''Clip a circle region on the background bg
    bg      the background
    p       center point
    radius  circle radius
'''
mshape = p.buffer(radius)
return rasterio.mask.mask(bg, [mshape], crop=True, nodata=nodata)

# build a class
class FloodEmergencyModel(object):
    def __init__(self):
        pass
    
    def bound_polygon(self, r):
        return Polygon([(r.left, r.top), (r.right, r.top), (r.right, r.bottom), (r.left, r.bottom)])

    def load(self):
        # load elevation data
        self.elevation = rasterio.open("Material/elevation/SZ.asc")
        self.elevation_band = self.elevation.read(1)

        # read elevation array
        elevation_matrix = elevation.read(1)

    # define a function to get elevation value of user input location
    def get_elevation(self, x, y):
        '''Get elevation in the point (x, y)'''
        row, col =  self.elevation.index(x, y)
        return self.elevation_band[row, col]
        
    
    def inbound(self, p):
        if user_n < 80000 or user_n > 95000 or user_e < 430000 or user_e > 4650000:
            print("Outside the extent!")
        else:
            print("Current location: ","easting: ",user_e," northing: ",user_n)


    out_elevation, out_transform = rasterio.mask.mask(elevation, feature, crop = True, nodata = np.nan)

    min_pixel = (0, 0)
    max_pixel = (out_elevation[0].shape[1], out_elevation[0].shape[0])


    #print(out_elevation[0])
    #print("box:",min_x, min_y, max_x, max_y)

    # set out_elevation array to one dimension
    out_elevation_array = out_elevation[0]

    max_elevation = np.max(out_elevation_array)
    max_elevation_index = np.where(out_elevation_array==np.max(out_elevation_array))

class Runner(object):
    def __init__(self):
        pass
        
    def mainloop(self):
    x = int(input("Input your esating: "))
    y = int(input("Input your northing: "))
                
    model = FloodEmergencyModel()
    model.load()

 

    # task 1
    # task 2
    # task 3
    # task 4
    # task 5

