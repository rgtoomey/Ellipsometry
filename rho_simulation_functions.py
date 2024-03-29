import numpy as np
import ri_models
from functools import reduce
import inspect
import json

pi = np.pi
exp = np.exp
asin = np.arcsin
acos = np.arccos
atan = np.arctan
sin = np.sin
cos = np.cos
tan = np.tan
tanh = np.tanh
sqrt = np.sqrt
deg2rad = np.deg2rad
rad2deg = np.rad2deg

#Functions for "ri_models"#
def get_ri_model_names():
    function_names = inspect.getmembers(ri_models, inspect.isfunction)
    return list(dict(function_names).keys())

def get_ri_param_names(ri_model):
    model = getattr(ri_models,ri_model)
    keys = list(inspect.signature(model).parameters.keys())
    return keys

def get_ri_params(ri_model,params):
    ri_param_names = get_ri_param_names(ri_model)
    ri_params = {key:params[key] for key in ri_param_names}
    return ri_params

#Functions for "ri_models"#
def get_n_t(substrate):
    with open("substrate_list.json", 'r') as refractive_index_list:
        refractive_index_list = json.load(refractive_index_list)
    return refractive_index_list[substrate]

#Ellipsometry rho modeling#

def get_rho_from_ri_profile(ri_model, angle_in_degrees, wavelength, n_i, n_t, **params):

    angle_in_degrees = np.array(angle_in_degrees)

    if ri_model not in get_ri_model_names():
        return print("The refractive index profile model has been incorrectly chosen")

    if 'angle_offset' in params:
        angle_in_degrees = angle_in_degrees + params['angle_offset']

    ri_params = get_ri_params(ri_model,params)

    angle_in_radians = to_angle_in_radians(angle_in_degrees)
    num_angles = len(angle_in_radians)
    iteration = 0
    rho = np.zeros(num_angles, dtype = np.complex)

    model_to_use = getattr(ri_models, ri_model)
    z_profile, n_profile = model_to_use(**ri_params)
    e_profile = n_profile ** 2
    e_slab_array = get_slab_array(e_profile)
    n_slab_array = sqrt(e_slab_array)
    dz_array = get_difference_array(z_profile)
    n_t_complex = complex(n_t[0], n_t[1])

    packed_n_array = get_packed_n_slab_array(n_i, n_t_complex, n_slab_array)

    for x in angle_in_radians:
        packed_q_array = get_packed_q_array(x, wavelength, packed_n_array)
        rho[iteration] = get_rho(packed_q_array, packed_n_array, dz_array)
        iteration += 1

    tol = 1e-8
    rho.real[abs(rho.real) < tol] = 1e-9
    rho.imag[abs(rho.imag) < tol] = 1e-9

    return rho

#returns rho for one angle#

def get_rho(packed_q_array, packed_n_array, dz_array):
    num_elements = len(packed_q_array)
    num_interfaces = num_elements - 1

    big_q_array = get_big_q_from_small_q(packed_q_array, packed_n_array)

    p = get_reflection_interface(big_q_array[:num_interfaces], big_q_array[1:])
    s = get_reflection_interface(packed_q_array[:num_interfaces], packed_q_array[1:])

    if num_interfaces == 1:
        rho = p / s
        return rho

    elif num_interfaces > 1:

        packed_dz_array = np.append([0],dz_array)
        beta = packed_q_array[:num_interfaces] * packed_dz_array * complex(0, 1)

        s_matrices = np.zeros([num_interfaces, 2, 2], dtype=complex)
        p_matrices = np.zeros([num_interfaces, 2, 2], dtype=complex)

        s_matrices[:, 0, 0] = exp(beta)
        s_matrices[:, 0, 1] = s * exp(beta)
        s_matrices[:, 1, 0] = s * exp(-beta)
        s_matrices[:, 1, 1] = exp(-beta)

        p_matrices[:, 0, 0] = exp(beta)
        p_matrices[:, 0, 1] = p * exp(beta)
        p_matrices[:, 1, 0] = p * exp(-beta)
        p_matrices[:, 1, 1] = exp(-beta)

        s_matrix_transfer = reduce(np.dot, s_matrices)
        p_matrix_transfer = reduce(np.dot, p_matrices)

        s_total = s_matrix_transfer[1, 0] / s_matrix_transfer[0, 0]
        p_total = p_matrix_transfer[1, 0] / p_matrix_transfer[0, 0]

        return p_total / s_total


# Fresnel terms to be used in analytic approximations

def fresnel_terms(angle_in_radians, wavelength, n_i, n_t):
    wn = get_wavenumber(wavelength)
    k = get_k(angle_in_radians, wn, n_i)
    small_q_i = get_small_q(k, wn, n_i)
    big_q_i = get_big_q_from_small_q(small_q_i, n_i)
    small_q_t = get_small_q(k, wn, n_t)
    big_q_t = get_big_q_from_small_q(small_q_t, n_t)

    e_i = to_dielectric(n_i)
    e_t = to_dielectric(n_t)

    rs_0 = get_reflection_interface(small_q_i, small_q_t)
    rp_0 = get_reflection_interface(big_q_i, big_q_t)

    return e_i, e_t, k, small_q_i, small_q_t, big_q_i, big_q_t, rs_0, rp_0


def get_rho_thin_film(angle_in_degrees,wavelength,n_i,n_t,difference,**params):

    angle_in_radians = to_angle_in_radians(angle_in_degrees)
    n_t_complex = complex(n_t[0], n_t[1])

    excess_1 = params.get("excess_1")
    excess_2 = params.get("excess_2")

    e_i, e_t, k,small_q_i, small_q_t, big_q_i, big_q_t, rs_0, rp_0 = fresnel_terms(angle_in_radians, wavelength, n_i, n_t_complex)

    k_prime = k ** 2 / (e_i * e_t)

    big_q_sum = (big_q_i + big_q_t)
    pf_1_prime = 2 * big_q_i * k_prime / big_q_sum ** 2
    pf_2_prime = 2 * big_q_i * k_prime ** 2 / big_q_sum ** 3
    pf_3_prime = 4 * big_q_i * big_q_t * k_prime / big_q_sum ** 2

    pf_i_1 = pf_1_prime / rs_0
    pf_r_1 = pf_2_prime / rs_0
    pf_r_2 = pf_3_prime / rs_0

    d_imag_1 = - pf_i_1 * excess_1

    d_real_1 = -pf_r_1 * excess_1 ** 2
    d_real_2 = pf_r_2 * excess_2
    d_rho = complex(0, 1) * d_imag_1 + d_real_1 + d_real_2

    if difference == "yes":
        return d_rho
    if difference == 'no':
        return d_rho+rp_0/rs_0


#auxiliary functions#

def get_slab_array(profile):
    if profile == []:
        return []
    else:
        left_side = profile[:-1]
        right_side = profile[1:]
        return (left_side + right_side) / 2

def get_difference_array(profile):
    if profile == []:
        return []
    else:
        left_side = profile[:-1]
        right_side = profile[1:]
        return right_side - left_side

def get_packed_n_slab_array(n_i, n_t, n_slab):
    if n_slab is None:
        n_slab = []
    packed_n_array = np.array([n_i, n_t])
    return np.insert(packed_n_array, -1, n_slab)

def get_packed_q_array(angle_in_radians, wavelength, packed_n_slab_array):
    wn = get_wavenumber(wavelength)
    k = get_k(angle_in_radians, wn, packed_n_slab_array[0])
    return get_small_q(k, wn, packed_n_slab_array)


def get_k(angle_in_radians, wn, n_incident):
    return wn * n_incident * sin(angle_in_radians)


def get_wavenumber(wavelength):
    out = 2 * pi / wavelength
    return out


def get_small_q(k, wn, n):
    angle_n = asin(k / (wn * n))
    out = wn * n * cos(angle_n)
    return out


def get_big_q_from_small_q(q, n):
    out = q / (n ** 2)
    return out


def get_reflection_interface(incident, transmitted):
    return (incident - transmitted) / (incident + transmitted)


#conversions#

def to_dielectric(n):
    return n**2


def to_angle_in_radians(angle_in_degrees):
    out = deg2rad(angle_in_degrees)
    return out


def to_n_complex(n_real, n_imag):
        return complex(n_real,n_imag)


def rho_to_delta(rho):
    delta_in_radians = np.angle(rho)
    delta_in_degrees = rad2deg(delta_in_radians)
    delta_in_degrees = delta_in_degrees % 360.0
    return delta_in_degrees

def rho_to_psi(rho):
    tan_delta = np.abs(rho)
    delta_in_radians = atan(tan_delta)
    delta_in_degrees = rad2deg(delta_in_radians)
    return delta_in_degrees


def rho_to_imag(rho):
    return np.imag(rho)


def rho_to_real(rho):
    return np.real(rho)

def psi_delta_to_rho(psi_in_degrees, delta_in_degrees):

    psi = to_angle_in_radians(psi_in_degrees)
    delta = to_angle_in_radians(delta_in_degrees)
    rho = tan(psi)*cos(delta)+complex(0,1)*tan(psi)*sin(delta)
    return rho