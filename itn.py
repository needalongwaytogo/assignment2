from rtree import index
idx = index.Index()
import json

solent_itn_json = "C:/Users/pc/CEGE0096_2/Material/itn/solent_itn.json"
with open (solent_itn_json, "r") as f:
    solent_itn = json.load(f)
road_nodes = solent_itn['roadnodes']
# read the .json file in material and save to "road_nodes"

coords_nodes = []
for coords in road_nodes:
    coords_nodes_id = road_nodes[coords]['coords']
    coords_nodes.append(coords_nodes_id)
print(coords_nodes)
# create a set named "coords_nodes" and append the easting and northing coordinates into the set.

index = 0
for i in coords_nodes:
    idx.insert(index, (i[0], i[1], i[0], i[1]))
    index = index + 1
# create the square for each points but do not need to create the square for two near points.
# we only need to find the nearest point.

x = 450000
y = 850000
for i in idx.nearest((450000, 850000), 1):
    print(i)
# use idx.nearest function to find the nearest point.
# suppose the input point is (450000, 850000)




