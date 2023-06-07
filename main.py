import elli_fit as fit
import lmfit

model_func = fit.model_to_fit("single",632.8,"silicon",1.0)

gmodel = lmfit.Model(model_func)

params = gmodel.make_params()

params.add("n_avg", value = 1.5, vary = False)
params.add("width", value = 10, vary = False)
angles = [*range(1,91,1)]

rho_eval = gmodel.eval(params, angle_in_degrees = angles)

print("hey")