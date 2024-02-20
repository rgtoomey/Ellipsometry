import numpy as np

import elli_fit_functions as fit
import lmfit
import pandas
import rho_simulation_functions as elli
import rho_simulation_class as Elli
import matplotlib.pyplot as plt
import csv

#filename = "Edmunds_crystal_2.txt"
#filename = "NBK7.txt"
filename = ("Si_only_and_PLDGA.txt")

#filename = "test_jan1724_c.txt"

#filename = "feb2_ozi_2.txt"

#filename = "NBK7.txt"
substrate = "silicon"
wavelength = 632.8
n_i = 1
ri_model = "single_layer"
plots = 'no'
offset = 0
zone = "avg"

file = open('data/'+filename)
file.readline()
date_data = file.readline().replace("\n","")
time_stamp_data = file.readline().replace("\n","")
file.readline()
num_zones = int(file.readline().replace("\n",""))

if num_zones == 1:
    data = pandas.read_csv(file,delimiter="\t",names=["Angle","Psi","Delta"])
    angle_data = data.Angle
    psi_data = data.Psi
    delta_data = data.Delta
elif num_zones == 2:
    data = pandas.read_csv(file, delimiter="\t", names=["Angle", "Psi_1", "Psi_2", "Delta_1", "Delta_2"])

    if zone == "left":
        angle_data = data.Angle
        psi_data = data.Psi_1
        delta_data = data.Delta_1

    if zone == "right":
        angle_data = data.Angle
        psi_data = data.Psi_2
        delta_data = data.Delta_2

    if zone == "avg":
        psi_1_index = data.Psi_1.idxmin()
        psi_2_index = data.Psi_2.idxmin()
        shift_factor = psi_1_index - psi_2_index
        data["Angle_shifted"] = data.Angle.shift(shift_factor)
        data["Psi_2_shifted"] = data.Psi_2.shift(shift_factor)
        data["Delta_2_shifted"] = data.Delta_2.shift(shift_factor)
        data["Angle_avg"] = (data.Angle+data.Angle_shifted)/2
        data["Psi_avg"] = (data.Psi_1+data.Psi_2_shifted)/2
        data["Delta_avg"] = (data.Delta_1 + data.Delta_2_shifted)/2
        angle_shift = data.Angle.iloc[psi_1_index]- data.Angle.iloc[psi_2_index]
        angle_data = data.Angle_avg.dropna()
        psi_data = data.Psi_avg.dropna()
        delta_data = data.Delta_avg.dropna()
elif num_zones == 4:
    data = pandas.read_csv(file, delimiter="\t", names=["Angles","Psi_1", "Psi_2", "Psi_3", "Psi_4", "Delta_1", "Delta_2", "Delta_3", "Delta_4"])

rho_data = elli.psi_delta_to_rho(psi_data, delta_data)

model_func = fit.elli_model(ri_model, wavelength, substrate, n_i)
gmodel = lmfit.Model(model_func, name = ri_model)
params = gmodel.make_params()

if ri_model == "thin_film":
    params.add("excess_1", value = -1.3, vary = True)
    params.add("excess_2", value = 0, vary = True)
elif ri_model == "single_layer":
    params.add("n_avg", value = 1.46, min = 1.0, max = 1.6, vary = False)
    params.add("width", value = 0, min = 0.01, max = 25, vary = True)
    params.add("angle_offset", value = offset, min = -2, max = 2.0, vary = True)
elif ri_model == "two_layer":
    params.add("n_avg_1", value = 1.5, min = 1.4, max = 1.7, vary = True)
    params.add("width_1", value = 80., min = 0.01, max = 300, vary = True)
    params.add("n_avg_2", value = 1.65, min = 1.5, max = 1.7, vary = True)
    params.add("width_2", value = 8., min = 0.01, max = 10, vary = True)
    params.add("angle_offset", value=offset, min=-1, max=1.0, vary=True)
elif ri_model == "three_layer":
    params.add("n_avg_1", value = 1.5, min = 1.4, max = 1.7, vary = True)
    params.add("width_1", value = 5., min = 0.01, max = 10, vary = True)
    params.add("n_avg_2", value = 1.585, min = 1.4, max = 1.7, vary = False)
    params.add("width_2", value = 80., min = 0.01, max = 300, vary = True)
    params.add("n_avg_3", value = 1.5, min = 1.4, max = 1.7, vary = True)
    params.add("width_3", value = 5., min = 0.01, max = 10, vary = True)
elif ri_model == "linear_profile":
    params.add("n_avg", value = 1.5,  min = 1.4, max = 1.7, vary = True)
    params.add("width", value = 80., min = 0.01, max = 300, vary = True)
    params.add("dn", value=0, min = -0.5, max = 0.5, vary=True)
    params.add("angle_offset", value=offset, min=-1, max=1.0, vary=True)
elif ri_model == "tanh_profile":
    params.add("n_avg", value = 1.5, min = 1.4, max = 1.7, vary = True)
    params.add("width", value = 80, min = 0.01, max = 300, vary = True)
    params.add("dn",  value = 0.0, min = -0.2, max = 0.2, vary = True)
    params.add("sigma", value = 20, min = 0.01, vary = True)
    params.add("angle_offset", value=offset, min=-1, max=1.0, vary=False)


title = filename.replace(".txt","")

gfit = gmodel.fit(data = rho_data, params = params, angle_in_degrees = angle_data)
print(gfit.fit_report())

result = fit.Elli_out(ri_model,n_i,substrate,gfit.values)
result.compare_to_data(angle_data,rho_data,type = "psi_delta")
result.compare_to_data(angle_data,rho_data,type = "rho_difference")
result.compare_to_data(angle_data,rho_data,type = "residual")

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
