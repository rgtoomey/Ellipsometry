import numpy as np
import ri_models
from functools import reduce

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

#Ellipsometry rho modeling#

def get_rho_from_model(model,angle_in_degrees,wavelength,n_i,n_t,**params):

    model_to_use = getattr(ri_models,model)
    z_profile,n_profile = model_to_use(**params)
    e_profile = n_profile**2
    e_slab_array = get_slab_array(e_profile)
    n_slab_array = sqrt(e_slab_array)
    dz_array = get_difference_array(z_profile)
    n_t_complex=complex(n_t[0], n_t[1])

    packed_n_array = get_packed_n_slab_array(n_i, n_t_complex, n_slab_array)
    angle_in_radians = to_angle_in_radians(angle_in_degrees)
    num_angles = len(angle_in_radians)

    rho = np.zeros(num_angles, dtype = np.complex)

    i = 0
    for x in angle_in_radians:
        packed_q_array = get_packed_q_array(x, wavelength, packed_n_array)
        rho[i] = get_rho(packed_q_array, packed_n_array, dz_array)
        i += 1

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