import matplotlib.pyplot as plt

objVal = 6
model_time = 77


#small5
result_solution = [0, 2.0, 4.0, 5.0, 6.0]
result_bound = [9.0, 9.0, 9.0, 9.0, 6]
result_time = [0.2709999084472656, 0.495999813079834, 0.8399999141693115, 1.0269999504089355, model_time]


if objVal == result_bound[-1]:
    for i in range(int(result_solution[-1]), 3800):
        if len(result_solution) !=3600:
            result_solution.append(result_bound[-1])
    for i in range(int(result_time[-1]), 3690):
        if len(result_time)!=3600 and result_time[-1]<=3600:
            result_time.append(i)


if objVal != result_bound[-1]:
    last_solution = result_solution[-1]
    for i in range(int(result_time[-1]), 3800):
        if len(result_solution) !=3600:
            result_solution.append(last_solution)
    for i in range(int(result_time[-1]), 3801):
        if len(result_time)!=3600 and result_time[-1]<=3600:
                result_time.append(i)
                

last_bound_value=result_bound[0]

last_bound=result_bound[-1]
for i in range(int(result_bound[-1]), 3800):
    if len(result_bound)!=len(result_time):
        result_bound.append(last_bound)

ny_result_solution  = [0, 2.0, 4.0, 5.0, 6.0]
ny_result_time=[0.2709999084472656, 0.495999813079834, 0.8399999141693115, 1.0269999504089355, model_time]

print(result_time)

print(result_bound)
def get_graph():
    plt.figure(2)
    plt.xlim(-160, 3800)
    plt.ylim(-1, last_bound_value + 1)
    plt.axvline(x = 3600, color = 'y', linestyle = 'dashed', label = "Time = 3600s" )
    plt.plot(ny_result_time, ny_result_solution)
    plt.plot(result_time, result_bound, color='red', linestyle='dashed', label="Upper bound")
    plt.ylabel('Passengers served')
    plt.xlabel('Time [s]')
    plt.legend()
    plt.legend(bbox_to_anchor = (0.85, 1.2), loc = 'upper center')


    
    plt.show()

get_graph()