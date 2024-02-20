import numpy as np

import elli_fit_functions as fit
import lmfit
import pandas
import rho_simulation_functions as elli
import rho_simulation_class as Elli
import matplotlib.pyplot as plt
import csv
angle_data = [70]
offset = 4

filename = "081718_02wtpldg24h1_r4.txt"
substrate = "silicon"
wavelength = 632.8
n_i = 1
ri_model = "single_layer"
plots = 'no'


file = open('data/'+filename)
file.readline()
date_data = file.readline().replace("\n","")
time_stamp_data = file.readline().replace("\n","")
file.readline()
num_zones = int(file.readline().replace("\n",""))


data = pandas.read_csv(file,delimiter="\t",names=["Temperature","Psi","Delta"])
temperature_data = data.Temperature
psi_data = data.Psi
delta_data = data.Delta
rho_data = elli.psi_delta_to_rho(psi_data, delta_data)


model_func = fit.elli_model(ri_model, wavelength, substrate, n_i)
gmodel = lmfit.Model(model_func, name=ri_model)
params = gmodel.make_params()

params.add("n_avg", value = 1.46, min = 1.42, max = 1.5, vary = False)
params.add("width", value = 15., min = 0.01, max = 300, vary = True)
params.add("angle_offset", value = offset, min = -2, max = 2.0, vary = False)

title = filename.replace(".txt","")
num_points = len(temperature_data)
fit_thickness = np.zeros(num_points)
fit_n = np.zeros(num_points)

for i in range(num_points):
    gfit = gmodel.fit(data=[rho_data[i]], params=params, angle_in_degrees=angle_data)
    fit_n[i] = gfit.values['n_avg']
    fit_thickness[i] = gfit.values['width']

plt.plot(temperature_data,fit_thickness,'o')
plt.show()

for i in temperature_data:
    print(i)

for i in fit_thickness:
    print(i)

#result = fit.Elli_out(ri_model,n_i,substrate,gfit.values)
#result.compare_to_data(angle_data,rho_data,type = "psi_delta")
#result.compare_to_data(angle_data,rho_data,type = "rho_difference")
#result.compare_to_data(angle_data,rho_data,type = "residual")

if plots == 'yes':
    plt.plot(angle_data,psi_data,'o')
    plt.title(title)
    plt.xlabel("Angle of incidence (deg)")
    plt.ylabel("Psi (deg)")
    plt.show()
    input("Press Enter to continue...")
    plt.plot(angle_data,delta_data,'o')
    plt.title(title)
    plt.xlabel("Angle of incidence (deg)")
    plt.ylabel("Delta (deg)")
    plt.show()
    input("Press Enter to continue...")
    gfit.plot(parse_complex='real', ylabel = "real_rho", title = filename)
    plt.show()
    input("Press Enter to continue...")
    gfit.plot(parse_complex='imag', ylabel = "imag_rho", title = filename)
    plt.show()

print("Done!")
