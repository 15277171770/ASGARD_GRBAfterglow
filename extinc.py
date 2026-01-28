from extinction import fitzpatrick99 as f99
import numpy as np
from extinction_cur import get_abs

def opt_extinction(mag_data,mag_err,frequency,Rv,Ebv,zeropointflux):
    
    wave = np.array([2.997e10/frequency*1e8])
    Av = Rv * Ebv
    
    mag_data_deredden = mag_data - f99(wave, Av, Rv)
    flux_data_deredden = 10**(0.4*(zeropointflux-mag_data_deredden))
    flux_data_err = 0.4*np.log(10.0)*flux_data_deredden*mag_err
    
    
    return flux_data_deredden, flux_data_err
    
    
def opt_extinction_zhou(mag_data,mag_err,frequency,Rv,Ebv,zeropointflux,redshift,Lyman_Ar):
    
    wave_in_mu_m = np.array([2.997e10/frequency*1e4])
    Av = Rv * Ebv
    
    mag_data_deredden = mag_data - get_abs(wave_in_mu_m, Av, redshift, Lyman_Ar)
    flux_data_deredden = 10**(0.4*(zeropointflux-mag_data_deredden))
    flux_data_err = 0.4*np.log(10.0)*flux_data_deredden*mag_err
    
    return flux_data_deredden, flux_data_err
    
def opt_extinction_pei92(mag_data,mag_err,frequency,model,Rv,Ebv,zeropointflux,redshift):
    
    wave_in_mu_m = np.array([2.997e10/frequency*1e4])
    wave_in_mu_m_redshift = wave_in_mu_m / (1.0 + redshift)
    
    mag_data_deredden = mag_data - pei92(wave_in_mu_m_redshift, Rv, Ebv, model) - pei92(wave_in_mu_m, 3.08, 0.29, 'MW')
    flux_data_deredden = 10**(0.4*(zeropointflux-mag_data_deredden))
    flux_data_err = 0.4*np.log(10.0)*flux_data_deredden*mag_err

    return flux_data_deredden, flux_data_err
    
import math
def pei92(wave_in_mu_m, Rv, Ebv, model='SMC') -> float:
    """
    ported from XSPEC originally by
    Martin.Still@gsfc.nasa.gov

    """

    if model=='MW':
        a=np.array([165.0, 14.0, 0.045, 0.002, 0.002, 0.012])
        lamb=np.array([0.047, 0.08, 0.22, 9.7, 18.0, 25.0])
        b=np.array([90.0, 4.0, -1.95, -1.95, -1.8, 0.0])
        n=np.array([2.0, 6.5, 2.0, 2.0, 2.0, 2.0])

    if model=='LMC':
        a=np.array([175.0, 19.0, 0.023, 0.005, 0.062, 0.02]),
        lamb=np.array([0.046, 0.08, 0.22, 9.7, 18.0, 25.0]),
        b=np.array([90.0, 5.5, -1.95, -1.95, -1.8, 0.0]),
        n=np.array([2.0, 4.5, 2.0, 2.0, 2.0, 2.0]),


    if model=='SMC':
        a=np.array([185.0, 27.0, 0.005, 0.01, 0.012, 0.03]),
        lamb=np.array([0.042, 0.08, 0.22, 9.7, 18.0, 25.0]),
        b=np.array([90.0, 5.5, -1.95, -1.95, -1.8, 0.0]),
        n=np.array([2.0, 4.0, 2.0, 2.0, 2.0, 2.0]),

    a_b = Ebv * (1.0 + Rv)

    # compute terms of sum

    ratio = wave_in_mu_m / lamb

    term = np.power(ratio, n)

    inv_term = 1.0 / term

    bottom = term + inv_term + b

    xi = np.sum(a / bottom)

    # remove a_b normalization on the extinction curve
    a_lambda = a_b * xi
    
    return a_lambda
    

