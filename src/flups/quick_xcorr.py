import numpy as np
import matplotlib.pyplot as plt
from glob import glob
import os.path as pth
from argparse import ArgumentParser
import lmfit
import logging
from scipy.stats import linregress
from numpy.polynomial import Polynomial

logging.basicConfig(
    format="%(levelname)5s | %(name)s: %(message)s",
    level=logging.INFO
)

def rescale(y):
    return y/np.max(np.abs(y))

def lineslope_analysis(trace, p, ax=0):
    gmodel = lmfit.models.GaussianModel()
    gmodel.set_param_hint("amplitude", min=0.0)#, max = 10*np.max(z)
    gmodel.set_param_hint("center", min=p[0], max=p[-1])
    gmodel.set_param_hint("sigma", max=(p[-1]-p[0])/2)
    def slicefit(y):
        pars = gmodel.make_params()
        pars["center"].set(value=p[np.argmax(y)])
        pars["sigma"].set(value=np.sqrt(np.cov(p, aweights=np.maximum(y,0))))
        pars["amplitude"].set(value=np.max(y)*pars["sigma"]/0.4)
        return np.array(list(gmodel.fit(y, pars, x=p).best_values.values()))
    return np.apply_along_axis(slicefit, ax, trace)

def read_asc(fname):
    with open(fname) as f:
        contents = f.read()
    start = contents.find("\n"*3)
    return np.loadtxt((ln for ln in contents[start:].splitlines() if ln), delimiter=",")

def load_asc_series(fnames, step=None, b0=0, b1=1):
    trace = [read_asc(fn)[:,1] for fn in fnames]
    assert np.allclose([t.size for t in trace], trace[0].size) # check they all have the same length
    trace = np.array(trace)
    step = step or float(fnames[0].split("_")[1][1:])
    n_pix = trace.shape[1]
    hd = (trace.shape[0]-1)/2
    assert hd % 1 == 0
    hd = int(hd)
    delays = np.arange(-hd, hd+1)*step
    pixels = np.arange(n_pix)
    wl = b0+b1*pixels
    return delays, wl, trace

def load_npz(fname, b0=0, b1=1):
    df = np.load(args.input)
    delays = df["delays"]
    trace = df["trace"]
    try:
        wl = df["wl"]
    except KeyError:
        logging.info("Could not find wavelengths in: %s, computing.", args.input)
        pix = np.arange(trace.shape[1])
        wl = b0 + b1*pix
    return delays, wl, trace

# wavelength calibration
# indexed by 1
a0 = 303.047
a1 = 0.122468
# indexed by 0
b0 = a0+a1
b1 = a1

parser = ArgumentParser(description="Quick analysis of XCorr trace.")
parser.add_argument("-l", "--lim", type=int, default=200, help="Limit spectral pixel")
# add possibility to specify timestep
# add possibility to specify wavelength calibrations
# add switch to save archive
# add option to set root name
parser.add_argument("-o", "--output", help="Output root name")
parser.add_argument("input", help="Input file name or pattern.")

args = parser.parse_args()

# determine file type
ext = pth.splitext(args.input)[1]
if  ext == ".asc":
    # collect asc files
    fnames = glob(args.input)
    delays, wl, trace = load_asc_series(fnames, b0=b0, b1=b1)
    args.output = args.output or fnames[0][:-8]
elif ext == ".npz":
    delays, wl, trace = load_npz(args.input, b0=b0, b1=b1)
    args.output = args.output or pth.splitext(args.input)[0]

assert trace.shape == (delays.size, wl.size)

# clip trace to roi
trace = trace[:,:args.lim]
wl = wl[:args.lim]
delays /= 1000

# compute projections
t_marg = rescale(trace.sum(axis=1))
wl_marg = rescale(trace.sum(axis=0))

# fits
fit_results = {}
# fit a gaussian to t_marg
t_model = lmfit.models.GaussianModel()
pars = t_model.guess(t_marg, delays)
fit_results["time"] = t_model.fit(t_marg, pars, x=delays)


# # perform peak line analysis, by fitting
wl_mask = wl_marg > 0.05
lineslope_params = lineslope_analysis(trace[:,wl_mask], delays).T # parameters are "amplitude", "center", "sigma"
mean_slope = np.average(np.gradient(lineslope_params[:,1], wl[wl_mask]), weights=lineslope_params[:,0])
#ls_fit = Polynomial.fit(lineslope_params[:,1], wl[wl_mask], deg=1, w=lineslope_params[:,0]).convert().coef
mean_width = np.average(lineslope_params[:,2], weights=lineslope_params[:,0])

# perform imperative peakline analysis, noisy,,,
# norm = trace.sum(axis=0)
# bcenter = np.sum(trace*delays[:,np.newaxis], axis=0)/trace.sum(axis=0)
# tsig = np.sqrt(np.sum(trace*(delays[:,np.newaxis]-bcenter[np.newaxis,:])**2, axis=0)/norm)


np.savez(
    args.output+".npz",
    delays=delays, wl=wl, trace=trace, t_marg=t_marg, wl_marg=wl_marg,
    #lineslope_params=lineslope_params
)

# plot
fig = plt.figure(constrained_layout=True, figsize=(7.2,4.8))
gs = fig.add_gridspec(2,2, width_ratios=(3,2))
axes = {}
axes["trace"] = fig.add_subplot(gs[:,0])
axes["time"] = fig.add_subplot(gs[0,1])
axes["spec"] = fig.add_subplot(gs[1,1])
#axes["hgram"] = axes["trace"].inset_axes([0.8, 0.1, 0.2, 0.2])
axes["cbar"] = axes["trace"].inset_axes([0.05, 0.05, 0.02, 0.2])

plt.sca(axes["trace"])
zlim = np.max(np.abs(trace))
heatmap = plt.pcolormesh(
    delays, wl, trace.T, shading="nearest",
    vmin=-zlim, vmax=zlim, cmap="seismic",
)
# hgram_ = plt.axes(
#     (0.6, 0.1, 0.3, 0.3), transform=plt.gca().transAxes
# )
# plt.grid(True, which="major", alpha=0.8)
# plt.grid(True, which="minor", alpha=0.5)
#plt.grid(True, which="both")
plt.plot(lineslope_params[:,1], wl[wl_mask], "k")
plt.plot(lineslope_params[:,1]+lineslope_params[:,2], wl[wl_mask], "k:")
plt.plot(lineslope_params[:,1]-lineslope_params[:,2], wl[wl_mask], "k:")
#plt.plot(delays, 310+delays/ls_fit[1])
lbl = r"""<gdd> = {:.02f} (fs/nm)
<$\sigma_t$> = {:.02f} (fs)
""".format(mean_slope*1000, mean_width*1000)
plt.text(
    0.55, 0.95, lbl,
    ha="left", va="top", fontsize="small",
    transform=plt.gca().transAxes,
    )
plt.xlabel("Delay (ps)")
plt.ylabel(r"$\lambda$ (nm)")

cb = plt.colorbar(heatmap, cax=axes["cbar"])
cb.set_label("Counts", labelpad=-20)#, fontsize="x-small")
#cb.set_labelpad(0)


#plt.sca(axes["hgram"])
# w, b = np.histogram(trace, bins=101)
# axes["hgram"].plot(w[10:], b[10:-1])
# plt.ylabel("counts")

plt.sca(axes["time"])
fr = fit_results["time"]
plt.plot(delays, rescale(t_marg), color="k", lw=1.5)
plt.plot(delays, fr.best_fit, "--", color="r", lw=1)
label = r"""t$_0$ = {:.02f} fs
$\sigma_t$ = {:.01f} fs
FWHM = {:.01f} fs""".format(
    fr.best_values["center"]*1000, 
    fr.best_values["sigma"]*1000, 
    fr.best_values["sigma"]*1000*2.355, 
)
plt.text(
    0.02, 0.95, label,
    ha="left", va="top", transform=plt.gca().transAxes,
    fontsize="x-small", weight="light",
)
plt.xlim(np.min(delays), np.max(delays))
plt.xlabel("Delay (ps)")


plt.sca(axes["spec"])
plt.plot(wl, rescale(wl_marg), color="k", lw=1)
plt.xlabel(r"$\lambda$ (nm)")
plt.xlim(np.min(wl), np.max(wl))

for ax in axes.values():
    ax.minorticks_on()

plt.savefig(args.output+".png", dpi=300)