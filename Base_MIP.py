
import matplotlib.pyplot as plt
import math
import load_forest_data as lfd
import load_forest_data1 as lfd1
import collections
import pickle
from collections import defaultdict
import random
from pqdict import PQDict
import xlwt
from xlwt import Workbook
import openpyxl
import time
import numpy as np
import gurobipy as gp
import os
from gurobipy import GRB
from scipy.spatial import ConvexHull
import json
import ast
import sys
from math import sqrt
from random import randint, shuffle
from shapely.geometry import Polygon
from shapely.ops import unary_union

fractional_counter=0
wb = Workbook()
best_z_ratio=0
# add_sheet is used to create sheet.
sheet1 = wb.add_sheet('Frac_Solution')
hourtimelimit=0
no_circle = 1
rows = 5
m = 1000
columns = 5
width = 10
nu = 8
ID = 1
g = 30
U = np.array(list(range(1, nu + 1)))
area_p = 0.05  # min budget area
are_p = area_p
min_comp = {}
for i in range(no_circle):
    min_comp[i + 1] = 0
bud_p = 0.1

# 0.5,1
limit = 1
dtol = 0.0005  # distance cut tolerance
mip_gap = 0
solve_new = True
use_lazy = True
use_random_data = False
use_inc = True
use_species = False
use_obj_cuts = True
use_compact = False
use_small_area = True
use_hole_callback = True
use_warmstart = False
use_heu = False
use_fractoint = True
option = 1  ### 1: Best Bound, 0: DFS (default is 1)
incr = 0
counter = True
epsi = 1e-6
onal = {}
hole = []
sel = {}
w = {}
x_inc_v = {}
w_inc_v = {}
k1_inc_v = {}
k2_inc_v = {}
k3_inc_v = {}
u_inc_v = {}
incumbents = {}
incumbentCounter = 0
incumbentSol = {}
incumbentCenterRadius = {}
incumbentCriticalPoints = {}
ccpIntegerOptimizeProblemsol = []
ccpIntegerOptimizeProblemobj = 0
test = []
zz = 0
Trig = 0
obje = 0
prev_sol = {}
for i in range(no_circle):
    prev_sol[i + 1] = []
# Directories
print("area_p:",area_p, "and bud_p:",bud_p)
data_dir = "data/"
results_dir = "results/"

circ = []

for i in range(no_circle):
    circ.append(i + 1)

for i in circ:
    w[i] = {}
###############################################################
class Graph: 
    # init function to declare class variables
    def __init__(self, V, nodes):
        self.V = V
        self.nodes = nodes
        self.adj = collections.defaultdict(list)

    def DFSUtil(self, temp, v, visited):
        visited[v] = True
        temp.append(v)

        # Repeat for all vertices adjacent
        for i in self.adj[v]:
            if not visited[i]:
                # Update the list
                temp = self.DFSUtil(temp, i, visited)
        return temp
        # method to add an undirected edge
    def addEdge(self, v, w):
        self.adj[v].append(w)
        self.adj[w].append(v)
        # Method to retrieve connected components
    # in an undirected graph
    def connectedComponents(self):
        visited = collections.defaultdict(bool)
        cc = []
        for v in self.nodes:
            if not visited[v]:
                temp = []
                cc.append(self.DFSUtil(temp, v, visited))
        return cc


def generate_unit_vectors(nu, U):
    delta = 2 * math.pi / nu
    angle = 0
    u1 = {}
    u2 = {}
    for i in U:
        u1[i] = round(math.cos(angle), 6)
        u2[i] = round(math.sin(angle), 6)
        angle += delta
    return u1, u2


u1, u2 = generate_unit_vectors(nu, U)


# Visualization utilities
def plot_solution(centers, width, selected, cost): # for random data can be removed
    for i in centers.keys():
        if i in selected:
            c = "r"
            a = 0.8
        else:
            c = "b"
            a = 0.08
        x = centers[i][0]
        y = centers[i][1]
        plt.plot([x - width / 2, x - width / 2], [y - width / 2, y + width / 2], alpha=a, color=c)
        plt.plot([x - width / 2, x + width / 2], [y + width / 2, y + width / 2], alpha=a, color=c)
        plt.plot([x + width / 2, x + width / 2], [y + width / 2, y - width / 2], alpha=a, color=c)
        plt.plot([x + width / 2, x - width / 2], [y - width / 2, y - width / 2], alpha=a, color=c)
        plt.text(x - width / 2, y, "({0})".format(round(cost[i], 2)), fontsize=10)
    plt.show()


def plot_solution_new(centers, width, selected, rad, centre, cost) -> object:# for random data can be removed
    fig, ax = plt.subplots()
    circ = {}
    for i in circ:
        cir[i] = plt.Circle(centre[i], radius=rad[i], color="b", alpha=0.2)
        ax.add_patch(cir[i])
        ax.plot()
    for i in centers.keys():
        if i in selected:
            c = "r"
            a = 0.8
        else:
            c = "b"
            a = 0.08
        x = centers[i][0]
        y = centers[i][1]
        plt.plot([x - width / 2, x - width / 2], [y - width / 2, y + width / 2], alpha=a, color=c)
        plt.plot([x - width / 2, x + width / 2], [y + width / 2, y + width / 2], alpha=a, color=c)
        plt.plot([x + width / 2, x + width / 2], [y + width / 2, y - width / 2], alpha=a, color=c)
        plt.plot([x + width / 2, x - width / 2], [y - width / 2, y - width / 2], alpha=a, color=c)
        plt.text(centers[i][0], centers[i][1], i)
    plt.show()


def generate_random_data(rows, columns, ID, width):# for random data can be removed
    def generate_polygon_centers(rows, columns, width):
        centers = {}
        x = width / 2
        y = width / 2
        ctr = 1
        for i in range(rows):
            for j in range(columns):
                centers[ctr] = (x + width * j, y + width * i)
                ctr += 1
        return centers

    def plot_grid(centers, width, cost):
        vertices = {}
        for i in centers.keys():
            vertices[i] = []
            x = centers[i][0]
            y = centers[i][1]
            plt.plot([x - width / 2, x - width / 2], [y - width / 2, y + width / 2], "b")
            vertices[i].append((x - width / 2, y - width / 2))
            plt.plot([x - width / 2, x + width / 2], [y + width / 2, y + width / 2], "b")
            vertices[i].append((x - width / 2, y + width / 2))
            plt.plot([x + width / 2, x + width / 2], [y + width / 2, y - width / 2], "b")
            vertices[i].append((x + width / 2, y + width / 2))
            plt.plot([x + width / 2, x - width / 2], [y - width / 2, y - width / 2], "b")
            vertices[i].append((x + width / 2, y - width / 2))
            vertices[i].append((x - width / 2, y - width / 2))
            plt.text(x - width / 2, y, "({0})".format(round(cost[i], 2)), fontsize=10)
        plt.show()
        return vertices

    centers = generate_polygon_centers(rows, columns, width)

    distance = {}
    for i in centers.keys():
        for j in centers.keys():
            distance[i, j] = ((centers[i][0] - centers[j][0]) ** 2 + (centers[i][1] - centers[j][1]) ** 2) ** 0.5

    neighbours = {}
    for i in centers.keys():
        neighbours[i] = []
        for j in centers.keys():
            if i != j and distance[i, j] <= width:
                neighbours[i].append(j)

    area = {}
    for i in centers.keys():
        area[i] = width ** 2

    filename = "grid_" + str(rows) + "x" + str(columns) + "_" + str(ID) + ".txt"

    def generate_costs(rows, columns, lb, ub):
        cost = {}
        for i in range(1, rows * columns + 1):
            cost[i] = np.random.uniform(lb, ub)
        return cost

    def write_data(filename, r, c, ub, lb):
        cost = generate_costs(r, c, lb, ub)
        f1 = open(filename, "w")
        for i in cost.keys():
            f1.write(str(i) + "\t" + str(cost[i]) + "\n")
        f1.close()
        return cost

    def read_data(filename):
        f1 = open(filename, "r")
        cost = {}
        for i in f1.readlines():
            j = i.strip().split("\t")
            cost[int(j[0])] = float(j[1])
        f1.close()
        return cost

    # cost=write_data(data_dir+filename,rows,columns,10,15)
    cost = read_data(data_dir + filename)
    vertices = plot_grid(centers, width, cost)

    circ = {}
    for i in centers.keys():
        circ[i] = round((area[i] / (2 * math.pi)) ** 0.5, 4)

    return centers, vertices, distance, neighbours, area, cost, circ
################################################################################################################

def use_subset_for_landscape(nodes, verticess, adj, area, cost, centers, ax, bx, ay, by): #this def finds nodes that are in selected area
    tbr = []
    count_number_of_nodes=0
    for i in nodes:
        trueval = True
        for j in verticess[i]:
            if (j[0] < ax or j[0] > bx) or (j[1] < ay or j[1] > by):
                trueval = False

                
                break
        if not trueval:
            tbr.append(i)
            
            
    nodes = list(i for i in nodes if i not in tbr) #which node will be considered or not considered

    for i in tbr:
        adj.pop(i)
        
        cost.pop(i)
        area.pop(i)
        verticess.pop(i)
        centers.pop(i)

    
    for i in adj.keys():
        adj[i] = list(i for i in adj[i] if i not in tbr) #remove neighbors that are not in the selected area

    return area, cost, nodes, adj, verticess, centers

###########reading data anbudget and area calculation###########
if use_random_data:
    nodes = list(range(1, rows * columns + 1))
    min_area = area_p * len(nodes) * width * width
    centers, vertices, distance, neighbours, area, cost, circ = generate_random_data(rows, columns, ID, width)
    xlim = columns * width
    ylim = rows * width
else:
    flgid = 5

    # A_max: Maximum area of the instance. Choose from one of these options
    # 1) 48.6 - for FLG9A instances.
    # 2) 40   - for Hardwicke and Shulkell and Random
    # 3) 80   - for NBCL5A instance.
    # 4) 120  - for El Dorado and Buttercreek.
    A_max = 48.6

    # T: Time periods: The value is 3 for the given model.
    T = 3

    # Yt: Number of years in each time period. Set this to 10 for El Dorado instance, 5 otherwise.
    Yt = 5

    #Data = lfd.FLG9A(A_max, T, flgid)  ## Import Data for FLG9A (5 instances)
    # Data=lfd.ButterCreek(A_max,T) ## Import Data for Buttercreek
    # Data=ld.NBCL5A(A_max,T)      ## Import Data for NBCL5A
    #Data=lfd.ElDorado(A_max,T)    ## Import Data for El Dorado
    # Data=lfd.ShulKellA(A_max,T)   ## Import Data for Shulkell
    Data = lfd.Hardwicke(A_max, T)  ## Import Data for Hardwicke
    #Data1 = lfd1.Hardwicke(A_max, T)  ## Import Data for Hardwicke
    # Data=ld.Random50(A_max,T)     ## Import Data for random instance. Change the numbers among
    ## a) 50 b) 100 c) 200 d) 400 e) 900
    min_area = Data.A_min  ### - in same format
    nodes = Data.node_set  ### - in same format
    area = Data.area_set  ### - in same format



    cost = Data.get_costs(Data.name, ID) #cost
    for node in nodes:
        if node not in cost:
            cost[node] = 0
    neighbours = Data.adj  ### - in same format #neighbours fixing for rach node
    for i in neighbours.keys():
        for j in neighbours[i]:
            if i not in neighbours[j]:
                neighbours[j].append(i)

    verticess = Data.point_set  ### - in same format # fixing veticess for each vertix # each vertix has x and y 
    vertices = {}
    for i in verticess.keys():
        vertices[i] = []
        for vertex in verticess[i]:
            vertices[i].append((round(vertex[0],2), round(vertex[1],2)))
    centers = {}
    for i in vertices.keys():
        x = 0
        y = 0
        for j in vertices[i][:len(vertices[i]) - 1]:
            x += j[0]
            y += j[1]
        x = x / (len(vertices[i]) - 1)
        y = y / (len(vertices[i]) - 1)
        centers[i] = (x, y) # centers of each pitches

    maxx = 0
    distance = {}
    distt = {}
    for i in centers.keys():
        for j in centers.keys():
            distance[i, j] = ((centers[i][0] - centers[j][0]) ** 2 + (centers[i][1] - centers[j][1]) ** 2) ** 0.5 #DISTANCE of center of two nodes
    for i in nodes:
        distt[i] = {}
        for j in nodes:
            dis = []
            for k in vertices[j]:
                dis.append(((centers[i][0] - k[0]) ** 2 + (centers[i][1] - k[1]) ** 2) ** 0.5) #calculation distance of vector k of node j and center of node j
            distt[i][j] = max(dis)
            if maxx < distt[i][j]:
                maxx = distt[i][j] #upper bound of distance of a vertix and center of a node
                
    xlim = 325  ## 100 each for flg9a, (175,75) for hardwicke, (325,175) for el dorado
    ylim = 175

budget = bud_p * sum(list(cost.values()))
print("budget", budget)
if use_small_area:
    ax = 0
    bx = 325
    ay = 0
    by = 200
    area, cost, nodes, neighbours, vertices, centers = use_subset_for_landscape(nodes, vertices, neighbours, area, cost,
                                                                                centers, ax, bx, ay, by)
    min_area = area_p * sum(area.values())
    mi_area = are_p * sum(area.values())
    budget = bud_p * sum(list(cost.values()))
    budget_backup=budget
    min_area_backup=min_area
    print("budget", budget)
    xlim = bx  ## 100 each for flg9a, (175,75) for hardwicke, (430,80) for el dorado
    ylim = by
################################################################


# Data.plot_data(nodes)
x_bin1 = {}
for i in nodes:
    x_bin1[i] = {}
for j in nodes:
    for i in nodes:
        x_bin1[i][j] = "x" + str(i) + str(j)
## create variables names
x_bin = {}
for i in nodes:
    x_bin[i] = {}
for j in circ:
    for i in nodes:
        x_bin[i][j] = "x" + str(i) + str(j)
x_bin_warmstart = {}
for i in nodes:
    x_bin_warmstart[i] = {}
for j in circ:
    for i in nodes:
        x_bin_warmstart[i][j] = "x" + str(i) + str(j)
        
x_bin_max = {}
for i in nodes:
    x_bin_max[i] = {}
for j in circ:
    for i in nodes:
        x_bin_max[i][j] = "x" + str(i) + str(j)
        

k1 = {}
for i in circ:
    k1[i] = "k1" + str(i)
k2 = {}
for i in circ:
    k2[i] = "k2" + str(i)
k3 = {}
for i in circ:
    k3[i] = "k3" + str(i)
up = {}
for i in circ:
    up[i] = "u" + str(i)
Radius = "r"
X = "x"
Y = "y"
#####################################################################
def divide_array(arr, d):
    # Sort the array
    arr.sort()
    n = len(arr)
    
    # Calculate the size of each part. Some parts might be larger by one element if n is not divisible by d.
    part_size, extras = divmod(n, d)
    
    dividing_values = []
    index = 0
    
    for i in range(d):
        # Calculate the size of the current part
        current_part_size = part_size + (1 if i < extras else 0)
        
        # Move the index to the end of the current part
        index += current_part_size
        
        # Save the dividing value, which is the last element of the current part, except for the last part
        if i < d - 1:
            dividing_values.append(arr[index ])
    
    return dividing_values

x_vecices=[]
y_vecices=[]
x_vecices_backup=[]
y_vecices_backup=[]
for j in nodes:
    for k in vertices[j]:
        x_vecices.append(k[0])
        y_vecices.append(k[1])
        x_vecices_backup.append(k[0])
        y_vecices_backup.append(k[1])
x_vecices.sort()
y_vecices.sort()
n_vecices_size=0
n_vecices_size=len(y_vecices)
# given_x=5
# given_y=1


# _________________________________________________________________Smallest Enclosing circle______________________________________________________


INF = 1e18


# Structure to represent a 2D point
class Point:
    def __init__(self, X=0, Y=0) -> None:
        self.X = X
        self.Y = Y


# Structure to represent a 2D circle
class Circle:
    def __init__(self, c=Point(), r=0.0, A = Point(0,0), B = Point(0,0), C = Point(0,0)) -> None:
        self.C = c
        self.R = r
        self.P1 = A
        self.P2 = B
        self.P3 = C


# Function to return the euclidean distance
# between two points
def dist(a, b):
    return sqrt(pow(a.X - b.X, 2)
                + pow(a.Y - b.Y, 2))


# Function to check whether a point lies inside
# or on the boundaries of the circle
def is_inside(c, p):
    return dist(c.C, p) <= c.R


# The following two functions are used
# To find the equation of the circle when
# three points are given.

# Helper method to get a circle defined by 3 points
def get_circle_center(bx, by,
                      cx, cy):
    B = bx * bx + by * by
    C = cx * cx + cy * cy
    D = bx * cy - by * cx
    return Point((cy * B - by * C) / ((2 * D)+0.000000000001),
                 (bx * C - cx * B) / ((2 * D)+0.000000000001))


# Function to return the smallest circle
# that intersects 2 points
def circle_from1(A, B):
    # Set the center to be the midpoint of A and B
    C = Point((A.X + B.X) / 2.0, (A.Y + B.Y) / 2.0)

    # Set the radius to be half the distance AB
    return Circle(C, dist(A, B) / 2.0, Point(A.X, A.Y), Point(B.X, B.Y))


# Function to return a unique circle that
# intersects three points
def circle_from2(A, B, C):
    I = get_circle_center(B.X - A.X, B.Y - A.Y,
                          C.X - A.X, C.Y - A.Y)

    I.X += A.X
    I.Y += A.Y
    return Circle(I, dist(I, A), Point(A.X,A.Y), Point(B.X,B.Y), Point(C.X, C.Y))


# Function to check whether a circle
# encloses the given points
def is_valid_circle(c, P):
    # Iterating through all the points
    # to check whether the points
    # lie inside the circle or not
    for p in P:
        if (not is_inside(c, p)):
            return False
    return True


# Function to return the minimum enclosing
# circle for N <= 3
def min_circle_trivial(P):
    assert (len(P) <= 3)
    if not P:
        return Circle()

    elif (len(P) == 1):
        return Circle(P[0], 0)

    elif (len(P) == 2):
        return circle_from1(P[0], P[1])

    # To check if MEC can be determined
    # by 2 points only
    for i in range(3):
        for j in range(i + 1, 3):

            c = circle_from1(P[i], P[j])
            if (is_valid_circle(c, P)):
                return c

    return circle_from2(P[0], P[1], P[2])


# Returns the MEC using Welzl's algorithm
# Takes a set of input points P and a set R
# points on the circle boundary.
# n represents the number of points in P
# that are not yet processed.
def welzl_helper(P, R, n):
    # Base case when all points processed or |R| = 3
    if (n == 0 or len(R) == 3):
        return min_circle_trivial(R)

    # Pick a random point randomly
    idx = randint(0, n - 1)
    p = P[idx]
    boundry = []
    # Put the picked point at the end of P
    # since it's more efficient than
    # deleting from the middle of the vector
    P[idx], P[n - 1] = P[n - 1], P[idx]

    # Get the MEC circle d from the
    # set of points P - :p
    d = welzl_helper(P, R.copy(), n - 1)

    # If d contains p, return d
    if (is_inside(d, p)):
        return d

    # Otherwise, must be on the boundary of the MEC
    else:
        R.append(p)

    # Return the MEC for P - :p and R U :p
    return welzl_helper(P, R.copy(), n - 1)


def welzl(P):
    P_copy = P.copy()
    shuffle(P_copy)
    return welzl_helper(P_copy, [], len(P_copy))


############################################################################
vv_distance=10000000

max_distance={}
sys.setrecursionlimit(50000)

for i in nodes:
    for j in nodes:
        max_distance[i, j] = 0
        

if len(nodes)==1363: # checking if landscape is eldorado use prepared max dsistance to save time
    with open('output/max_distance_eldorado.txt', 'r') as f:
        max_distance_str_keys = json.load(f)
    max_distance = {ast.literal_eval(k): v for k, v in max_distance_str_keys.items()}
else:
    for i in nodes:
        for j in nodes:
            for vertex_i in vertices[i]:
                for vertex_j in vertices[j]:
                    vv_distance = ((vertex_i[0] - vertex_j[0]) ** 2 + (vertex_i[1] - vertex_j[1]) ** 2) ** 0.5
                    if vv_distance >max_distance[i, j]:
                         max_distance[i, j]=vv_distance

#########################################################################

# Compute the convex hull vertices of each patch.

convex_hull_arr = []  # Holds the NumPy arrays of points for each node
for i in nodes:
    temp_list = vertices[i]  # Directly using vertices[i] assuming it's in the correct format
    convex_hull_arr.append(np.array(temp_list))

hull_vertices = []  # To store vertices of the convex hull for each set
points_outside_hull_dict = {}  # To store points not in the convex hull for each set, keyed by node

for index, points in enumerate(convex_hull_arr):
    node = nodes[index]  # Get the corresponding node value
    hull = ConvexHull(points)
    hull_points = points[hull.vertices]
    hull_vertices.append(hull_points)
    
    # Determine points not in the hull
    outside_hull = np.array([point for point in points if point.tolist() not in hull_points.tolist()])
    points_outside_hull_dict[node] = outside_hull  # Use node as key


for i in nodes:
    # Convert the NumPy array to a list of tuples for comparison
    outside_points_list = [tuple(point) for point in points_outside_hull_dict[i]]
    
            
transformed_dict = {}
for key, value in points_outside_hull_dict.items():
    transformed_dict[key] = [(float(x), float(y)) for x, y in value]

def get_patches(z, adj):
    patch = []
    in_list = {}

    for i in z:
        in_list[i] = False

    for i in z:
        if in_list[i]:
            continue

        s = [i]
        l = []
        in_list[i] = True

        while len(s) > 0:
            j = s.pop()

            l.append(j)

            for k in adj[j]:
                if k in in_list and in_list[k] == False:
                    in_list[k] = True
                    s.append(k)

        patch.append(l)

    return patch

    


#####################################################################################

def dijkstra(G, start, end=None):
    start = str(start)

    inf = float('inf')
    D = {start: 0}  # mapping of nodes to their dist from start
    Q = PQDict(D)  # priority queue for tracking min shortest path
    P = {}  # mapping of nodes to their direct predecessors
    U = set(G.keys())  # unexplored nodes

    while U:  # nodes yet to explore
        (v, d) = Q.popitem()  # node w/ min dist d on frontier
        D[v] = d  # est dijkstra greedy score
        U.remove(v)  # remove from unexplored
        if v == end: break

        # now consider the edges from v with an unexplored head -
        # we may need to update the dist of unexplored successors
        for w in G[v]:  # successors to v
            if w in U:  # then w is a frontier node
                d = D[v] + G[v][w]  # dgs: dist of start -> v -> w
                if d < Q.get(w, inf):
                    Q[w] = d  # set/update dgs
                    P[w] = v  # set/update predecessor

    return D, P


def shortest_path(G, start, end):
    dist, pred = dijkstra(G, start, end)
    v = end
    path = [v]
    while v != start:
        v = pred[v]
        path.append(v)
    path.reverse()
    return path


def make_graph(filename):
    G = {}

    with open(filename) as file:
        for row in file:
            r = row.strip().split('\t')
            label = r.pop(0)
            neighbors = {v: int(length) for v, length in [e.split(',') for e in r]}
            G[label] = neighbors

    return G

################################################################

incr=0
incr=0
def mycallback(problem, where):
    def neighbourhood( z, adj):  # neighbourhood of the connected reserves
        S = set()
        for i in z:
            for j in adj[i]:
                S.add(j)
        return list(S - set(z))

    def get_patches( z, adj):  #connected components (multi reserve)
        patch = []
        in_list = {}

        for i in z:
            in_list[i] = False
        for i in z:
            s = []
            l = []
            if in_list[i] == True:
                continue
            else:
                s.append(i)
                in_list[i] = True
                while len(s) > 0:
                    for j in s:
                        for k in adj[j]:
                            if (k in z) and (in_list[k] == False):
                                in_list[k] = True
                                s.append(k)
                        l.append(j)
                        s.remove(j)
            patch.append(l)
        return patch

    def patch_areas( patch, area_set):  # area of the reserves
        area = {}
        for i, j in enumerate(patch):
            a = 0
            for k in j:
                a += area_set[k]

            area[i] = a
        return area
    ##################################################################
    
    if where == GRB.Callback.MIPSOL:
        incumbent = problem.cbGet(gp.GRB.Callback.MIPSOL_OBJ)
        
        Trig = 0
        global x_inc_v
        global w_inc_v
        global max_R_tilda
        ccc = 1
        selected = {}
        x = {}
        y = {}
        RR = {}
        zz_val = incumbent

        for j in circ:
            for i in nodes:
                x_inc_v[i, j] = round(problem.cbGetSolution(x_bin[i, j]))
                w_inc_v[i, j] = problem.cbGetSolution(w[i, j])
        for k in circ:
            k1_val = problem.cbGetSolution(k1[k])
            k2_val = problem.cbGetSolution(k2[k])
            k3_val = problem.cbGetSolution(k3[k])
            
            u_val = problem.cbGetSolution(up[k])
            ask = {}
            for i in nodes:
                for ind, j in enumerate(vertices[i][:len(vertices[i]) - 1]):
                    ask[i, ind] = ((u_val * j[0] - k1_val) ** 2 + (u_val * j[1] - k2_val) ** 2) ** 0.5

            x_bin_dic = {}
            for i in nodes:
                x_bin_dic[i] = {}
                x_bin_dic[i][k] = round(problem.cbGetSolution(x_bin[i, k]))
            RR[k] = k3_val / (u_val - 1e-30)
            x[k] = k1_val / (u_val + 1e-30)
            y[k] = k2_val / (u_val + 1e-30)
            
#################################ploting part########################################
        selected = {}
        semi = []
        compact = {}
        for j in circ:
            selected[j] = []
            for i in nodes:
                if x_inc_v[(i, j)] == 1:
                    selected[j].append(i)
                if x_inc_v[(i, j)] == 0:
                    semi.append(i)

        if use_random_data:
            plot_solution_new(centers, width, selected, RR[j], (x[j], y[j]), cost)
        else:
            pass

        total_cost = 0
        total_area = {}
        for l in circ:
            total_area[l] = 0
        for j in circ:
            for i in nodes:
                if x_inc_v[(i, j)] == 1:
                    total_cost += cost[i]
                    total_area[j] += area[i]
            compact[j] = total_area[j] / ((math.pi * RR[j] * RR[j]) + 1e-20)
        tot_compact = 0
        for i in circ:
            tot_compact += compact[i]

        counter = True
        pa_ar = {}
        for j in circ:
            for i in range(len(selected[j])):
                pa_ar[selected[j][i]] = area[selected[j][i]]

#################################cuts####################################

            
        hole_cut= False
        conectivity_cut=False
        circle_cut1= False
        circle_cut2= False
        for k in circ:
            if RR[k] > 0:
                expr = gp.LinExpr()
                if 2 * math.pi * RR[k] * k3_val - math.pi * (RR[k] ** 2) * u_val > 1 + u_val * dtol  and use_obj_cuts:
                    
                    
                    expr = ( 2 * math.pi * RR[k] * k3[k] - math.pi * (RR[k] ** 2) * up[k])

                    problem.cbLazy(expr <= 1)# Adding objective cut
                    circle_cut1 = True

            lets = True
            M = max(xlim, ylim)
            for i in target_nodes:
                if x_bin_dic[i][k]==1:
                    for ind, j in enumerate(vertices[i][:len(vertices[i]) - 1]):
                        expr1 = gp.LinExpr()
                        expr2 = gp.LinExpr()
                        if j not in transformed_dict[i]:
                            if ask[i, ind] > k3_val + u_val *dtol:
                                lets = False
                                xt = k1_val - j[0] * u_val
                                yt = k2_val - j[1] * u_val
                                u1t = xt / ask[i, ind]
                                u2t = yt / ask[i, ind]
                                
                                m_corner=0
                                corner1=math.sqrt((final_period_arr_x[final_period_counter_x]-j[0])**2+(final_period_arr_y[final_period_counter_y]-j[1])**2)
                                corner2=math.sqrt((final_period_arr_x[final_period_counter_x+1]-j[0])**2+(final_period_arr_y[final_period_counter_y]-j[1])**2)
                                corner3=math.sqrt((final_period_arr_x[final_period_counter_x]-j[0])**2+(final_period_arr_y[final_period_counter_y+1]-j[1])**2)
                                corner4=math.sqrt((final_period_arr_x[final_period_counter_x+1]-j[0])**2+(final_period_arr_y[final_period_counter_y+1]-j[1])**2)
                                if m_corner< max(corner1, corner2, corner3, corner4):
                                    m_corner = max(corner1, corner2, corner3, corner4)
                                
                                M=m_corner -((min_area/round(math.pi,3))**(1/2)) 
                                
                                if u1t *  k1_val + u2t * k2_val + M * w_inc_v[i, k] - k3_val - (M + j[0] * u1t + j[1] * u2t) * u_val>0:
    
                                    expr1 = u1t * k1[k] + u2t * k2[k] + M * w[i, k] - k3[k] - (M + j[0] * u1t + j[1] * u2t) * up[k]
                                    problem.cbLazy(expr1 <= 0)  # Adding constraint
                                    
                                if -u1t * k1_val - u2t * k2_val + M * w_inc_v[i, k] - k3_val - (M - j[0] * u1t - j[1] * u2t) * u_val>0:
                                    expr2 = -u1t * k1[k] - u2t * k2[k] + M * w[i, k] - k3[k] - (M - j[0] * u1t - j[1] * u2t) * up[k]
                                    problem.cbLazy(expr2 <= 0)  # Adding constraint fixing cornesers be inside the circle
    
                                

                                circle_cut2= True

            ######################################################################
            comp = False
            selected[k] = []
            for i in target_nodes:
                if x_bin_dic[i][k] == 1:
                    selected[k].append(i)
            patches = get_patches(selected[k], neighbours)
            if True:
                if len(patches) > 1:
                    s = []
                    area_set = patch_areas(patches, area)
                    for i in range(len(patches)):
                        if True:  
                            neigh = neighbourhood(patches[i], neighbours)
                            if neigh != []:
                                comp = True
                                expr = gp.LinExpr()
                                for j in patches[i]:
                                    expr += x_bin[j, k]  # Add terms with coefficient 1 for each j in patches[i]
                                for j in neigh:
                                    expr -= x_bin[j, k]  # Add terms with coefficient -1 for each j in neigh
                                rhs = len(patches[i]) - 1
                                problem.cbLazy(expr <= rhs) #connectivity cut
                                conectivity_cut= True

            if True: 
                if len(patches)==1 and use_hole_callback: ### there is only one patch
                    nod=list(set(nodes).difference(set(selected[k])))
                    g=Graph(len(nodes),nodes)
                    for i in nod:
                        for j in neighbours[i]:
                            if j in nod:
                                g.addEdge(i, j)
                    cc = g.connectedComponents()
                    pholes=[] ## list of potential holes
                    for i in cc:
                        tval=True
                        for j in i:
                            if x_bin_dic[j][k]==0 and tval:
                                pholes.append(i)
                                tval=False

                    holes = []
                    for o in pholes:
                        flag = True
                        for l in o:
                            for m in vertices[l]:
                                if ((m[0]-x[k])**2+(m[1]-y[k])**2)**0.5>RR[k]:
                                    flag = False
                                    break
                            if not flag:
                                break
                        if flag:
                            holes.append(o)

                    if holes==[]:
                        pass
                    else:
                        for hole_component in holes:
                            nei = neighbourhood(hole_component, neighbours)
                            for j in hole_component:
                                expr = gp.LinExpr()
                                for i in nei:
                                    expr += x_bin[i, k]
                                expr -= x_bin[j, k]
                                problem.cbLazy(expr <= len(nei) - 1) # hole cut
                            hole_cut = True



            ###############################################################################
def find_neighbors_and_vectors(coordinates, target_coordinate):
    n = len(coordinates)
    if target_coordinate not in coordinates:
        return None, None, None, None, None  # Target coordinate not found

    target_index = coordinates.index(target_coordinate)

    # Coordinate before the target coordinate
    previous_coordinate_index = (target_index - 1) % n

    # Coordinate after the target coordinate
    next_coordinate_index = (target_index + 1) % n

    previous_coordinate = coordinates[previous_coordinate_index]
    current_coordinate = coordinates[target_index]
    next_coordinate = coordinates[next_coordinate_index]

    # Vectors from current to previous and next coordinates
    vector_to_previous = (-current_coordinate[0] + previous_coordinate[0], -current_coordinate[1] + previous_coordinate[1])
    vector_to_next = (-current_coordinate[0] + next_coordinate[0], -current_coordinate[1] + next_coordinate[1])

    return previous_coordinate, current_coordinate, next_coordinate, vector_to_previous, vector_to_next

def rotate_vector_90_deg_toward(v, u):
                              
    vx, vy = v
    # Calculate the two perpendicular vectors
    v_perp_ccw = np.array([-vy, vx])  # Counterclockwise perpendicular
    v_perp_cw = np.array([vy, -vx])   # Clockwise perpendicular

    # Calculate dot products with target vector u
    dot_ccw = np.dot(v_perp_ccw, u)
    dot_cw = np.dot(v_perp_cw, u)

    # Choose the perpendicular vector that has a positive dot product with u
    if dot_ccw > dot_cw:
        return v_perp_ccw
    else:
        return v_perp_cw
        
def angle_with_x_axis(v):
                               
    return np.arctan2(v[1], v[0])

def find_extreme_rays(vectors):

    # Normalize vectors to get only direction
    normalized_vectors = [v / np.linalg.norm(v) for v in vectors]

    # Sort vectors by their angle with the x-axis
    sorted_vectors = sorted(normalized_vectors, key=angle_with_x_axis)

    # The extreme rays are the first and last vectors in the sorted list
    min_ray = sorted_vectors[0]
    max_ray = sorted_vectors[-1]

    return min_ray, max_ray

def angle_with_x_axis(v):
  
    return np.arctan2(v[1], v[0])

def normalize_vector(v):

    return v / np.linalg.norm(v)

def find_cone_intersection(extreme_rays1, extreme_rays2):

    # Normalize and calculate angles for the extreme rays
    rays1 = [normalize_vector(r) for r in extreme_rays1]
    rays2 = [normalize_vector(r) for r in extreme_rays2]

    angles1 = sorted([angle_with_x_axis(r) for r in rays1])
    angles2 = sorted([angle_with_x_axis(r) for r in rays2])

    # Find the overlapping interval of angles
    min_angle = max(angles1[0], angles2[0])
    max_angle = min(angles1[1], angles2[1])

    # Check if there is an intersection
    if min_angle > max_angle:
        return None  # No intersection

    # Convert the angles back to vectors
    min_ray = np.array([np.cos(min_angle), np.sin(min_angle)])
    max_ray = np.array([np.cos(max_angle), np.sin(max_angle)])

    return min_ray, max_ray


def normalize(v):
    """ Normalize a 2D vector """
    norm = np.linalg.norm(v)
    return v / norm

def interpolate_rays(ray1, ray2, num_divisions):
    """ Interpolate between two rays and generate middle rays """
    # Ensure rays are normalized
    ray1 = normalize(ray1)
    ray2 = normalize(ray2)

    # Calculate the angle between the two rays
    dot_product = np.dot(ray1, ray2)
    angle = np.arccos(dot_product)

    # Generate middle rays
    middle_rays = []
    for i in range(1, num_divisions):
        # Calculate the interpolation factor
        t = i / num_divisions

        # Calculate the rotation angle for this factor
        theta = t * angle

        # Rotation matrix for the angle
        rotation_matrix = np.array([
            [np.cos(theta), -np.sin(theta)],
            [np.sin(theta), np.cos(theta)]
        ])

        # Generate the new ray and append to the list
        new_ray = np.dot(rotation_matrix, ray1)
        middle_rays.append(new_ray)

    return middle_rays

        
    ######################################################################
    ######################################################################
best_radius={}
best_selected=[]
best_objective=0
best_real_ratio=0
best_x={}
best_y={}
final_period_arr_x=[]
final_period_arr_y=[]
boom_counter=0

given_x=1
given_y=1
number_of_dot_cut=2 #best choises :  flg9a= 2 eldorado =3, hardwick =2 

if given_x>= 1:
    final_period_arr_x=[round(num) for num in divide_array(x_vecices, given_x)]
    final_period_arr_x.insert(0, ax)
    final_period_arr_x.append(bx)
if  given_y>=1:
    final_period_arr_y=[round(num) for num in divide_array(y_vecices, given_y)]  
    final_period_arr_y.insert(0, ay)
    final_period_arr_y.append(by)


best_result=0
final_period_counter_x=0
final_period_counter_y=0
################################################################
while given_x>final_period_counter_x:
    while given_y>final_period_counter_y:
        try:
            problem = gp.Model("mip")
            problem.setParam('OutputFlag', 1) 
            problem.ModelSense = GRB.MAXIMIZE
            problem.setParam('TimeLimit', 3600)

            
            for i in circ:
                k3[i] = problem.addVar(lb=0.0, ub=1, vtype=GRB.CONTINUOUS, name="k3_" + str(i))
                up[i] = problem.addVar(lb=0, ub=1 / mi_area, vtype=GRB.CONTINUOUS, name="up_" + str(i))
                k1[i] = problem.addVar(lb=0.0, ub=xlim, vtype=GRB.CONTINUOUS, name="k1_" + str(i))
                k2[i] = problem.addVar(lb=0.0, ub=ylim, vtype=GRB.CONTINUOUS, name="k2_" + str(i))

            for j in circ:
                for i in nodes:
                    x_bin[i, j] = problem.addVar(lb=0, ub=1, vtype=GRB.BINARY, name="x_bin_" + str(i) + "_" + str(j))
                    w[i, j] = problem.addVar(lb=0, ub=1 / mi_area, vtype=GRB.CONTINUOUS, name="w_" + str(i) + "_" + str(j))

            z_ratio = problem.addVar(lb=0, ub=1, vtype=GRB.CONTINUOUS, name="z_PROBLEM")

            problem.update()  # Update the model to include the new variables

            
            # max_R_tilda = (alfa_tilda / (max(best_z_ratio,best_result)*round(math.pi, 3)))**0.5  # Square root operation
            
            # max_R_tilda_local=max_R_tilda
            ################################################################################
            target_nodes=[]
            target_nodes_counter=0
            new_targetpoint_counter=0
            curent_targetpoint_counter=0
            target_nodes=nodes
            # if True:
            #     for i in nodes:
            #         target_nodes_counter=0
            #         for k in range(len(vertices[i])):
            #             if vertices[i][k][0]<= final_period_arr_x[final_period_counter_x]-max_R_tilda_local or vertices[i][k][0]>= final_period_arr_x[final_period_counter_x+1]+max_R_tilda_local or vertices[i][k][1]<= final_period_arr_y[final_period_counter_y]-max_R_tilda_local or vertices[i][k][1]>= final_period_arr_y[final_period_counter_y+1]+max_R_tilda_local : 
            #                 target_nodes_counter=target_nodes_counter+1
            #         if target_nodes_counter==0:
            #             target_nodes.append(i)

            current_targetpoint_counter=len(target_nodes)
        ################################################################################################################
            for i in nodes:
                if i  not in target_nodes:
                    problem.addConstr(x_bin[i, 1] == 0, name="out of area")
                    #print(i)
            #############################################################################
            #max_R_for_big_m=(alfa_tilda / (max(best_z_ratio,best_result)*round(math.pi, 3)))**0.5 
            big_m2=math.sqrt((final_period_arr_x[final_period_counter_x+1]-final_period_arr_x[final_period_counter_x])**2+( final_period_arr_y[final_period_counter_y+1]-final_period_arr_y[final_period_counter_y])**2)
            big_m1=math.sqrt(xlim**2+ ylim**2)-((min_area/round(math.pi,3))**(1/2))
            min_R_hat=(min_area/round(math.pi,3))**(1/2)
            M = min(big_m1, big_m2)#-((min_area/round(math.pi,3))**(1/2))
            for k in circ:
                for i in target_nodes:
                    m_corner=0
                    for j in vertices[i][:len(vertices[i]) - 1]:
                        if j not in transformed_dict[i]:
                            m_corner=0
                            corner1=math.sqrt((final_period_arr_x[final_period_counter_x]-j[0])**2+(final_period_arr_y[final_period_counter_y]-j[1])**2)
                            corner2=math.sqrt((final_period_arr_x[final_period_counter_x+1]-j[0])**2+(final_period_arr_y[final_period_counter_y]-j[1])**2)
                            corner3=math.sqrt((final_period_arr_x[final_period_counter_x]-j[0])**2+(final_period_arr_y[final_period_counter_y+1]-j[1])**2)
                            corner4=math.sqrt((final_period_arr_x[final_period_counter_x+1]-j[0])**2+(final_period_arr_y[final_period_counter_y+1]-j[1])**2)
                            if m_corner< max(corner1, corner2, corner3, corner4):
                                m_corner = max(corner1, corner2, corner3, corner4)
                            M= m_corner-((min_area/round(math.pi,3))**(1/2))#+max_R_tilda
######################################################################################################
                            coordinates = vertices[i][:len(vertices[i]) - 1]
                            target_coordinate = j
                            previous_coordinate, current_coordinate, next_coordinate, vector_to_previous, vector_to_next = find_neighbors_and_vectors(coordinates, target_coordinate)
                            v = np.array(vector_to_next)
                            u = np.array(vector_to_previous)

                            rey1cone1 = rotate_vector_90_deg_toward(v, u)
                            rey2cone1 = rotate_vector_90_deg_toward(u, v)

                            vectors_to_core_corner = [
                                np.array([-j[0]+final_period_arr_x[final_period_counter_x], -j[1]+final_period_arr_y[final_period_counter_y]]),
                                np.array([-j[0]+final_period_arr_x[final_period_counter_x], -j[1]+final_period_arr_y[final_period_counter_y+1]]),
                                np.array([-j[0]+final_period_arr_x[final_period_counter_x+1], -j[1]+final_period_arr_y[final_period_counter_y]]),
                                np.array([-j[0]+final_period_arr_x[final_period_counter_x+1], -j[1]+final_period_arr_y[final_period_counter_y+1]])
                            ]

                            rey1cone2, rey2cone2 = find_extreme_rays(vectors_to_core_corner)
                            if j[0]<=final_period_arr_x[final_period_counter_x+1] and j[0]>=final_period_arr_x[final_period_counter_x] and j[1]<=final_period_arr_y[final_period_counter_y+1] and j[1]>=final_period_arr_y[final_period_counter_y] :
                                rey1cone2=rey1cone1
                                rey2cone2=rey2cone1
                            
                            extreme_rays_cone1 = (np.array(rey1cone1), np.array(rey2cone1))
                            extreme_rays_cone2 = (np.array(rey1cone2), np.array(rey2cone2))

                            intersection_rays = find_cone_intersection(extreme_rays_cone1, extreme_rays_cone2)

                            if intersection_rays and M>=0:

 
                                intersection_rays = [intersection_rays[0], intersection_rays[1]]
                                new_rays = interpolate_rays(intersection_rays[0], intersection_rays[1], number_of_dot_cut)
                                if corner1 >= min_R_hat or corner2 >= min_R_hat or corner3 >= min_R_hat or corner4 >= min_R_hat :
                                    for idx, ray in enumerate(new_rays):
    
                                        expr = gp.LinExpr()
                                        expr = ray[0] * k1[1] + ray[1] * k2[1] + (-j[0] *ray[0] - j[1] * ray[1] - M) * up[1] + M * w[i, 1] - k3[1]
######################################################################################################

                            for u in U:
                                if u1[u] * centers[i][0] + u2[u] * centers[i][1] + (-j[0] * u1[u] - j[1] * u2[u] ) >0:
                                    expr = gp.LinExpr()
                                    expr += u1[u] * k1[k] + u2[u] * k2[k] + (-j[0] * u1[u] - j[1] * u2[u] - M) * up[k] + M * w[i, k] - k3[k]
                                    problem.addConstr(expr <= 0, name="radius constraint25 " + str(i) + "," + str(j) + "," + str(u) + "," + str(k))
                                if u1[u] * centers[i][0] + u2[u] * centers[i][1] + (-j[0] * u1[u] - j[1] * u2[u] ) <0:

                                    expr = gp.LinExpr()
                                    expr +=-u1[u] * k1[k] - u2[u] * k2[k]  - (M - j[0] * u1[u] - j[1] * u2[u]) * up[k]   + M * w[i, k] - k3[k]
                                    problem.addConstr(expr <= 0, name="radius constraint52 " + str(i) + "," + str(j) + "," + str(u) + "," + str(k))

            for j in circ:
                expr = gp.LinExpr()
                expr += z_ratio  
                for i in target_nodes:
                    expr -= area[i] * w[i, j] 
                problem.addConstr(expr <= 0, name="z_con" + str(j))
            for j in circ:
                expr = gp.LinExpr()
                for i in target_nodes:
                    expr += area[i] * x_bin[i, j]  
                problem.addConstr(expr >= min_area, name="area")  


            for j in circ:
                expr = gp.LinExpr()
                for i in target_nodes:
                    expr += cost[i] * x_bin[i, j]  
                problem.addConstr(expr <= budget, name="Budget")  
            def add_obj_cutting_planes1(problem, nop, min_R):
                r0 = {}
                for k in circ:
                    r0[k] = np.linspace(min_R, max(xlim, ylim), nop)
                    PI = round(math.pi, 8)
                    expr = gp.LinExpr()
                    for i in r0[k]:
                        expr = 2 * PI * i * k3[k] - PI * i * i * up[k]
                        problem.addConstr(expr <= 1, name="objective_cut_" + str(i) + str(k)) #validated 3.13


            def add_linearization_constraints1(problem):
                M = round(1 / min_area, 8)
                for j in circ:
                    for i in target_nodes:
                        problem.addConstr(w[i, j] - M * x_bin[i, j] <= 0, name="auxiliary1_" + str(i) + str(j))  
                        problem.addConstr(w[i, j] - up[j] <= 0, name="auxiliary2_" + str(i) + str(j))  
                        problem.addConstr(w[i, j] - M * x_bin[i, j] - up[j] >= -M, name="auxiliary3_" + str(i) + str(j))  

            min_R = round((min_area / math.pi) ** 0.5, 3)

            def wasta01(inst, nodes):
                nv = []
                nval = []
                k = 0
                for i in onal:
                    for j in onal[i]:
                        nv.append(x_bin[j][k + 1])
                        nval.append(1)
                    k += 1
                for l in circ:
                    for i in nodes:
                        if x_bin[i][l] not in nv:
                            nv.append(x_bin[i][l])
                            nval.append(0)
                nv1, nval1 = CCP_onal_veri(nv, nval)
                if nv != False:
                    inst.MIP_starts.add([nv1, nval1], prob.MIP_starts.effort_level.no_check, "Warmstart1")
      
            ##############################################################
            if use_species:
                add_speciation_constraints1(prob, ax, bx, ay, by) 

            add_linearization_constraints1(problem)

            use_inc = True

            if use_obj_cuts:
                add_obj_cutting_planes1(problem, 50, min_R) 

            problem._vars = x_bin
            problem.setObjective(z_ratio, GRB.MAXIMIZE)

            t1=time.time()
            problem.Params.LazyConstraints = 1
            problem.optimize(mycallback)
            t2=time.time()
            print("Time Elapsed : ", round(t2 - t1, 4))
            hourtimelimit=hourtimelimit+round(t2 - t1, 4)
            if hourtimelimit>=7200:
                print ("end of 7200 sec with best solution of",best_result)

            file3 = "Resl2.lp"
            problem.write(file3)
            


            if problem.SolCount > 0 and problem.Status in (GRB.OPTIMAL,GRB.TIME_LIMIT,GRB.SUBOPTIMAL):

                x = {}
                y = {}
                radius = {}
                total_area = {}
                selected = {}
                for k in circ:
                    selected[k] = []
                    semi = []
                    dam = []
                    for i in nodes:
                        count = x_bin[i, k].X  
                        if round(count) > 0:
                            selected[k].append(i)
                        if count > 0 and count < 1:
                            semi.append(i)

                    total_area[k] = 0
                    total_cost = 0
                    for i in selected[k]:
                        total_area[k] += area[i]
                        total_cost += cost[i]
                    k1c = k1[k].X  # Accessing the value of the variable in Gurobi
                    k2c = k2[k].X
                    k3c = k3[k].X
                    ucc = up[k].X
                    Wc = {}

                    objective = problem.ObjVal  

                    radius[k] = k3c / (ucc + 1e-20)
                    x[k] = k1c / (ucc + 1e-20)
                    y[k] = k2c / (ucc + 1e-20)

                if use_random_data:
                    plot_solution_new(centers, width, selected, radius, (x, y), cost)
                else:
                    Data.plot_soln_data(selected, dam, "NEW", nodes, (x, y), radius)
                for k in circ:
                    compact = total_area[k] / (round(math.pi, 8) * radius[k] * radius[k] + 1e-20)
                    print("Objective value:", objective)
                    print("Selected patches:", selected)
                    print("Reock score:", compact)
                    print("Enclosing-circle radius:", radius[k])

                filename = "Instance_results.xlsx"
##############################################
                l = 1
                points = {}
                for i in circ:
                    points[l] = []
                    for j in selected[i]:
                        for k in vertices[j]:
                            if (Point(k[0],k[1]) not in points[l]):
                                points[l].append(Point(k[0], k[1]))
                    l += 1
                

                circ_data = {}
                for i in points:
                    circ_data[i] = welzl(points[i])
                
                rr_warmstart=0
                xx_warmstart=0
                yy_warmstart=0
                for i in circ_data:
                
                    rr_warmstart = circ_data[i].R
                    xx_warmstart=circ_data[i].C.X
                    yy_warmstart=circ_data[i].C.Y
                area_of_selected_for_partition=0
                for i in selected[i]:
                    area_of_selected_for_partition=area_of_selected_for_partition+ area[i]

                l = 1
                points = {}
                for i in circ:
                    points[l] = []
                    for j in selected[i]:
                        for k in vertices[j]:
                            if (Point(k[0],k[1]) not in points[l]):
                                points[l].append(Point(k[0], k[1]))
                    l += 1
                

                circ_data = {}
                for i in points:
                    circ_data[i] = welzl(points[i])
                
                rr_warmstart=0
                xx_warmstart=0
                yy_warmstart=0
                for i in circ_data:
                
                    rr_warmstart = circ_data[i].R
                    xx_warmstart=circ_data[i].C.X
                    yy_warmstart=circ_data[i].C.Y
                area_of_selected_for_partition=0
                for i in selected[i]:
                    area_of_selected_for_partition=area_of_selected_for_partition+ area[i]
                    
                if best_result<(total_area[1]/(rr_warmstart*rr_warmstart* math.pi)) and (total_area[1]/(rr_warmstart*rr_warmstart* math.pi)) < objective:
                    best_result=(total_area[1]/(rr_warmstart*rr_warmstart* math.pi))
                    best_objective=objective
                    best_selected=selected
                    best_radius=radius
                    best_x=x
                    best_y=y
                    print("best result", best_result)
                    
        except gp.GurobiError as e:
            print(e)
            
        boom_counter=boom_counter+1
        print("end of subproblem",boom_counter)
        final_period_counter_y=final_period_counter_y+1
        
    final_period_counter_y=0
    final_period_counter_x=final_period_counter_x+1
Data.plot_soln_data(best_selected, dam, "NEW", nodes, (best_x, best_y), best_radius)
print("Objective value:", best_objective)
print("Selected patches:", best_selected)
print("Enclosing-circle radius:", best_radius)
end_time = time.time()
print(end_time- start_time)