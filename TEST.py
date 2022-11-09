import numpy as np
from gurobipy import Model, GRB, quicksum
import matplotlib.pyplot as plt
import json

passengers_json = json.load(open('passengers1.json'))
drivers_json = json.load(open('drivers1.json'))
rnd=np.random
rnd.seed(0)

nr_passengers = len(passengers_json)
nr_drivers = len(drivers_json)

'''Coordinates '''
xc = []
yc = []

def add_coordinates():
        """Add coordinates"""
        for drivers in drivers_json:
                xc.append(drivers_json[drivers]['origin_xc'])
                yc.append(drivers_json[drivers]['origin_yc'])
        for passengers in passengers_json:
                xc.append(passengers_json[passengers]['origin_xc'])
                yc.append(passengers_json[passengers]['origin_yc'])
        for passengers in passengers_json:
                xc.append(passengers_json[passengers]['destination_xc'])
                yc.append(passengers_json[passengers]['destination_yc'])
        for drivers in drivers_json:
                xc.append(drivers_json[drivers]['destination_xc'])
                yc.append(drivers_json[drivers]['destination_yc'])
add_coordinates()

'''Sets'''

D = [i for i in range(nr_drivers)]
N = [i for i in range(nr_passengers*2+nr_drivers*2)]
NP = N[int(len(D)):int(len(N)/2)]
ND = N[int(len(N)/2):-int(len(D))]


#ny
A = [(i, j) for i in N for j in N if i!=j]


#gammel
N_k = N
A_k = [(i, j) for i in N_k for j in N_k if i!=j]


'''Parameters'''
o_k = {}
d_k = {}
T_k = {}
T_ij = {(i,j): np.hypot(xc[i]-xc[j], yc[i] - yc[j]) for i,j in A}
Q_k = {}
A_k1 = {}
A_k2 = {}
M = 1200


def add_parameters():
    """Add parameters"""
    for drivers in drivers_json:
        o_k[drivers_json[drivers]['id']] = drivers_json[drivers]['id']
        d_k[drivers_json[drivers]['id']] = drivers_json[drivers]['id'] + nr_passengers * 2 + nr_drivers
        T_k[drivers_json[drivers]['id']] = drivers_json[drivers]['max_ride_time']
        Q_k[drivers_json[drivers]['id']] = drivers_json[drivers]['max_capacity']
        A_k1[drivers_json[drivers]['id'] + nr_passengers * 2 + nr_drivers] = drivers_json[drivers]['lower_tw']
        A_k2[drivers_json[drivers]['id'] + nr_passengers * 2 + nr_drivers] = drivers_json[drivers]['upper_tw']
    for passengers in passengers_json:
        T_k[passengers_json[passengers]['id']] = passengers_json[passengers]['max_ride_time']
        A_k1[passengers_json[passengers]['id'] + nr_passengers] = passengers_json[passengers]['lower_tw']
        A_k2[passengers_json[passengers]['id'] + nr_passengers] = passengers_json[passengers]['upper_tw']


add_parameters()

print(d_k)

def generate_NK():
    NK = {}
    for drivers in drivers_json:
        nodes = []
        for paths in T_ij:
            if paths[0] == drivers_json[drivers]['id']:
                """origin og destination noden for driver. Hvis disse to ikke er i listen nodes,
                 og hvis driver ikke rekker å komme seg til destination innen gitt timewindow"""
                if paths[0] not in nodes and ((paths[0] + nr_passengers * 2 + nr_drivers) not in nodes) \
                        and T_ij[(paths[0], paths[0] + nr_passengers * 2 + nr_drivers)] < A_k2[
                    drivers_json[drivers]['id'] + nr_passengers * 2 + nr_drivers]:
                    nodes.append(paths[0])
                    nodes.append(paths[0] + nr_passengers * 2 + nr_drivers)
                """pick up and delivery noder for passengers. Hvis pick up noden ikke er i listen, 
                og den tilhørende delivery noden ikke er innenfor den korteste veien"""
                if paths[1] not in nodes and ((paths[1] + nr_passengers) in ND) and (
                        paths[1] + nr_passengers < len(N) - 1) \
                        and (T_ij[paths] < A_k2[paths[1] + nr_passengers]):
                    nodes.append(paths[1])
                if paths[1] not in nodes and paths[1] in ND and (T_ij[paths] < A_k2[paths[1]]):
                    nodes.append(paths[1])
                if drivers_json[drivers]['max_ride_time'] < T_ij[paths] and paths[1] in ND and paths[1] in nodes:
                    nodes.remove(paths[1])
                    nodes.remove(paths[1] - nr_passengers)
        nodes.sort()
        NK[drivers_json[drivers]['id']] = nodes
    return NK


print(generate_NK())