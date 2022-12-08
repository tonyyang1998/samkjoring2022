import matplotlib.pyplot as plt

objVal = 15


#M3

result_solution = [0, 6.0, 8.0, 10.0, 11.0, 11.0, 11]
result_bound = [20.0, 20.0, 20.0, 20.0, 17.0, 16]
result_time = [1.5329999923706055, 60, 100, 300, 540, 2861]

if objVal == result_bound[-1]:
    for i in range(int(result_solution[-1]), 3800):
        if len(result_solution) !=3600:
            result_solution.append(result_bound[-1])
    for i in range(int(result_time[-1]+1), 3690):
        if len(result_time)!=3600 and result_time[-1]<=3600:
            result_time.append(i)

if objVal != result_bound[-1]:
    last_solution = result_solution[-1]
    for i in range(int(result_time[-1]+1), 3801):
        if len(result_time)!=3600 and result_time[-1]<=3600:
                result_time.append(i)
    for i in range(len(result_solution), 3800):
        if len(result_solution) !=3600 and len(result_solution)!=len(result_time):
            print("fitte")
            result_solution.append(last_solution)
                
last_bound_value=result_bound[0]

last_bound=result_bound[-1]
for i in range(int(result_bound[-1]), 3800):
    if len(result_bound)!=len(result_time):
        result_bound.append(last_bound)


def get_graph():
    plt.figure(2)
    plt.xlim(-160, 3800)
    plt.ylim(-1, last_bound_value + 5)
    plt.axvline(x = 3600, color = 'y', linestyle = 'dashed', label = "Time = 3600s" )
    plt.plot(result_time, result_solution)
    plt.plot(result_time, result_bound, color='red', linestyle='dashed', label="Upper bound")
    plt.ylabel('Passengers served')
    plt.xlabel('Time [s]')
    plt.legend()
    plt.legend(bbox_to_anchor = (0.85, 1.2), loc = 'upper center')


    
    plt.show()

get_graph()