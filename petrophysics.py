"""
Petrophysical Calculation Library for Well Log Analysis.

Provides functions to compute:
- Shale Volume (Vshale) via Linear, Steiber, Larionov, and Clavier equations
- Density Porosity (PHID)
- Sonic Porosity (PHIS) via Wyllie and Raymer-Hunt-Gardner (RHG) equations
- Neutron-Density Combination Porosity (PHIND) via RMS and Average methods
- Effective Porosity (PHIE)
"""

import numpy as np
import pandas as pd

def calculate_vshale(gr, gr_sand, gr_shale, method='linear'):
    """
    Calculate Shale Volume (Vshale) from Gamma Ray log.

    Parameters:
    -----------
    gr : array-like or float
        Gamma Ray log values (API).
    gr_sand : float
        Clean sand baseline GR value (API).
    gr_shale : float
        Pure shale baseline GR value (API).
    method : str, default 'linear'
        Method for Vshale calculation:
        - 'linear': Linear Gamma Ray index
        - 'steiber': Steiber non-linear model
        - 'larionov_young': Larionov model for Tertiary (soft) rocks
        - 'larionov_old': Larionov model for Mesozoic/Paleozoic (older) rocks
        - 'clavier': Clavier non-linear model

    Returns:
    --------
    vsh : array-like or float
        Shale volume fraction (0.0 to 1.0).
    """
    igr = (gr - gr_sand) / (gr_shale - gr_sand)
    igr = np.clip(igr, 0.0, 1.0)
    
    if method == 'linear':
        vsh = igr
    elif method == 'steiber':
        vsh = igr / (3.0 - 2.0 * igr)
    elif method == 'larionov_young':
        vsh = 0.083 * (2.0**(3.7 * igr) - 1.0)
    elif method == 'larionov_old':
        vsh = 0.33 * (2.0**(2.0 * igr) - 1.0)
    elif method == 'clavier':
        vsh = 1.7 - np.sqrt(np.maximum(0, 3.38 - (igr + 0.7)**2))
    else:
        raise ValueError(f"Unknown method: {method}")
        
    return np.clip(vsh, 0.0, 1.0)


def calculate_density_porosity(rhob, rho_ma=2.65, rho_f=1.0):
    """
    Calculate Density Porosity (PHID).

    Parameters:
    -----------
    rhob : array-like or float
        Bulk density log values (g/cm^3).
    rho_ma : float, default 2.65
        Matrix density (g/cm^3). Sandstone=2.65, Limestone=2.71, Dolomite=2.87.
    rho_f : float, default 1.0
        Fluid density (g/cm^3). Fresh water=1.0, Salt water=1.1.

    Returns:
    --------
    phid : array-like or float
        Density porosity fraction (0.0 to 1.0).
    """
    phid = (rho_ma - rhob) / (rho_ma - rho_f)
    return np.clip(phid, 0.0, 1.0)


def calculate_sonic_porosity(dt, dt_ma=55.5, dt_f=189.0, method='wyllie'):
    """
    Calculate Sonic Porosity (PHIS).

    Parameters:
    -----------
    dt : array-like or float
        Sonic transit time log values (us/ft).
    dt_ma : float, default 55.5
        Matrix transit time (us/ft). Sandstone=55.5, Limestone=47.5, Dolomite=43.5.
    dt_f : float, default 189.0
        Fluid transit time (us/ft). Fresh water=189.0, Salt water=185.0.
    method : str, default 'wyllie'
        Formula to use: 'wyllie' (Wyllie time-average) or 'rhg' (Raymer-Hunt-Gardner).

    Returns:
    --------
    phis : array-like or float
        Sonic porosity fraction (0.0 to 1.0).
    """
    if method == 'wyllie':
        phis = (dt - dt_ma) / (dt_f - dt_ma)
    elif method == 'rhg':
        phis = 0.625 * (dt - dt_ma) / dt
    else:
        raise ValueError(f"Unknown method: {method}")
        
    return np.clip(phis, 0.0, 1.0)


def calculate_neutron_density_porosity(nphi, phid, method='rms'):
    """
    Calculate Combination Neutron-Density Porosity (PHIND).

    Parameters:
    -----------
    nphi : array-like or float
        Neutron porosity log values (fraction).
    phid : array-like or float
        Density porosity log values (fraction).
    method : str, default 'rms'
        Method to combine neutron and density porosity:
        - 'rms': Root-mean-square combination sqrt((nphi^2 + phid^2) / 2)
        - 'average': Simple arithmetic mean (nphi + phid) / 2

    Returns:
    --------
    phind : array-like or float
        Neutron-density combination porosity fraction (0.0 to 1.0).
    """
    if method == 'rms':
        phind = np.sqrt((np.maximum(nphi, 0)**2 + np.maximum(phid, 0)**2) / 2.0)
    elif method == 'average':
        phind = (nphi + phid) / 2.0
    else:
        raise ValueError(f"Unknown method: {method}")
        
    return np.clip(phind, 0.0, 1.0)


def calculate_effective_porosity(phit, vsh, phi_shale=0.10):
    """
    Calculate Effective Porosity (PHIE) by correcting total porosity for shale content.

    Parameters:
    -----------
    phit : array-like or float
        Total porosity fraction (e.g. PHIND).
    vsh : array-like or float
        Shale volume fraction (0.0 to 1.0).
    phi_shale : float, default 0.10
        Porosity of pure shale.

    Returns:
    --------
    phie : array-like or float
        Effective porosity fraction (0.0 to 1.0).
    """
    phie = phit - (vsh * phi_shale)
    return np.clip(phie, 0.0, 1.0)


def compute_all_petrophysical_properties(df, gr_sand=None, gr_shale=None, rho_ma=2.65, rho_f=1.0, dt_ma=55.5):
    """
    Computes Vshale, PHID, PHIS, PHIND, and PHIE for a well log DataFrame.

    Returns:
    --------
    data : pandas.DataFrame
        Copy of input DataFrame with added porosity and shale volume columns.
    """
    data = df.copy()
    
    if gr_sand is None:
        gr_sand = np.percentile(data['GR'].dropna(), 5)
    if gr_shale is None:
        gr_shale = np.percentile(data['GR'].dropna(), 95)
        
    data['VSH_linear'] = calculate_vshale(data['GR'], gr_sand, gr_shale, method='linear')
    data['VSH_steiber'] = calculate_vshale(data['GR'], gr_sand, gr_shale, method='steiber')
    
    if 'RHOB' in data.columns:
        data['PHID'] = calculate_density_porosity(data['RHOB'], rho_ma=rho_ma, rho_f=rho_f)
        
    if 'DT' in data.columns:
        data['PHIS'] = calculate_sonic_porosity(data['DT'], dt_ma=dt_ma, method='wyllie')
        
    if 'NPHI' in data.columns and 'PHID' in data.columns:
        data['PHIND'] = calculate_neutron_density_porosity(data['NPHI'], data['PHID'], method='rms')
        
    if 'PHIND' in data.columns and 'VSH_linear' in data.columns:
        data['PHIE'] = calculate_effective_porosity(data['PHIND'], data['VSH_linear'], phi_shale=0.10)
        
    return data
