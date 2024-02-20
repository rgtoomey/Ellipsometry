import rho_simulation_functions as elli
def residual_tf(excess,n_f,n_i,substrate):

    n_t = complex(elli.get_n_t(substrate)[0],elli.get_n_t(substrate)[1])

    e_i = n_i**2
    e_t = n_t**2
    e_f = n_f**2

    guess = excess_slab(n_f,n_i,substrate)

    guessed = guess[1]/guess[0]**2
    expected = excess[1]/excess[0]**2

    return guessed-expected

def fit_tf(excess, n_i, substrate):
    def fit(n_f):
        return residual_tf(excess,n_f,n_i,substrate)
    return fit

def excess_slab(n_f,n_i,substrate):

    n_t = complex(elli.get_n_t(substrate)[0], elli.get_n_t(substrate)[1])

    e_i = n_i ** 2
    e_t = n_t ** 2
    e_f = n_f ** 2

    excess_1 = (e_i - e_f) * (e_f - e_t) / e_f
    excess_2 = (e_i / (e_i - e_t) * (e_i - e_f) * (e_f - e_t) ** 2 / e_f - 1 / 2 * (e_i - e_f) * (e_f - e_t))

    return [excess_1, excess_2]

def get_ratio(excess):

    return excess[1]/excess[0]**2




#excess_1 = l*(e_i-e_f)*(e_f-e_i)/e_f

#excess_2 = l^2*(e_i/(e_i-e_t) * (e_i-e_f)*(e_f-e_i)^2/e_f - 1/2*(e_i-e_f)*(e_f-e_i))

