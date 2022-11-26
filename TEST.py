import main

arcs = main.run_only_once()

print(arcs)


def sort_path():
    sorted_path = {}
    for driver in arcs:
        b = []
        a = arcs[driver]
        d = {t[0]: t[1] for t in a}
        prev_key = 0
        for i in range(len(d)):
            b.append((prev_key, d[prev_key]))
            prev_key = d[prev_key]
        sorted_path[driver] = b
    return sorted_path

sorted_path = sort_path()

print(sorted_path)

def get_coordinates():

    result = {}
    for driver in sorted_path:
        visitation_sequence=[]
        for arc in sorted_path[driver]:
            if arc[0] not in visitation_sequence:
                visitation_sequence.append(arc[0])
            if arc[1] not in visitation_sequence:
                visitation_sequence.append(arc[1])

        driver_origin = []
        driver_destination = []
        passenger_pickup = []
        passenger_delivery = []

        for node in visitation_sequence:
            if node in main.D:
                for d in main.drivers_json:
                    if main.drivers_json[d]['id'] == node:
                        driver_origin.append(
                            (main.drivers_json[d]['origin_yc'], main.drivers_json[d]['origin_xc']))
                        driver_destination.append(
                            (main.drivers_json[d]['destination_yc'], main.drivers_json[d]['destination_xc']))

            if node in main.NP:
                for p in main.passengers_json:
                    if main.passengers_json[p]['id'] == node:
                        passenger_pickup.append(
                            (main.passengers_json[p]['origin_yc'], main.passengers_json[p]['origin_xc']))

            if node in main.ND:
                for p in main.passengers_json:
                    if main.passengers_json[p]['id'] == node:
                        passenger_delivery.append(
                            (main.passengers_json[p]['destination_yc'], main.passengers_json[p]['destination_xc']))
        result[driver] = driver_origin + passenger_pickup + passenger_delivery + driver_destination
    return result


get_coordinates()


#print(path)