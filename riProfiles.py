import numpy as np

tanh = np.tanh

def linear_profile(n_avg,width,dn):
    if width == 0:
        z_profile = np.array([])
        n_profile = np.array([])
        return z_profile,n_profile
    elif width > 0:
        dz = 0.1
        num_pts = int(np.ceil(width / dz) + 1)
        z_profile = np.linspace(0, width, num_pts)
        z_modified = z_profile / width - 1 / 2
        n_profile = n_avg + dn * z_modified
        return z_profile,n_profile

def tanh_profile(n_avg,width,dn,sigma):
    if width == 0:
        z_profile = np.array([])
        n_profile = np.array([])
        return z_profile, n_profile
    elif width > 0:
        dz = 0.1
        num_pts = int(np.ceil(width / dz) + 1)
        z_profile = np.linspace(0, width, num_pts)
        z_modified = z_profile / width - 1 / 2
        n_profile = n_avg + dn/2 * tanh(4*z_modified*width/sigma)
    return z_profile, n_profile


def single(n_avg, width):
    z_profile = np.array([0,width],dtype=float)
    n_profile = np.copy(z_profile)
    n_profile[0] = n_avg
    n_profile[1] = n_avg
    return z_profile,n_profile

def single_weak(n_avg, width):
    if width == 0:
        z_profile = np.array([])
        n_profile = np.array([])
        return z_profile,n_profile
    elif width > 0:
        dz = 0.1
        num_pts = int(np.ceil(width / dz) + 1)
        z_profile = np.linspace(0, width, num_pts)
        num_pts = len(z_profile)
        n_profile = np.full(num_pts, n_avg)
        return z_profile,n_profile

def double(n_avg_1,width_1,n_avg_2,width_2):
    interface_width = 0.001
    z_profile = np.array([0,width_1,width_1+interface_width,width_1+width_2],dtype=float)
    n_profile = np.copy(z_profile)
    n_profile[0] = n_avg_1
    n_profile[1] = n_avg_1
    n_profile[2] = n_avg_2
    n_profile[3] = n_avg_2
    return z_profile,n_profile

def double_weak(n_avg_1,width_1,n_avg_2,width_2):

    dz = 0.1
    num_pts_1 = int(np.ceil(width_1 / dz) + 1)
    z_profile_1 = np.linspace(0, width_1, num_pts_1)
    num_pts_2 = int(np.ceil(width_2 / dz) + 1)
    z_profile_2 = np.linspace(0, width_2, num_pts_2)+z_profile_1[-1]

    num_pts_1 = len(z_profile_1)
    num_pts_2 = len(z_profile_2)

    n_profile_1 = np.full(num_pts_1, n_avg_1)
    n_profile_2 = np.full(num_pts_2, n_avg_2)

    z_profile = np.append(z_profile_1,z_profile_2)
    n_profile = np.append(n_profile_1,n_profile_2)

    return z_profile, n_profile



    z_profile = np.array([0,width_1,width_1+interface_width,width_1+width_2],dtype=float)
    n_profile = np.copy(z_profile)
    n_profile[0] = n_avg_1
    n_profile[1] = n_avg_1
    n_profile[2] = n_avg_2
    n_profile[3] = n_avg_2
    return z_profile,n_profile


def interface():
    num_pts = 0
    z_profile = np.array([])
    n_profile = np.array([])
    return z_profile,n_profile








