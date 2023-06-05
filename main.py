import ellipsometry as elli
import questionary
import matplotlib.pyplot as plt
import json
import lmfit
import numpy as np

import csv

print("Hello and Welcome!")

with open("lastSimulation.json", 'r') as last_simulation:
    last_simulation = json.load(last_simulation)

with open("refractiveIndexList.json", 'r') as refractive_index_list:
    refractive_index_list = json.load(refractive_index_list)

with open("modelRegistration.json", 'r') as model_information:
    model_information = json.load(model_information)

name_of_models_list = model_information.keys()
name_of_substrates_list = refractive_index_list.keys()

name_of_model_to_use = questionary.select(
        "",
        qmark = "Name of model",
        choices = name_of_models_list,
    ).ask()

name_of_substrate_to_use = questionary.select(
        "",
        qmark = "Name of substrate",
        choices = name_of_substrates_list,
    ).ask()


n_i = float(input("What is the refractive index of the incident medium (default is 1.0)? ") or 1.0)
n_t = refractive_index_list[name_of_substrate_to_use]


function_pointer = model_information[name_of_model_to_use]["function name"]
simulation_model = lmfit.Model(getattr(elli,function_pointer))

#parameter dictionary for fitting. Takes parameters directly from function.
simulation_params_dict = simulation_model.make_params()

#open additional list of parameter names
simulation_names_of_params = simulation_model.param_names

#Number of default parameters is 4
number_default_parameters = 4

#Number of total parameters
number_total_parameters = len(simulation_names_of_params)

#set the required values of parameters for all models (or default parameters).
simulation_params_dict.add("wavelength", value = 632.8, vary = False)
simulation_params_dict.add("n_i", value = n_i, vary = False)
simulation_params_dict.add("n_t_real", value = n_t[0], vary = False)
simulation_params_dict.add("n_t_imag", value = n_t[1], vary = False)

#set the optional values that depend on the model.

for i in range(4,number_total_parameters):
    param_name = simulation_names_of_params[i]
    text_to_ask = param_name + "? "
    param_value = float(input(text_to_ask))
    simulation_params_dict.add(param_name, value = param_value, vary = False)


angles = [*range(1,91,1)]

rho_eval = simulation_model.eval(simulation_params_dict, angle_in_degrees = angles)

real_rho = elli.rho_to_real(rho_eval)
imag_rho = elli.rho_to_imag(rho_eval)

plt.plot(angles,imag_rho)
plt.plot(angles,real_rho)

plt.show()

#simulation_params_dict.add("n_avg", value = 1.9, vary = True, min = 1, max = 2 )
#simulation_params_dict.add("thickness", value = 1800, vary = True, min = 0, max = 2000 )
#simulation_params_dict.pretty_print()


#model_fit = simulation_model.fit(method= 'ampgo', data = rho_eval, params= simulation_params_dict, angle_in_degrees = angles )

#best_fit_params = model_fit.params

#print(model_fit.values)
#print(model_fit.fit_report())





#print(model_eval)



#model_fit.plot(parse_complex='real')
#model_fit.plot(parse_complex='imag')






