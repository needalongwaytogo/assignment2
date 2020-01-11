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

# define function to clip elevation
def clip_rectangle(bg, p, dx, dy):
    mshape = Polygon([(p.x - dx / 2, p.y + dy / 2), (p.x + dx / 2, p.y + dy /2), (p.x + dx / 2, p.y - dy / 2), (p.x - dx / 2, p.y - dy / 2)])
    return rasterio.mask.mask(bg, [mshape], crop=True)


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

        # for task 4, build networkx graph from itn data, we store link feature id in Graph for
        # computing
        self.itn_graph = networkx.Graph()
        road_links = self.itndata['roadlinks']
        for link in road_links:
            s = road_links[link]['start']
            e = road_links[link]['end']

        # get start point elevation and end point elevation
        s_ele = self.get_elevation(self.road_nodes[s]["coords"][0], self.road_nodes[s]["coords"][1])
        e_ele = self.get_elevation(self.road_nodes[e]["coords"][0], self.road_nodes[e]["coords"][1])

        length = road_links[link]['length']

        # compute travel time according to Naismith's rule
        time = length * 60 / 5000 + max(e_ele - s_ele, 0) / 10
        self.itn_graph.add_edge(s, e, fid=link, weight=time)



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

    def shortest_route(self, s, e):
        ''' Task4: Find the shortest route between point p1 and p2point within a specified radius,

        return:

            path    shortest route between node s and e, path is a list of node feature id'''
        path = networkx.dijkstra_path(self.itn_graph, source=s, target=e, weight="weight")
        return path

    def plot(pu_itn, ph_itn, shortest_route): 
        
        bg = rasterio.open("../Material/background/raster-50k_2724246.tif")
        fig = pyplot.figure(dpi=600)
        ax = fig.add_subplot()

        clip_image, clip_trans = clip_rectangle(bg, pu,200, 150)
        ax = rasterio.plot.show(clip_image, ax=ax, origin="upper", transform=clip_trans)


class Runner(object):
    def __init__(self):
        pass
        
    def mainloop(self):
        x = int(input("Input your esating: "))
        y = int(input("Input your northing: "))
                
        model = FloodEmergencyModel()
        model.load()

        p_user = Point(x, y)
        print("User position {}".format(p_user))

        # task 1
        if not model.inbound(p_user):
            print("User not in Isle bound")
            return None

        # task 2
        p_high = model.nearest_highpoint(p_user, 5000)
        print("Nearest high point position {}".format(p_high))

        # task 3
                p_itn_user_fid, p_itn_user = model.nearest_itnnode(p_user)
        print("ITN node nearest to user fid={}, position={}".format(p_itn_user_fid, p_itn_user))
        p_itn_high_fid, p_itn_high = model.nearest_itnnode(p_high)
        print("ITN node nearest to highpoint fid={}, position={}".format(p_itn_high_fid, p_itn_high))

        # task 4
        route = model.shortest_route(p_itn_user_fid, p_itn_high_fid)
        print("Shortest route from {} to {}".format(p_itn_user_fid, p_itn_high_fid))
        print(route)

        # task 5
        def plot(pu_itn, ph_itn, shortest_route):
        plot = model.plot(p_user, p_high, p_itn_user, p_itn_high, route)
