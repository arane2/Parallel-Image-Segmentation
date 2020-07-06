import numpy as np
from mpi4py import MPI
import time
import random
import math


def ugen(n):
    u = []
    for i in range(n):
        r,g,b = random.randint(0,255),random.randint(0,255),random.randint(0,255)
        u.append([r,g,b])
    print()
    print(u)
    print()
    print()
    return u


def clusteringpluscentroids(points, centroids, n):
    listrgb = [[] for zxc in range(n)]
    for point in points:
        dists = []
        for centroid in centroids:
            dist = (centroid[0] - point[0])**2 + (centroid[1] - point[1])**2 + (centroid[2] - point[2])**2 
            dist = math.sqrt(dist)
            dists.append(dist)
        mindist = min(dists)
        listrgb[dists.index(mindist)].append(point)
    centroids = []
    
    for listx in listrgb:
        x,y,z = 0,0,0
        for point in listx:
            x = x + point[0]
            y = y + point[1]
            z = z + point[2]
        
        centroids.append([x,y,z,len(listx)])
    return centroids


comm = MPI.COMM_WORLD
rank = comm.Get_rank()

np = 32

f = open("input_" + str(rank) + ".txt","r")

r = f.readlines()

values = r[0].split()

points = []
for x in range(int(len(values)/3)):
    points.append([int(values[x*3]),int(values[x*3+1]),int(values[x*3+2])])
print(len(points))


n = 3
centroids = []

if rank == 0:
    stt = time.time()
    centroids = ugen(n)

for iteration in range(20):
    centroids = comm.bcast(centroids, root = 0)


    centroids = clusteringpluscentroids(points, centroids, n)

    if(rank != 0):
        req = comm.isend(centroids, dest = 0, tag = rank)
        req.wait()

    if(rank == 0):
        size_list = []
        for z in range(len(centroids)):
            size_list.append(centroids[z][3])

            
        for x in range(1, np):
            req = comm.irecv(source = x, tag = x)
            recvd_c = req.wait()
            
            for y in range(len(centroids)):
                centroids[y][0] += recvd_c[y][0]
                centroids[y][1] += recvd_c[y][1]
                centroids[y][2] += recvd_c[y][2]
                size_list[y] += recvd_c[y][3]

        for x in range(len(centroids)):
            centroids[x][0] = centroids[x][0]/(size_list[x]+1)
            centroids[x][1] = centroids[x][1]/(size_list[x]+1)
            centroids[x][2] = centroids[x][2]/(size_list[x]+1)

if rank == 0:
    print(centroids)
    print(size_list)
    print(time.time()-stt)
