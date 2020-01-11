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

    def read_geojson(self, filepath):
        with codecs.open(filepath) as fin:
            return json.load(fin)

    def load(self):
        # load elevation data
        self.elevation = rasterio.open("../Material/elevation/SZ.asc")
        self.elevation_band = self.elevation.read(1)

        # for task 1, restrict user point in a range that is more than 5km from the bounding edge
        self.bound_polygon = self.bound_polygon(self.elevation.bounds)
        self.inner_polygon = self.bound_polygon.buffer(-5000)

        # load itn data
        self.itndata = self.read_geojson("../Material/itn/solent_itn.json")
        self.road_nodes = self.itndata["roadnodes"]

        # for task 3, build rtree from itn data
        count = 0
        self.itn_rtree = index.Index()
        for fid, node in self.road_nodes.items():
            corrds = node["coords"].copy()
            self.itn_rtree.insert(count, corrds, fid)
            count+=1




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


    def nearest_highpoint(self, p, radius):
        ''' Task 2: Find the highest point within a specified radius'''
        clip_image, clip_transform = clip_circle(self.elevation, p, radius)
        clip_band = clip_image[0]

        pcircle = p.buffer(radius)

        hp = [0, 0]
        # high point coords = clip_transform * hp
        hp_elevation = self.get_elevation(*(clip_transform * hp))

        rows, cols = clip_band.shape
        for row in range(rows):
            for col in range(cols):
                x, y = clip_transform * [row, col]

                if not pcircle.contains(Point(x, y)):
                    continue

                elevation = self.get_elevation(x, y);
                if elevation > hp_elevation:
                    hp = [row, col]
                    hp_elevation = elevation

        print(rows, cols, hp, hp_elevation)
        return Point(*(clip_transform * hp))

    def nearest_itnnode(self, p):
        ''' Task3: Find the nearest itn node from the point p,

        return:
                node feature id,
                node position point
        '''
        nodes = list(self.itn_rtree.nearest((p.x, p.y), num_results=1,
            objects=True))
        bbox = nodes[0].bbox
        return nodes[0].object, Point(bbox[0], bbox[1])



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

