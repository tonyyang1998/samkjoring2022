import matplotlib.pyplot as plt


result_solution = [-1e+100, 2.0, 5.0, 7.0, 9.0, 11.0, 12.0]
result_bound = [13.0, 13.0, 13.0, 13.0, 13.0, 13.0, 13.0]
result_time = [0.16000008583068848, 0.17300009727478027, 0.5250000953674316, 0.8350000381469727, 1.948000192642212, 3.3000001907348633, 5.150000095367432]

upper_bound=result_bound[0]
x_axis=[]

for i in range(3600):
    x_axis.append(i)

def get_graph():
    plt.plot(result_time, result_solution)
    plt.ylabel('Passengers served')
    plt.xlabel('Time [s]')
    plt.show()
get_graph