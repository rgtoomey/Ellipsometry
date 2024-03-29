import numpy as np
import numpy.fft as fft
import matplotlib.pyplot as plt
import pandas

cos = np.cos
sin = np.sin
pi = np.pi

def intensity(A_deg,P_deg,psi_deg,delta_deg,c_offset=0):

    pr = pi/2
    C_degrees = np.arange(0,360,.01)+c_offset
    C = np.deg2rad(C_degrees)

    A,P,psi,delta = [np.deg2rad(i) for i in [A_deg,P_deg,psi_deg, delta_deg]]

    a0 = (1/2)*(1+cos(pr))*(cos(2*A)*cos(2*P)-cos(2*P)*cos(2*psi)+sin(2*A)*sin(2*P)*sin(2*psi)*cos(delta))-cos(2*A)*cos(2*psi)+1
    a2c = -sin(2*A)*sin(2*P)*sin(pr)*sin(2*psi)*sin(delta)
    a2s = sin(2*A)*cos(2*P)*sin(pr)*sin(2*psi)*sin(delta)
    a4c = 1/2*(1-cos(pr))*(cos(2*A)*cos(2*P)-cos(2*P)*cos(2*psi)-sin(2*A)*sin(2*P)*sin(2*psi)*cos(delta))
    a4s = 1/2*(1-cos(pr))*(cos(2*A)*sin(2*P)-sin(2*P)*cos(2*psi)+sin(2*A)*cos(2*P)*sin(2*psi)*cos(delta))

    print(a0,a2c,a4c,a2s,a4s)

    out = a0+a2c*cos(2*C)+a2s*sin(2*C)+a4c*cos(4*C)+a4s*sin(4*C)
    plt.plot(abs(C_degrees),out)
    plt.show()
    return

def get_fourier(data):

    out = fft(data)

    dc = out[0]
    c2 = out[2].real
    c4 = out[4].real
    s2 = out[2].imag
    s4 = out[4].imag

    return dc,c2,c4,s2,s4
