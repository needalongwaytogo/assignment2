start = (439619, 85800)
end = (460000, 92500)

import json
import rasterio
from shapely.geometry import Point
import networkx as nx

solent_itn_json = "C:/Users/pc/CEGE0096_2/Material/itn/solent_itn.json"
with open (solent_itn_json, "r") as f:
    solent_itn = json.load(f)
road_links_node = solent_itn['roadlinks']
road_links_node_elevation = []
elevation = rasterio.open("C:/Users/pc/CEGE0096_2/Material/elevation/SZ.asc")
def get_elevation(a, b):
    elevation = rasterio.open("C:/Users/pc/CEGE0096_2/Material/elevation/SZ.asc")
    elevation_matrix = elevation.read(1)
    x, y = (elevation.bounds.left + a - elevation.bounds.left, elevation.bounds.top + elevation.bounds.top - b)
    row, col = elevation.index(x, y)
    return elevation_matrix[row, col]


g = nx.Graph()
road_links = solent_itn['roadlinks']
for link in road_links:
    Time = []
    pt_start = Point(road_links[link]['coords'][0])
    elevation_start = get_elevation(pt_start.x, pt_start.y)
    for i in road_links[link]['coords'][1:]:
        pt = Point(i)
        elevation_difference = get_elevation(pt.x, pt.y) - elevation_start
        pt_start = pt
        if elevation_difference > 0:
            Time.append(pt.distance(pt_start)/5000 + elevation_difference/600)
        else:
            Time.append(pt.distance(pt_start)/5000)
    g.add_edge(road_links[link]['start'], road_links[link]['end'], fid=link, weight=Time)


#nx.draw(g, node_size=1)

path = nx.dijkstra_path(g, source=(450000, 85000), target=(460000, 92500), weight="weight")
def color_path(g, path, color="blue"):
    res = g.copy()
    first = path[0]
    for node in path[1:]:
        res.edges[first, node]["color"] = color
        first = node
    return res
def obtain_colors(graph, default_node="blue", default_edge="black"):
    node_colors = []
    for node in graph.nodes:
        node_colors.append(graph.nodes[node].get('color', default_node))
    edge_colors = []
    for u, v in graph.edges:
        edge_colors.append(graph.edges[u, v].get('color', default_edge))
    return node_colors, edge_colors
g_1 = color_path(g, path, "red")

node_colors, edge_colors = obtain_colors(g_1)

nx.draw(g_1, node_size=1, edge_color=edge_colors, node_color=node_colors)