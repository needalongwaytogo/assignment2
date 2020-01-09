user_e = int(input("Input your esating: "))
user_n = int(input("Input your northing: "))
            
print (user_e)
print (user_n)
if user_n < 80000 or user_n > 95000 or user_e < 430000 or user_e > 4650000:
    print("Outside the extent!")
else:
    print("Current location: ","easting: ",user_e," northing: ",user_n)

# import packages
import rasterio
import pyproj
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from shapely.geometry import LineString
from shapely.geometry import Point
from shapely.geometry import Polygon

# read the elevation raster in 'Material⁩/background/raster-50k_2724246.tif'
elevation = rasterio.open("Material/elevation/SZ.asc")
from rasterio import plot
#rasterio.plot.show(elevation)
#print(elevation.width, elevation.height, elevation.dtypes)

# read elevation array
elevation_matrix = elevation.read(1)

# define a function to get elevation value of user input location
def get_elevation_value(eastings = user_e, northings = user_n):
    # calculate elevation array index (col_elevation, row_elevation)
    res_h = (470000-425000)/9000
    res_v = (100000-75000)/5000
    col_elevation = int((eastings - 425000)//res_h)
    row_elevation = int((abs(northings - 100000))//res_v)
    # access to the elevation value using elevation array index
    elevation_value = elevation_matrix[row_elevation, col_elevation]
    return (elevation_value)

print("Your elevation is", get_elevation_value(), "m.")

# draw a buffer with 5 km radius, user_loaction is the input user coordinates of easting and northing
user_location = Point(user_e, user_n)
user_buffer = user_location.buffer(5000)

'''resource https://www.cnblogs.com/shoufengwei/p/6437934.html

rasterio.mask document
https://rasterio.readthedocs.io/en/latest/api/rasterio.mask.html#rasterio.mask.mask
'''
# clip the elevation data using 5 km buffer
# import package to use rasterio.mask module to mask the dataset
import rasterio.mask
# input raster: elevation;       input vector: [user_buffer] list
# out_transform: Affine(5.0, 0.0, 434615.0,
#       0.0, -5.0, 90800.0)
out_elevation, out_transform = rasterio.mask.mask(elevation, feature, crop = True, nodata = elevation.nodata)

min_pixel = (0, 0)
max_pixel = (out_elevation[0].shape[1], out_elevation[0].shape[0])

# Affine matrix (6 parameters) * vector 
min_x, max_y = out_transform * min_pixel
max_x, min_y = out_transform * max_pixel

print(out_elevation[0])
print("box:",min_x, min_y, max_x, max_y)
