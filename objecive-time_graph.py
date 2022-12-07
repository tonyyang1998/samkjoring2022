import matplotlib.pyplot as plt

objVal = 15


#M3




result_solution = [0, 1.0, 3.0, 7.0, 8.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0]
result_bound=[20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 19.0]
result_time =[0.24100017547607422, 0.9900000095367432, 3.249000072479248, 3.427000045776367, 4.616000175476074, 6.702000141143799, 11.049000024795532, 509.04100012779236, 530.9560000896454, 987.6380000114441]
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