import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
_HAS_COLORCET = False
try:
    import colorcet as cc
    _HAS_COLORCET = True
except ImportError:
    pass

if _HAS_COLORCET:
    default_cmap = cc.cm.CET_L17
else:
    default_cmap = "inferno"


def plot_flups(t, wl, z,
               vmin=0, vmax=None, cmap=default_cmap,
               levels=None, scatter_mask = None, filter=[3,1], lev_colors=None,
               ax=None):
    assert z.shape == (wl.size, t.size)
    ax = plt.gca() if ax is None else ax
    vmax = np.percentile(z, 99) if vmax is None else vmax
    scatter_mask = np.full_like(wl, True) if scatter_mask is None else scatter_mask
    art = []
    art.append(
        plt.pcolormesh(t, wl, z, vmin=vmin, vmax=vmax, cmap=cmap)
    )
    cb = plt.colorbar(label="$S_\mathrm{F}$")
    art.append(cb)
    if levels is None:
        # try to provide a default
        step = (vmax-vmin)/10
        levels = np.arange(0, 20)*step+vmin
    if len(levels)>0:
        if filter is not None and len(filter)>0:
            cnt = gaussian_filter(z, filter)
        else:
            cnt = z
        cnt = cnt.compress(scatter_mask, axis=0)
        wl_cnt = wl.compress(scatter_mask)
        if lev_colors is None:
            lev_colors = ["w" for v in levels]
            lev_colors[0] = "0.85"
        lines = plt.contour(t, wl_cnt, cnt, levels=levels, colors=lev_colors, linewidths=0.5)
        cb.add_lines(lines)
        art.append(lines)
    return art

