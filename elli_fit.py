import rho_simulation_functions as elli
import rho_smear as smear
import json

with open("substrate_list.json", 'r') as refractive_index_list:
    refractive_index_list = json.load(refractive_index_list)

    name_of_substrates_list = refractive_index_list.keys()

sigma = 70

def model_to_fit(model,wavelength,substrate,incident_ri,**kwargs):
    n_t = refractive_index_list[substrate]
    n_i = incident_ri

    if model == "linear_profile":
        def fit(angle_in_degrees, n_avg, width, dn,**kwargs):
            params = {"n_avg": n_avg, "width": width, "dn": dn}

            if kwargs.get("smear") == 'yes':
                return smear.get_smeared_rho(model, angle_in_degrees, wavelength,substrate,incident_ri,sigma,**params)
            else:
                return elli.get_rho_from_model(model, angle_in_degrees, wavelength, n_i, n_t, **params)

    elif model == "tanh_profile":
        def fit(angle_in_degrees, n_avg, width, dn, sigma):
            params = {"n_avg": n_avg, "width": width, "dn": dn, "sigma": sigma}
            return elli.get_rho_from_model(model, angle_in_degrees, wavelength, n_i, n_t, **params)

    elif model == "single":
        def fit(angle_in_degrees, n_avg, width):
            params = {"n_avg": n_avg, "width": width}

            if kwargs.get("offset"):
                angle_in_degrees = angle_in_degrees + kwargs.get("offset")

            if kwargs.get("smear") == 'yes':
                return smear.get_smeared_rho(model, angle_in_degrees, wavelength,substrate,incident_ri,sigma,**params)
            else:
                return elli.get_rho_from_model(model, angle_in_degrees, wavelength, n_i, n_t, **params)
    else:
        pass

    return fit


