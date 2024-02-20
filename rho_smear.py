import rho_simulation_functions as elli
import elli_fit_functions as fit
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import make_interp_spline
import matplotlib.pyplot as plt

def get_smeared_rho(model, angle_locations, wavelength, substrate, incident_ri, sigma, **params):
    simulation = fit.model_to_fit(model, wavelength, substrate, incident_ri)
    angles = np.arange(1,90,0.01)
    rho = simulation(angles,**params)
    psi = elli.rho_to_psi(rho)
    delta = elli.rho_to_delta(rho)
    psi_smeared = gaussian_filter1d(psi, sigma)
    delta_smeared = gaussian_filter1d(delta, sigma)
    rho_smeared_all = elli.psi_delta_to_rho(psi_smeared, delta_smeared)
    real_smeared_all = rho_smeared_all.real
    imag_smeared_all = rho_smeared_all.imag

    interp_func_real = make_interp_spline(angles,real_smeared_all)
    interp_func_imag = make_interp_spline(angles,imag_smeared_all)

    real_smeared_at_angle_locations = interp_func_real(angle_locations)
    imag_smeared_at_angle_locations = interp_func_imag(angle_locations)

    return real_smeared_at_angle_locations+complex(0,1)*imag_smeared_at_angle_locations






