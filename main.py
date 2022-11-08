import numpy as np
from gurobipy import Model, GRB, quicksum
import matplotlib.pyplot as plt
import json
passengers_json = json.load(open('passengers.json'))
drivers_json = json.load(open('drivers.json'))
rnd=np.random
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
N = [i for i in range(nr_passengers*2+nr_drivers*2)]
NP = N[int(len(D)):int(len(N)/2)]
ND = N[int(len(N)/2):-int(len(D))]
A = [(i, j) for i in N for j in N if i!=j]

delivery_and_pickup_node_pairs = {ND[i]: NP[i] for i in range(len(ND))}
pickup_and_delivery_node_pairs = {NP[i]: ND[i] for i in range(len(ND))}

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
        """ Use driver and passenger information from json. files to add Parameters
        :return:
        """
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

driver_origin_nodes = {k: o_k[k] for k in D}
driver_destination_nodes = {k: d_k[k] for k in D}

def check_time_window_between_arc(i, j):
        """ Checks if the time of traveling between (i, j) = (driver origin or passenger pick up nodes, passenger delivery node) is within the time window of j
        :param i: Integer - origin or pick up nodes
        :param j: Integer - delivery nodes
        :return: Boolean
        """
        return T_ij[(i, j)] < A_k2[j]

def check_max_ride_time_between_arc(i, j):
        """ Checks if the time of traveling between (i, j) = (driver origin node, passenger delivery or driver destination node) is within the max travel time to j
        :param i: Integer - origin or pick up nodes
        :param j: Integer - delivery nodes
        :return: Boolean
        """
        return T_k[i] < T_ij[(i,j)]

def process_NK():
        '''Removes nodes where:
         1) the quickest path between (i, j) = (driver origin node, passenger delivery node) is not within j's timewindow
         2) the quickest path between (i, j) = (any node, passenger delivery node) is not within j's timewindow
         3) the quickest path between (i, j) = (driver origin node, passenger delivery) is not within the maximum ridetime from driver origin node i to j
        :return: {k: [nodes]} - returns set of feasible nodes driver k can travel to and excludes other driver's origin and destination nodes
        '''
        NK = {}
        for driver in D:
                resulting_nodes = []
                for arc in T_ij:
                        i = arc[0]
                        j = arc[1]
                        if i not in resulting_nodes:
                                resulting_nodes.append(i)
                        if j not in resulting_nodes:
                                resulting_nodes.append(j)
                        if i == driver and j in ND and not check_time_window_between_arc(i, j):
                                        pickup_node = delivery_and_pickup_node_pairs[j]
                                        resulting_nodes.remove(pickup_node)
                                        resulting_nodes.remove(j)
                        if i in NP and j in ND and pickup_and_delivery_node_pairs[i] == j and not check_time_window_between_arc(i, j):
                                        resulting_nodes.remove(i)
                                        resulting_nodes.remove(j)
                        if i == driver and j in ND and not check_max_ride_time_between_arc(i, j):
                                        pickup_node = delivery_and_pickup_node_pairs[j]
                                        resulting_nodes.remove(pickup_node)
                                        resulting_nodes.remove(j)
                resulting_nodes.sort()
                NK[driver] = resulting_nodes
                for node in NK[driver]:
                        if node != driver and node in list(driver_origin_nodes.values()):
                                resulting_nodes.remove(node)
                        if node != driver_destination_nodes[driver] and node in list(driver_destination_nodes.values()):
                                resulting_nodes.remove(node)
                NK[driver] = resulting_nodes
        return NK
NK = process_NK()


def generate_NPK(NK):
        """
        :param NK: {k: [nodes]} - set of preprocessed feasible nodes for driver k to visit
        :return: {k: [nodes]} - set of feasible pick up nodes for driver k to visit
        """
        NPK={}
        for drivers in NK:
                nodes = []
                for node in NK[drivers]:
                        if node in NP:
                                nodes.append(node)
                NPK[drivers]=nodes
        return NPK

def generate_NDK(NK):
        """
        :param NK: {k: [nodes]} - set of preprocessed feasible nodes for driver k to visit
        :return: {k: [nodes]} - set of feasible pick up nodes for driver k to visit
        """
        NDK={}
        for drivers in NK:
                nodes = []
                for node in NK[drivers]:
                        if node in ND:
                                nodes.append(node)
                NDK[drivers]=nodes
        return NDK

NPK = generate_NPK(NK)
NDK = generate_NDK(NK)


def check_driver_origin_node(node):
        """ Checks if node is a driver origin node
        :param node: Integer - a node
        :return: Boolean - True if node is a driver origin node, False otherwise
        """
        return node in driver_origin_nodes.values()

def check_driver_destination_node(node):
        """ Checks if node is a driver destination node
        :param node: Integer - a node
        :return: Boolean - True if node is a driver destination node, False otherwise
        """
        return node in driver_destination_nodes.values()

def from_delivery_to_pickup_arc(arc):
        """  Checks if the arc (i, j) is from a passenger delivery node to a passenger pick up node
        :param arc: (i, j) - arc from node i to node j
        :return: Boolean - returns True if i is a delivery node AND j is a pick up node in arc (i, j), False otherwise
        """
        return arc[0] in ND and arc[1] in NP

def process_AK(NK):
        """ Removes:
        1) all arcs (i, j) where j are origin nodes, i are destination nodes, and i j in (i, j) where i is a pick up node and j is a delivery node
        2) all arcs going in to j, where j is a delivery node and if the ride time for a passenger to travel from its pick up node to j is higher than the maximum ride time for passenger.
                If a passenger cannot get to its delivery node within that persons max ride time from their pick up node using the shortest arc,
                then there should be no arcs going into that persons delivery node because we would never be able to deliver that guy
        :param NK: {k, [nodes]} - set of preprocessed feasible nodes for driver k to visit
        :return: {k, [arcs]} - returns a set of feasible arcs (i, j) for driver k to travel with.
        """
        result = {}
        AK = {k: [(i, j) for i in NK[k] for j in NK[k] if i != j] for k in NK}
        for driver in AK:
                arcs = []
                for arc in AK[driver]:
                        i = arc[0]
                        j = arc[1]
                        if not check_driver_origin_node(j):
                                if not check_driver_destination_node(i):
                                        if not from_delivery_to_pickup_arc(arc):
                                                arcs.append(arc)

                for arc in AK[driver]:
                        i = arc[0]
                        j = arc[1]
                        """removes all arcs going into j, if a passenger that has j as the delivery node where traveling from that guys pick up node to j exceeds the max time a passenger is willing to ride"""
                        if i in NP and j in ND and pickup_and_delivery_node_pairs[i] == j and T_k[i] < T_ij[(i, j)]:
                                arcs.remove(arc)
                                for i in D + NP:
                                        if (i, j) in arcs:
                                                arcs.remove((i,j))
                        # må remove alle arcs som går inn til j da
                result[driver] = arcs

        return result

AK = process_AK(NK)

print("D:", D)
print("N:", N)
print("NP:", NP)
print("ND:", ND)
print("A:", A)
print("NK:", NK)
print("NPK:", NPK)
print("NDK:", NDK)
print("AK:", AK)

model=Model('RRP')

def set_variables():
        """Add variables"""
        x = model.addVars([(k,i,j) for k in D for (i, j) in AK[k]], vtype=GRB.BINARY, name ='x_kij')
        model.update()
        z = model.addVars(NP, vtype=GRB.BINARY, name='z_i')
        model.update()
        t = model.addVars([(k, i) for k in D for i in NK[k]], vtype=GRB.CONTINUOUS, name='t_ki')
        model.update()
        return x, z, t

x, z ,t = set_variables()

def set_objective():
        '''Model'''
        #model.modelSense = GRB.MINIMIZE
        #model.setObjective(quicksum(T_ij[i,j]*x[k,i,j] for i, j in A for k in D), GRB.MINIMIZE)
        #model.setObjective(quicksum(T_ij[i,j]*x[k,i,j] for i in N for j in N for k in D if i!=j), GRB.MINIMIZE)
        model.modelSense = GRB.MAXIMIZE
        model.setObjective(quicksum(z[i] for i in NP))
        model.update()

set_objective()

def add_constraints():
        '''Constraints'''
        '''Routing constraits'''
        nodes_without_destinations = {}
        for k in D:
                liste = []
                for i in NK[k]:
                        destinations = list(driver_destination_nodes.values())
                        if i not in destinations:
                                liste.append(i)
                nodes_without_destinations[k] = liste

        model.addConstrs(quicksum(x[k,i,j] for j in NPK[k] + [driver_destination_nodes[k]]) == 1 for k in D for i in [driver_origin_nodes[k]])


        model.addConstrs(quicksum(x[k,i,j] for i in [driver_origin_nodes[k]] + NDK[k]) == 1 for k in D for j in [driver_destination_nodes[k]])
        model.addConstrs((quicksum(x[k,i,j] for j in NK[k] if j!=i if j not in list(driver_origin_nodes.values())) == quicksum(x[k,j,i] for j in NK[k] if j!=i if j not in list(driver_destination_nodes.values()))) for k in D for i in NK[k][1:-1])

        model.addConstrs((quicksum(x[k,i,j] for j in NK[k] if j!=i if j not in list(driver_origin_nodes.values())) - quicksum(x[k,nr_passengers+i,j] for j in ND + [driver_destination_nodes[k]] if j!=(i + nr_passengers)))==0 for k in D for i in NPK[k])
        model.addConstrs((quicksum(x[k,i,j] for k in D for j in NK[k] if j!=i if j not in list(driver_origin_nodes.values()))) - z[i]==0 for i in NP)

        #ny constraint 1 (test ut å ta bort) ENDRING
        model.addConstrs((quicksum(x[k,i,j] for k in D for i in NK[k] if j!=i if i not in list(driver_destination_nodes.values()))) <= 1 for j in NP + ND)


        #ny constraint 2 (endre i rapporten) ENDRING

        model.addConstr((quicksum(x[k,i,j] for k in D for i in N for j in driver_origin_nodes.values() if j!=i and (j not in driver_origin_nodes.values() and i not in driver_origin_nodes.values()))) == 0)

        #model.addConstrs((quicksum(x[k, i, j] for k in D for i in NP + ND + list(driver_destination_nodes.values()) if i!=j)) == 0 for j in list(driver_origin_nodes.values()))


        #ny constraint 3
        model.addConstr((quicksum(x[k,i,j] for k in D for i in driver_destination_nodes.values() for j in N if j!=i and (j not in driver_destination_nodes.values() and i not in driver_destination_nodes.values()))) == 0)
        #model.addConstrs((quicksum(x[k, i, j] for k in D for j in N if i!=j) == 0 for i in list(driver_destination_nodes.values())))
        #model.addConstrs((quicksum(x[k, i, j] for k in D for j in N if i!=j if (i not in list(driver_destination_nodes.values()) and j not in list(driver_destination_nodes.values()))) == 0 for i in list(driver_destination_nodes.values())))


        '''Precedence constraint'''
        model.addConstrs(t[k,i] + T_ij[i, nr_passengers+i] - t[k, nr_passengers+i] <= 0 for k in D for i in NP)

        '''Time constraint'''
        model.addConstrs(t[(k,i)]+T_ij[(i,j)] - t[(k,j)] - M*(1-x[k,i,j]) <= 0 for k in D for (i, j) in AK[k])
        model.addConstrs(A_k1[nr_passengers+i]<=t[k,nr_passengers+i] for k in D for i in NPK[k])
        model.addConstrs(t[k,nr_passengers+i]<=A_k2[nr_passengers+i] for k in D for i in NPK[k])

        #ENDRET
        model.addConstrs(A_k1[k1]<=t[k, k2] for k in D for k1 in driver_destination_nodes.values() for k2 in nodes_without_destinations[k])
        #ENDRET
        model.addConstrs(t[k, k2]<=A_k2[k1] for k in D for k1 in driver_destination_nodes.values() for k2 in nodes_without_destinations[k])
        model.addConstrs(t[k,nr_passengers+i] - t[k,i] <= T_k[i] for k in D for i in NPK[k])


        model.addConstrs(t[k,driver_destination_nodes[k]] - t[k, driver_origin_nodes[k]] <= T_k[k] for k in D)

        #ny timewindow constraint:

        model.addConstrs(x[k,i,j]*A_k1[j]<=(t[k,i]+T_ij[i,j]) * x[k,i,j] for k in D for i in NPK[k] for j in NDK[k] if i!=j)
        model.addConstrs(x[k,i,j]*A_k2[j]>=(t[k,i]+T_ij[i,j]) * x[k,i,j] for k in D for i in NPK[k] for j in NDK[k] if i!=j)
        #model.addConstrs(A_k1[k1]<=(t[k, k1]+T_ij[] for k in D for k1 in d_k.values())
        #model.addConstrs(t[k, k1]<=A_k2[k1] for k in D for k1 in d_k.values())

        '''Capacity constraint'''
        model.addConstrs(quicksum(x[k,i,j] for i in NPK[k] for j in NK[k] if j!=i if j not in list(driver_origin_nodes.values())) <= Q_k[k] for k in D)
        model.update()

"""Optimize"""
model.Params.TimeLimit=30
add_constraints()
model.optimize()

obj = model.getObjective()
#for i in model.getVars():
 #       print(i, i.x)

"""model.computeIIS()
model.write('model.MPS')
model.write('model.lp')
model.write('model.ilp')"""

"""Visualization"""
def visualize():

        for k in D:
                active_arcs=[a for a in AK[k] if x[k, a[0], a[1]].x > 0.99]
                arc_sum=0
                for i,j in active_arcs:
                        plt.plot([xc[i], xc[j]], [yc[i],yc[j]], c='g', zorder=0)

                for i in range(len(active_arcs)):
                        arc_sum += T_ij[active_arcs[i]]

        plt.plot(xc[0], yc[0], c='r', marker='s')
        plt.plot(xc[1], yc[1], c='r', marker='s')
        plt.plot(xc[-1],yc[-1], c='r', marker = 's')
        plt.plot(xc[-nr_drivers],yc[-nr_drivers], c='r', marker = 's')
        plt.scatter(xc[1:len(xc)-nr_drivers], yc[1:len(yc)-nr_drivers], c='b')
        plt.show()
        print(active_arcs)
        print(arc_sum)

visualize()

