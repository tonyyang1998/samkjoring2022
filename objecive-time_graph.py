import matplotlib.pyplot as plt

<<<<<<< HEAD
objVal = 15




result_solution = [0, 6.0, 8.0, 10.0, 11.0, 11.0, 11]
result_bound = [20.0, 20.0, 20.0, 20.0, 17.0, 16]
result_time = [1.5329999923706055, 60, 100, 300, 540, 2861]
=======
objVal = 6
model_time = 77


#small5
result_solution = [0, 2.0, 4.0, 5.0, 6.0]
result_bound = [9.0, 9.0, 9.0, 9.0, 6]
result_time = [0.2709999084472656, 0.495999813079834, 0.8399999141693115, 1.0269999504089355, model_time]
>>>>>>> 3231f675705cd0245d8c76a57b12dda6637ee283

#M3, 1.5
#[0, 6.0, 8.0, 10.0, 11.0]
#[20.0, 20.0, 20.0, 20.0]
#[1.5329999923706055, 6.293999910354614, 9.065000057220459, 11.213000059127808]

<<<<<<< HEAD
=======
if objVal == result_bound[-1]:
    for i in range(int(result_solution[-1]), 3800):
        if len(result_solution) !=3600:
            result_solution.append(result_bound[-1])
    for i in range(int(result_time[-1]), 3690):
        if len(result_time)!=3600 and result_time[-1]<=3600:
            result_time.append(i)
>>>>>>> 3231f675705cd0245d8c76a57b12dda6637ee283

if objVal == result_bound[-1]:
    for i in range(int(result_solution[-1]), 3800):
        if len(result_solution) !=3600:
            result_solution.append(result_bound[-1])
    for i in range(int(result_time[-1]+1), 3690):
        if len(result_time)!=3600 and result_time[-1]<=3600:
            result_time.append(i)

if objVal != result_bound[-1]:
    last_solution = result_solution[-1]
<<<<<<< HEAD
    for i in range(int(result_time[-1]+1), 3801):
        if len(result_time)!=3600 and result_time[-1]<=3600:
                result_time.append(i)
    for i in range(len(result_solution), 3800):
        if len(result_solution) !=3600 and len(result_solution)!=len(result_time):
            print("fitte")
            result_solution.append(last_solution)
                
=======
    for i in range(int(result_time[-1]), 3800):
        if len(result_solution) !=3600:
            result_solution.append(last_solution)
    for i in range(int(result_time[-1]), 3801):
        if len(result_time)!=3600 and result_time[-1]<=3600:
                result_time.append(i)
                

>>>>>>> 3231f675705cd0245d8c76a57b12dda6637ee283
last_bound_value=result_bound[0]

last_bound=result_bound[-1]
for i in range(int(result_bound[-1]), 3800):
    if len(result_bound)!=len(result_time):
        result_bound.append(last_bound)

<<<<<<< HEAD

def get_graph():
    plt.figure(2)
    plt.xlim(-160, 3800)
    plt.ylim(-1, last_bound_value + 5)
    plt.axvline(x = 3600, color = 'y', linestyle = 'dashed', label = "Time = 3600s" )
    plt.plot(result_time, result_solution)
=======
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
>>>>>>> 3231f675705cd0245d8c76a57b12dda6637ee283
    plt.plot(result_time, result_bound, color='red', linestyle='dashed', label="Upper bound")
    plt.ylabel('Passengers served')
    plt.xlabel('Time [s]')
    plt.legend()
    plt.legend(bbox_to_anchor = (0.85, 1.2), loc = 'upper center')


    
    plt.show()

get_graph()