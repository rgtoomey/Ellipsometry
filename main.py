import elli_fit as fit
import lmfit
import pandas
import rho_simulation_functions as elli
import rho_simulation_class as sim
import matplotlib.pyplot as plt
import csv

filename= "silicon_1st_run.txt"
substrate = "silicon"

file = open('data/'+filename)
file.readline()
date_data = file.readline().replace("\n","")
time_stamp_data = file.readline().replace("\n","")
file.readline()
num_zones = int(file.readline().replace("\n",""))

data = pandas.read_csv(file,delimiter="\t",header=None)

psi_columns = [*range(1,num_zones+1)]
delta_columns = [*range(num_zones+1,2*num_zones+1)]

angle_data = data[0]
psi_data = data[psi_columns].mean(1)
delta_data = data[delta_columns].mean(1)

rho_data = elli.psi_delta_to_rho(psi_data, delta_data)

model_func = fit.model_to_fit("single",632.8,substrate,1.0)

gmodel = lmfit.Model(model_func)

params = gmodel.make_params()

params.add("n_avg", value = 1.48, vary = False)
params.add("width", value = 3.25, vary = True)


gfit = gmodel.fit(data = rho_data, params = params, angle_in_degrees = angle_data)

print(gfit.fit_report())
gfit.plot(parse_complex='real', ylabel = "real_rho", title = filename )
plt.show()

gfit.plot(parse_complex='imag', ylabel = "imag_rho", title = filename)

plt.show()

print("hey")