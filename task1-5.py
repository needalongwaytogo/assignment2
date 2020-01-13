#!/usr/bin/env python
# -*- coding: utf-8 -*-
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


def clip_circle(bg, p, radius, nodata=numpy.nan):
    '''Clip a circle region on the background bg
        bg      the background
        p       center point
        radius  circle radius
    '''
    mshape = p.buffer(radius)
    return rasterio.mask.mask(bg, [mshape], crop=True, nodata=nodata)

def clip_rectangle(bg, p, dx, dy):
    '''Clip a circle region on the background bg
        bg      the background
        p       center point
        dx      rectangle width
        dy      rectangle height
    '''
    mshape = Polygon([(p.x - dx / 2, p.y + dy / 2), (p.x + dx / 2, p.y + dy /2), (p.x + dx / 2, p.y - dy / 2), (p.x - dx / 2, p.y - dy / 2)])
    return rasterio.mask.mask(bg, [mshape], crop=True)

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

    def get_elevation(self, x, y):
        '''Get elevation in the point (x, y)'''
        row, col =  self.elevation.index(x, y)
        return self.elevation_band[row, col]

    def color_source(self, image, transform):
        X = []
        Y = []
        Z = []
        band = image[0]
        rows, cols = band.shape
        for row in range(rows):
            xc = []
            yc = []
            rc = []

            for col in range(cols):
                x, y = transform * [row, col]
                xc.append(x)
                yc.append(y)
                rc.append(self.get_elevation(*(transform * [row, col])))
            X.append(xc)
            Y.append(yc)
            Z.append(rc)
        return X, Y, Z

    def inbound(self, p):
        ''' Task 1: Find the highest point within a specified radius'''
        return self.inner_polygon.contains(p) or self.inner_polygon.touches(p)

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
        nodes = list(self.itn_rtree.nearest((p.x, p.y), num_results=1, objects=True))
        bbox = nodes[0].bbox
        return nodes[0].object, Point(bbox[0], bbox[1])

    def shortest_route(self, s, e):
        ''' Task4: Find the shortest route between point p1 and p2point within a specified radius,

        return: 

            path    shortest route between node s and e, path is a list of node feature id'''
        path = networkx.dijkstra_path(self.itn_graph, source=s, target=e, weight="weight")
        return path

    def plot(self, pu, ph, pu_itn, ph_itn, shortest_route):
        ''' Task5: Find the highest point within a specified radius
            pu                  User position
            ph                  Highpoint position
            pu_itn              ITN node nearest to user
            ph_itn              ITN node nearest to highpoint
            shortest_route      shortest_route between pu_itn and ph_itn 
        '''
        bg = rasterio.open("../Material/background/raster-50k_2724246.tif")

        fig = pyplot.figure(dpi=600)
        ax = fig.add_subplot()

        # plot blackground which 20000 width and 15000 height
        clip_image, clip_trans = clip_rectangle(bg, pu, 20000, 15000)
        ax = rasterio.plot.show(clip_image, ax=ax, origin="upper", transform=clip_trans)

        # plot elevation
        clip_image, clip_trans = clip_circle(self.elevation, pu, 5000)
        ax = rasterio.plot.show(clip_image, ax=ax, transform=clip_trans, alpha=0.9)

        cX, cY, cZ = self.color_source(clip_image, clip_trans)
        psm = ax.pcolormesh(cX, cY, cZ, alpha=0.9, facecolor='none')
        fig.colorbar(psm, ax=ax, fraction=0.046, pad=0.04)

        # four points
        pX = [pu.x, ph.x, pu_itn.x, ph_itn.x]
        pY = [pu.y, ph.y, pu_itn.y, ph_itn.y]
        pColor = ["#C73B0B", "#f2317f", "#6b48ff", "#350608"]
        pLabel = ["user", "highpoint", "user's nearest itn", "highpoint's nearest itn"]

        for i in range(4):
            pyplot.scatter(pX[i], pY[i], color=pColor[i], label=pLabel[i])

        # shortest route
        # first get position coords information on the route
        routeX = []
        routeY = []
        for node in shortest_route:
            routeX.append(self.road_nodes[node]["coords"][0])
            routeY.append(self.road_nodes[node]["coords"][1])

        pyplot.plot(routeX, routeY, color="red", label="shortest route")

        # north arrow
        x, y, arrow_length = 0.05, 0.95, 0.01
        ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length - 0.1),
                    arrowprops=dict(facecolor='black', width=5, headwidth=15),
                    ha='center', va='center', fontsize=20,
                    xycoords=ax.transAxes)

        # scacle bar
        scalebar = ScaleBar(1, location='lower left')
        pyplot.gca().add_artist(scalebar)

        pyplot.xlabel('Easting')
        pyplot.ylabel('Northing')
        pyplot.title('Shortest route to nearest high point')
        pyplot.legend(fontsize='xx-small')
        return pyplot


class Runner(object):
    def __init__(self):
        pass

    def mainloop(self):
        x = int(input("Input your easting: "))
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
        plot = model.plot(p_user, p_high, p_itn_user, p_itn_high, route)
        plot.savefig("spatial.png", format="png")
