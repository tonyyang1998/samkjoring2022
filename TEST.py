import numpy as np
from gurobipy import Model, GRB, quicksum
import gurobipy as gp
import matplotlib.pyplot as plt
import json
import time
import TestExcel as te
import xlwt
from xlwt import Workbook
import pandas as pd




filename = "Medium Instances 1,5/Medium4,1.5.xlsx"
file_to_save = 'Results/Small Instances 1,5/Small_4,1.5.xls'

te.main(filename)

start_time = time.time()

passengers_json = json.load(open('sample_passenger.json'))
drivers_json = json.load(open('sample_driver.json'))


rnd = np.random
rnd.seed(0)

nr_passengers = len(passengers_json)
nr_drivers = len(drivers_json)

'''Coordinates '''
xc = []
yc = []


def add_coordinates():
    """ Create coordinates (x, y) for the origins and destinations of drivers and passengers
        :return:
        """
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
N = [i for i in range(nr_passengers * 2 + nr_drivers * 2)]
NP = N[int(len(D)):int(len(N) / 2)]
ND = N[int(len(N) / 2):-int(len(D))]
A = [(i, j) for i in N for j in N if i != j]

delivery_and_pickup_node_pairs = {ND[i]: NP[i] for i in range(len(ND))}
pickup_and_delivery_node_pairs = {NP[i]: ND[i] for i in range(len(ND))}

'''Parameters'''
o_k = {}
d_k = {}
T_k = {}

df = pd.read_excel("All_Origins_and_destinations.xlsx")
rows = df.shape[0]

# Create an empty dictionary to store the locations and their X and Y coordinates
all_origins = {}
all_destinations = {}

def read_from_file():

    # Start iterating from the first row
    for i in range(rows):
        # Get the current row
        row = df.iloc[i]
        
        # Get the location name
        origin = row["Origins"]
        
        # Get the X and Y coordinates
        x = row["Origin X"]
        y = row["Origin Y"]
        
        # Add the location and its X and Y coordinates to the dictionary
        all_origins[origin] = (x, y)
        
        destination = row["Destination"]
        xx = row["Destination X"]
        yy = row["Destination Y"]

        all_destinations[destination] = (xx, yy)

    all_destinations.popitem()

read_from_file()

def compare_locations(locations1, locations2):
    results = {}
    for location1, (x1, y1) in locations1.items():
        for location3, (x3, y3) in locations1.items():
            if location1 != location3:
                results[(location1, location3)] = ((x1, y1), (x3, y3))
        for location2, (x2, y2) in locations2.items():
            results[(location1, location2)] = ((x1, y1), (x2, y2))
        
    for location4, (x4, y4) in locations2.items():
        for location5, (x5, y5) in locations2.items():
            if location4 != location5:
                results[(location4, location5)] = ((x4, y4), (x5, y5))
    return results

compare_locations(all_origins, all_destinations)
#print(compare_locations(all_origins, all_destinations))


df = pd.read_excel(filename)
df1 = pd.read_excel("Between_Origins_and_destinations.xlsx")


def create_Tij():
    T_ij = {}
    for i, j in A:
        origin = df.iloc[i]["Origin location"]
        destination = df.iloc[j]["Destination location"]
        if j>len(D) + len(NP) and i < len(D) + len(NP):
            origin = df.iloc[i]["Origin location"]
            destination = df.iloc[j- (len(D) + len(NP))]["Destination location"]
        if i > len(D) + len(NP) and j < len(D) + len(NP):
            origin = df.iloc[i-(len(D) + len(NP))]["Origin location"]
            destination = df.iloc[j]["Destination location"]
        if i > len(D) + len(NP) and j > len(D) + len(NP):
            origin = df.iloc[i-(len(D) + len(NP))]["Origin location"]
            destination = df.iloc[j-(len(D) + len(NP))]["Destination location"]
        
        print(origin)
        print(destination)
        #print(df1.loc[origin, destination])
    

print(create_Tij())

T_ij = {(i, j): np.hypot(xc[i] - xc[j], yc[i] - yc[j]) for i, j in A}




Q_k = {}
A_k1 = {}
A_k2 = {}


def add_parameters():
    """ Use driver and passenger information from json. files to add Parameters
        :return:
        """
    for drivers in drivers_json:
        o_k[drivers_json[drivers]['id']] = drivers_json[drivers]['id']
        d_k[drivers_json[drivers]['id']] = drivers_json[drivers]['id'] + nr_passengers * 2 + nr_drivers
        T_k[drivers_json[drivers]['id']] = drivers_json[drivers]['max_ride_time'] * 1.9/1.5
        Q_k[drivers_json[drivers]['id']] = drivers_json[drivers]['max_capacity']
        A_k1[drivers_json[drivers]['id'] + nr_passengers * 2 + nr_drivers] = drivers_json[drivers]['lower_tw']
        A_k2[drivers_json[drivers]['id'] + nr_passengers * 2 + nr_drivers] = drivers_json[drivers]['upper_tw']
    for passengers in passengers_json:
        T_k[passengers_json[passengers]['id']] = passengers_json[passengers]['max_ride_time'] * 1.9/1.5
        A_k1[passengers_json[passengers]['id'] + nr_passengers] = passengers_json[passengers]['lower_tw']
        A_k2[passengers_json[passengers]['id'] + nr_passengers] = passengers_json[passengers]['upper_tw']

add_parameters()

driver_origin_nodes = {k: o_k[k] for k in D}
driver_destination_nodes = {k: d_k[k] for k in D}


def initialize_big_M():
    result={}
    for driver in D:
        result[driver] = T_k[driver] * 2.5
    return result


M = initialize_big_M()

