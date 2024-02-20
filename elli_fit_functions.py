import rho_simulation_functions as elli
import rho_simulation_class as Elli

def elli_model(ri_model,wavelength,substrate,incident_ri, **kwargs):
    n_t = elli.get_n_t(substrate)
    n_i = incident_ri

    if ri_model == "thin_film":
        def fit_function(angle_in_degrees,**params):
            return elli.get_rho_thin_film(angle_in_degrees, wavelength, n_i, n_t, difference = 'no', **params)

    elif ri_model in elli.get_ri_model_names():
        def fit_function(angle_in_degrees,**params):
            return elli.get_rho_from_ri_profile(ri_model,angle_in_degrees, wavelength, n_i, n_t, **params)

    else:
        return print("Something is Wrong!")

    return fit_function

def Elli_out(ri_model,n_i,substrate,params):
    return Elli.Simulation(ri_model,n_i,substrate,**params)