import rho_simulation_functions as elli
import matplotlib.pyplot as plt
import numpy as np
import ri_models
import json

with open("substrate_list.json", 'r') as refractive_index_list:
    refractive_index_list = json.load(refractive_index_list)

name_of_substrates_list = refractive_index_list.keys()

class Simulation:

    def __init__(self,ri_model,n_i,substrate,**params):
        self.ri_model = ri_model
        self.substrate = substrate
        self.n_i = n_i
        self.params = params
        self.angles = [*range(1,91,1)]
        self.angles[-1] = 89.999
        self.wavelength = 632.8
        self.show_ri_profile()
        self.show_rho()
        self.show_psi_delta()

    def get_info(self):
        print("Refractive Index Profile: " + self.ri_model)
        print(self.wavelength)
        print(self.substrate)
        print(self.params)
        pass


    def reset(self):
        pass


    def show_ri_profile(self):
        z,n_f=self.ri_profile()
        plot_title = "Substrate: " + self.substrate
        fig = plt.figure(dpi=300, layout='constrained', figsize=(5, 5))
        axs = fig.subplots()
        axs.plot(z, n_f, linewidth=2)
        axs.set_ymargin(0.2)
        axs.set_xlabel('z (nm)', size=16)
        axs.set_ylabel('Refractive Index', size=16)
        axs.tick_params(axis='both', labelsize=12)
        axs.text(0.025, 0.95, plot_title, transform=axs.transAxes, size=12, ha="left")
        plt.show()


    def show_psi_delta(self):
        psi_array = self.psi(with_coating = "yes")
        delta_array = self.delta(with_coating = "yes")

        fig = plt.figure(dpi=300, layout='constrained', figsize=(5, 5))
        axs = fig.subplots()
        axs.tick_params(axis='both', labelsize=12)

        axs.set_xlabel('Angle of Incidence (deg)', size=16)
        axs.set_ylabel('Psi,Delta', size=16)
        axs.set_xticks([0, 15, 30, 45, 60, 75, 90])

        psi_line, = axs.plot(self.angles, psi_array, label="Psi (deg)", linewidth=2)
        delta_line, = axs.plot(self.angles, delta_array, label="Delta (deg)", linewidth=2)

        axs.legend(fontsize=10)
        plt.show()


    def show_rho(self, name_of_comparison="none", **kwargs):
        print("hello")
        n_t = self.n_transmitted(**kwargs)
        rho_eval = self.rho(type="difference",**kwargs)
        error = self.uncertainity(type="difference",**kwargs)

        real_rho = elli.rho_to_real(rho_eval)
        imag_rho = elli.rho_to_imag(rho_eval)

        plot_title = "Substrate: " + self.substrate
        z, nf = self.ri_profile()

        fig = plt.figure(dpi=300, layout='constrained', figsize=(5, 5))
        axs = fig.subplots()
        axs.tick_params(axis='both', labelsize=12)

        axs.set_xlabel('Angle of Incidence (deg)', size=16)
        axs.set_ylabel(r'$\rho - \rho_0$', size=16)
        axs.set_xticks([0, 15, 30, 45, 60, 75, 90])

        imag_line, = axs.plot(self.angles, imag_rho, label=r"$\mathrm{Im}(\rho-\rho_0)$", linewidth=2)
        axs.errorbar(self.angles, imag_rho, yerr=error.imag, fmt = "none",errorevery=(1,10),ecolor=imag_line.get_color())
        real_line, = axs.plot(self.angles, real_rho, label=r"$\mathrm{Re}(\rho-\rho_0)$", linewidth=2)
        axs.errorbar(self.angles, real_rho, yerr=error.real, fmt = "none",errorevery=(5,10),ecolor=real_line.get_color())


        if name_of_comparison == "none":
            pass
        elif name_of_comparison == "tf":
            rho_eval_analytic = self.d_rho_tf()
        elif name_of_comparison == "weak_t":
            rho_eval_analytic = self.d_rho_weak_t()
        else:
            return print("There is an error!")

        if "rho_eval_analytic" in locals():
            imag_rho_analytic = elli.rho_to_imag(rho_eval_analytic)
            axs.plot(self.angles, imag_rho_analytic, color=imag_line.get_color(),
                     label=r"$\mathrm{Im}(\rho-\rho_0)_{analytic}$", linestyle='dashed', linewidth=2)
            real_rho_analytic = elli.rho_to_real(rho_eval_analytic)
            axs.plot(self.angles, real_rho_analytic, color=real_line.get_color(),
                     label=r"$\mathrm{Re}(\rho-\rho_0)_{analytic}$", linestyle='dashed', linewidth=2)

        axs.legend(fontsize=10)
        plt.show()


    def n_transmitted(self,**kwargs):

        if "ri_over_ride" in kwargs:
            return kwargs["ri_over_ride"]
        else:
            return refractive_index_list[self.substrate]


    def rho(self,type = "coating",**kwargs):
        n_t = self.n_transmitted(**kwargs)
        if type == "coating":
            rho_eval = elli.get_rho_from_model(self.ri_model, self.angles, self.wavelength, self.n_i, n_t, **self.params)
            return rho_eval
        elif type == "no_coating":
            rho_eval = elli.get_rho_from_model("interface", self.angles, self.wavelength, self.n_i, n_t)
            return rho_eval
        elif type == "difference":
            rho_eval = elli.get_rho_from_model(self.ri_model, self.angles, self.wavelength, self.n_i, n_t, **self.params)\
                       - elli.get_rho_from_model("interface", self.angles, self.wavelength, self.n_i, n_t)
            return rho_eval


    def psi(self, with_coating = "yes",**kwargs):
        if with_coating == "yes":
            out = elli.rho_to_psi(self.rho(type="coating",**kwargs))
            return out
        elif with_coating == "no":
            out = elli.rho_to_psi(self.rho(type="no_coating",**kwargs))
            return out


    def delta(self, with_coating = "yes",**kwargs ):
        if with_coating == "yes":
            out = elli.rho_to_delta(self.rho(type="coating",**kwargs))
            return out
        elif with_coating == "no":
            out = elli.rho_to_delta(self.rho(type="no_coating",**kwargs))
            return out


    def uncertainity(self,type = "coating",**kwargs):

        if "d_psi" in kwargs:
            d_psi = kwargs.get("d_psi")
        else:
            d_psi = 0.01

        if "d_delta" in kwargs:
            d_delta = kwargs.get("d_delta")
        else:
            d_delta = 0.01

        b = np.pi / 180

        if type == "coating":
            psi_array = self.psi(with_coating="yes",**kwargs)
            delta_array = self.delta(with_coating="yes",**kwargs)
        elif type == "no_coating":
            psi_array = self.psi(with_coating="no",**kwargs)
            delta_array = self.delta(with_coating="no",**kwargs)
        elif type == "difference":
            error_coating=self.uncertainity(type="coating",**kwargs)
            error_no_coating=self.uncertainity(type="no_coating",**kwargs)
            d_re = np.sqrt(error_coating.real**2+error_no_coating.real**2)
            d_im = np.sqrt(error_coating.imag**2+error_no_coating.imag**2)
            return d_re+d_im*complex(1j)


        d_tan = abs(b*(np.cos(b*psi_array))**(-2)*d_psi)
        d_sin = abs(b*np.cos(b*delta_array)*d_delta)
        d_cos = abs(b*np.sin(b*delta_array)*d_delta)

        tan_term = np.tan(b*psi_array)
        sin_term = np.sin(b*delta_array)
        cos_term = np.cos(b*delta_array)

        f_im = tan_term*sin_term
        f_re = tan_term*cos_term
        d_im = np.sqrt(f_im**2*((d_tan/tan_term)**2+(d_sin/sin_term)**2))
        d_re = np.sqrt(f_re**2*((d_tan/tan_term)**2+(d_cos/cos_term)**2))

        return d_re+d_im*complex(1j)


    def ri_profile(self):
        function_to_call = getattr(ri_models, self.ri_model)
        z,n_f = function_to_call(**self.params)
        return z, n_f


    def dielectric_excess_functions(self,**kwargs):
        z,n_f = self.ri_profile()

        if z == []:
            excess_1 = 0
            excess_2 = 0
            excess_3 = 0
            return excess_1,excess_2,excess_3
        else:
            e_i = elli.to_dielectric(self.n_i)
            e_f = elli.to_dielectric(n_f)
            n_t = elli.to_n_complex(self.n_transmitted(**kwargs)[0],self.n_transmitted(**kwargs)[1])
            e_t = elli.to_dielectric(n_t)

            dielectric_excess = (e_i-e_f)*(e_f-e_t)/e_f

            excess_1 = np.trapz(dielectric_excess, x=z)

            excess_2a = excess_1 * np.trapz((e_f-e_t), x=z)*e_i/(e_i-e_t)

            e_f_slab = elli.get_slab_array(e_f)
            dz = elli.get_difference_array(z)

            inside_integral = np.append(0.0,np.cumsum(e_f_slab*dz))

            excess_2b =np.trapz(dielectric_excess * inside_integral,x=z)

            return excess_1,excess_2a,excess_2b


    def fresnel_terms(self,**kwargs):
        angle_in_radians = elli.to_angle_in_radians(self.angles)
        wn = elli.get_wavenumber(self.wavelength)
        n_t = elli.to_n_complex(self.n_transmitted(**kwargs)[0],self.n_transmitted(**kwargs)[1])

        e_i = elli.to_dielectric(self.n_i)
        e_t = elli.to_dielectric(n_t)
        k = elli.get_k(angle_in_radians, wn, self.n_i)
        small_q_i = elli.get_small_q(k, wn, self.n_i)
        big_q_i = elli.get_big_q_from_small_q(small_q_i,self.n_i)
        small_q_t = elli.get_small_q(k, wn, n_t)
        big_q_t = elli.get_big_q_from_small_q(small_q_t, n_t)

        rs_0 = elli.get_reflection_interface(small_q_i, small_q_t)
        rp_0 = elli.get_reflection_interface(big_q_i, big_q_t)

        return e_i, e_t, k, small_q_i, small_q_t, big_q_i, big_q_t, rs_0, rp_0


    def prefactors_tf(self,**kwargs):
        e_i, e_t, k, small_q_i, small_q_t, big_q_i, big_q_t, rs_0, rp_0 = self.fresnel_terms(**kwargs)
        k_prime = k**2/(e_i*e_t)
        big_q_sum = (big_q_i+big_q_t)

        pf_1_prime = 2*big_q_i*k_prime/big_q_sum**2

        pf_2_prime = 2*big_q_i*k_prime**2/big_q_sum**3

        pf_3_prime = 4*big_q_i*big_q_t*k_prime/big_q_sum**2

        pf_i_1 = pf_1_prime/rs_0
        pf_r_1 = pf_2_prime/rs_0
        pf_r_2 = pf_3_prime/rs_0

        return pf_i_1,pf_r_1,pf_r_2

    def leading_tf(self,order,**kwargs):
        e_i, e_t, k, small_q_i, small_q_t, big_q_i, big_q_t, rs_0, rp_0 = self.fresnel_terms(**kwargs)
        k_prime = k ** 2 / (e_i * e_t)
        big_q_sum = (big_q_i + big_q_t)

        pf_prime = 2*big_q_i*(k_prime**order)/(big_q_sum**(order+1))
        pf = pf_prime / rs_0
        excess_1, excess_2a, excess_2b = self.dielectric_excess_functions()
        return pf*(excess_1**order)


    def d_rho_tf(self,**kwargs):

            pf_i_1, pf_r_1, pf_r_2 = self.prefactors_tf(**kwargs)

            excess_1, excess_2a, excess_2b = self.dielectric_excess_functions(**kwargs)

            d_imag_1 = -pf_i_1 * excess_1

            d_real_1 = -pf_r_1 * excess_1 ** 2
            d_real_2 = pf_r_2 * (excess_2a - excess_2b)


            d_rho = complex(0,1)*d_imag_1 + d_real_1+ d_real_2

            return d_rho

    def moment_i(self, order,**kwargs):
        z_f, n_f = self.ri_profile()
        e_f = elli.to_dielectric(n_f)
        e_i = elli.to_dielectric(self.n_i)
        excess = (e_f - e_i) * (z_f ** order)
        out = np.trapz(excess, x=z_f)
        return out


    def moment_t(self, order,**kwargs):
        z_f, n_f = self.ri_profile()
        e_f = elli.to_dielectric(n_f)
        n_t = elli.to_n_complex(self.n_transmitted(**kwargs)[0], self.n_transmitted(**kwargs)[1])
        e_t = elli.to_dielectric(n_t)

        excess = (e_f - e_t) * (z_f ** order)

        out = np.trapz(excess, x=z_f)
        return out


    def d_rho_weak_t(self,**kwargs):
        num_terms = 100
        e_i, e_t, k, small_q_i, small_q_t, big_q_i, big_q_t, rs_0, rp_0 = self.fresnel_terms()

        d_rho = 0

        for term in range(1,num_terms+1):
            pf = (-2*complex(0,1))**term/np.math.factorial(term-1)
            fresnel_terms = big_q_i*big_q_t**(term-1.0)*(k**2/(e_i*e_t))*e_t**(term-2.0)*(e_i-e_t)/(big_q_i+big_q_t)**2
            moment = self.moment_t(term-1)
            d_rho = pf*fresnel_terms*moment/rs_0 + d_rho

        return d_rho


    def vary(self,param_name,value_low,value_high,num_points,angle,name_of_comparison = 'none'):
        fig = plt.figure(dpi=300, layout='constrained',figsize=(5,5))
        axs = fig.subplots()
        axs.tick_params(axis='both', labelsize=12)

        default_angles = self.angles

        if param_name != "n_t":
            default_value = self.params.get(param_name)

        self.angles = [angle]

        value_array = np.linspace(value_low, value_high, num = num_points)
        d_rho = np.zeros(num_points, dtype=np.complex)

        if name_of_comparison == 'tf' or name_of_comparison == "weak_t":
            d_rho_analytic = np.zeros(num_points, dtype = np.complex)

        i = 0

        for value in value_array:

            if param_name != "n_t":
                self.params.update({param_name:value})
                d_rho[i] = self.rho(type="difference")
                if name_of_comparison == "tf":
                    d_rho_analytic[i] = self.d_rho_tf()
                elif name_of_comparison == "weak_t":
                    d_rho_analytic[i] = self.d_rho_weak_t()
            elif param_name == "n_t":
                d_rho[i] = self.rho(type="difference",ri_over_ride = [value,0])
                if name_of_comparison == "tf":
                    d_rho_analytic[i] = self.d_rho_tf(ri_over_ride = [value,0])
                elif name_of_comparison == "weak_t":
                    d_rho_analytic[i] = self.d_rho_weak_t(ri_over_ride = [value,0])
            i+=1

        real_rho = elli.rho_to_real(d_rho)
        imag_rho = elli.rho_to_imag(d_rho)

        if param_name == "width":
            axs.set_xlabel("Coating Thickness (nm)", size=16)
        elif param_name == "sigma":
            axs.set_xlabel(r"$\sigma$ (nm)", size=16)
        elif param_name == "n_t":
            axs.set_xlabel("Substrate Refractive Index", size=16)
        else:
            axs.set_xlabel(param_name,size =16)

        axs.set_ylabel(r'$\rho - \rho_0$', size=16)

        imag_line, = axs.plot(value_array, imag_rho, label=r"$Im(\rho-\rho_0)$",linewidth=2)
        real_line, = axs.plot(value_array, real_rho, label=r"$Re(\rho-\rho_0)$",linewidth=2)



        if "d_rho_analytic" in locals():
            real_rho_analytic = elli.rho_to_real(d_rho_analytic)
            imag_rho_analytic = elli.rho_to_imag(d_rho_analytic)
            axs.plot(value_array, imag_rho_analytic, color=imag_line.get_color(),
                     label=r"$\mathrm{Im}(\rho-\rho_0)_{analytic}$",linestyle='dashed',linewidth=2)
            axs.plot(value_array, real_rho_analytic, color=real_line.get_color(),
                     label=r"$\mathrm{Re}(\rho-\rho_0)_{analytic}$",linestyle='dashed',linewidth=2)


        plot_title =  "Angle of Incidence: " + str(angle)+" degrees"
#        axs.text(0.025, 0.025, plot_title, transform=axs.transAxes, size=12, ha="left")

        axs.legend(fontsize=10)

        plt.show()
        self.angles = default_angles

        if param_name != "n_t":
            self.params.update({param_name: default_value})

        return print("Done!")

#function to compare simulation objects
def plot(labels, simulation_objects, plot_title = "none", comparison = "none", confidence_bars = "no"):

    print(len(labels))
    print(len(simulation_objects))
    if len(labels) != len(simulation_objects):
        return print("You do not have the right nuber of labels")

    fig_ri = plt.figure(dpi=300, layout='constrained',figsize=(5,5))
    fig_im = plt.figure(dpi=300, layout='constrained',figsize=(5,5))
    fig_re = plt.figure(dpi=300, layout='constrained',figsize=(5,5))

    ax_ri,ax_im,ax_re=fig_ri.subplots(), fig_im.subplots(), fig_re.subplots()

    ax_ri.set_ymargin(0.2)

    ax_ri.tick_params(axis='both', labelsize=12)
    ax_im.tick_params(axis='both', labelsize=12)
    ax_re.tick_params(axis='both', labelsize=12)

    ax_ri.set_xlabel('z (nm)',fontsize=16)
    ax_ri.set_ylabel('Refractive Index',size=16)
    ax_im.set_xlabel('Angle of Incidence (deg)',size=16)
    ax_im.set_ylabel(r'$Im(\rho - \rho_0)$',size=16)
    ax_re.set_xlabel('Angle of Incidence (deg)',size=16)
    ax_re.set_ylabel(r'$Re(\rho - \rho_0)$',size=16)

    for i in range(len(simulation_objects)):
        legend_label = labels[i]
        object = simulation_objects[i]

        z, nf = object.ri_profile()
        rho_out = object.rho(type="difference")
        real_rho=elli.rho_to_real(rho_out)
        imag_rho=elli.rho_to_imag(rho_out)

        ax_ri.plot(z, nf, label=legend_label, linewidth = 2 )
        imag_line,=ax_im.plot(object.angles, imag_rho, label=legend_label, linewidth = 2)
        real_line,=ax_re.plot(object.angles, real_rho, label=legend_label, linewidth = 2)

        if confidence_bars == "yes":
            error = object.uncertainity(type="difference")
            ax_im.errorbar(object.angles, imag_rho, yerr=error.imag, fmt="none", errorevery=(2*i, 10),
                         ecolor=imag_line.get_color())
            ax_re.errorbar(object.angles, real_rho, yerr=error.real, fmt="none", errorevery=(2*i, 10),
                         ecolor=real_line.get_color())

        if comparison == "none":
            pass
        elif comparison == "tf":
            rho_eval_analytic = object.d_rho_tf()
        elif comparison == "weak_t":
            rho_eval_analytic = object.d_rho_weak_t()
        else:
            return print("There is an error!")

        if "rho_eval_analytic" in locals():
            imag_rho_analytic = elli.rho_to_imag(rho_eval_analytic)
            ax_im.plot(object.angles, imag_rho_analytic, color=imag_line.get_color(),
                     label="", linestyle='dashed', linewidth=2)
            real_rho_analytic = elli.rho_to_real(rho_eval_analytic)
            ax_re.plot(object.angles, real_rho_analytic, color=real_line.get_color(),
                     label="", linestyle='dashed', linewidth=2)

    ax_im.set_xticks([0, 15, 30, 45, 60, 75, 90])
    ax_re.set_xticks([0, 15, 30, 45, 60, 75, 90])

    ax_ri.legend(fontsize=10)
    ax_im.legend(fontsize=10)
    ax_re.legend(fontsize=10)

    fig_ri.show()
    input("Press Enter to continue...")
    fig_im.show()
    input("Press Enter to continue...")
    fig_re.show()
