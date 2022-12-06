import matplotlib.pyplot as plt

objVal = 41



result_solution = [0, 11.0, 22.0, 24.0, 26.0, 27.0, 36.0, 40.0, 41.0]
result_bound = [44.999999999999986, 44.99999999993048, 44.99999999993048, 44.99999999993048, 44.99999999993048, 44.99999999993048, 44.99999999993048, 45]
result_time = [55.60800004005432, 312.279000043869, 2013.6779999732971, 2013.6949999332428, 2013.7160000801086, 2088.667000055313, 2088.6829998493195, 3332.3079998493195]



if objVal == result_bound[-1]:
    for i in range(len(result_solution), 3600):
        result_solution.append(result_bound[-1])
    for i in range(len(result_time), 3600):
        result_time.append(i)


if objVal != result_bound[-1]:
    last_solution = result_solution[-1]
    for i in range(int(result_time[-1]), 3600):
        print(i)
        result_solution.append(last_solution)
    for i in range(int(result_time[-1]), 3601):
        result_time.append(i)

  
def get_graph():
    plt.figure(2)
    plt.xlim(-160, 3800)
    plt.ylim(-1, result_bound[-1] + 1)
    plt.axhline(y = result_bound[0], color = 'r', linestyle = 'dashed', label = "UB = " + str(result_bound[-1]))
    plt.axvline(x = 3600, color = 'y', linestyle = 'dashed', label = "Time = 3600s" )
    plt.plot(result_time, result_solution)
    plt.ylabel('Passengers served')
    plt.xlabel('Time [s]')
    plt.legend()
    
    plt.legend(bbox_to_anchor = (0.85, 1.2), loc = 'upper center')
    
    plt.show()

get_graph()