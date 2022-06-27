## This script calculates evaporation rate for lakes
## by: Gang Zhao
## 04/01/2020

from math import log, exp, sqrt, pow
from math import sin, cos, tan, atan
from math import pi, acos

def del_calc(ta):
    # slope of the saturation water vapour curve 
    # at the temperatures (kPa deg C-1)
    
    ea = 0.6108*exp(17.27*ta/(ta+237.3))
    delcalc = 4098*ea/pow((ta+237.3),2.)
    return delcalc


def airdens(ta, elev):
    # airds is air density (kg/m3) at elev (m) and ta (C) 
    # https://en.wikipedia.org/wiki/Density_of_air#Altitude 
    # p, p0     sea level standard atmospheric pressure, 101.325 kPa 
    # g         earth-surface gravitational acceleration, 9.80665 m/s2 
    # r         ideal (universal) gas constant, 8.31447 J/(mol K) 
    # m         molar mass of dry air, 0.0289644 kg/mol 
    # t0, l     temperature lapse rate, 0.0065 K/m 
    p0 = 101.325
    g = 9.80665
    r = 8.31447
    m = 0.0289644
    l = 0.0065
    
    ta = ta+273.15     ## celsius to kelvin 
    t0 = ta+l*elev
    p = p0*pow(1-l*elev/t0,g*m/r/l)*1000.0     # in Pa 
    airds = p*m/r/ta
    airds = 1.225 if airds>1.225 else airds
    return airds


def cloud_factor(srad, mth, lat, elev):
    # srad is incoming shortwave radiation (MJ/m2/d) and M is the month 
    # J, omega, delta, dr
    # Kso, Ket, Kr, fcd
    # lat_r
    
    J = (int)(30.4*mth-15)
    delta = 0.409*sin(2.*pi*J/365. - 1.39)
    lat_r = lat/180.*pi
    omega_input = -tan(lat_r)*tan(delta)
    if abs(omega_input) < 1:                    ## Polar night
        omega = acos(omega_input)
        dr = 1.+0.033*cos(2.*pi/365.*J)
        
        Ket = 24./pi*4.92*dr*(omega*sin(lat_r)*sin(delta) + cos(lat_r)*cos(delta)*sin(omega))
        Kso = (0.75+2e-5*elev)*Ket
        Kr = srad/Kso
        
        Kr=1. if Kr > 1. else Kr
        Kr=0. if Kr < 0. else Kr
        
        fcd = 1. - Kr
    else:
        fcd = 0
    
    return fcd


def equilibrim(lat, depth, elev, area, srad, lrad, ta, vpd, ut, tw0, fch, mth):
    
    # INPUT
    # lat  :  latitude (deg)
    # depth:  average depth (m)
    # elev :  water surface elevation (m)
    # area :  water surface area (km2)
    # srad :  surface downward shortwave radiation (W/m2)
    # lrad :  surface downward longwave radiation (W/m2)
    # ta   :  air temperature at 2m height (degC)
    # vpd  :  vapor pressure deficit (kPa)
    # ut   :  wind speed at 2m height (m/s)
    # tw0  :  water column temperature at previous time step (degC)
    # fch  :  fetch length (m)
    # mth  :  month (1 to 12)
    
    # OUTPUT
    # evap_hs: evaporation rate considering heat storage (mm/d)
    # evap_nohs: evaporation rate without considering heat storage (mm/d)
    # ierr: error code
    
    # initialize constants
    waterds = 1000.0
    cw = 0.0042
    ca = 1.013
    sigma = 4.9e-9
    T_abs = 273.15
    alb = 0.1
    tstep = 30
    
    ierr = 0
    ### check input data errors
    ierr = 1 if alb <= 0.0 or alb >= 1.0 else ierr
    ierr = 2 if depth <= 0 else ierr
    
    depth_calc = 4.6*pow(area, 0.205)
    depth = depth if depth<depth_calc else depth_calc
    # depth = 20.0 if depth>20.0 else depth
    
    fch = 10000 if fch > 10000 else fch
    
    ierr = 3 if srad <= 0. else ierr
    [ierr, ut] = [4, 0.01] if ut <= 0.01 else [ierr, ut]
    [ierr, vpd] = [5, 0.0001] if vpd <= 0.0 else [ierr, vpd]
    
    es = 0.6108*exp(17.27*ta/(ta+237.3))
    [ierr, vpd] = [6, es*0.99] if es <= vpd else [ierr, vpd]
    ea = es - vpd
    
    t_d = (116.9+237.3*log(ea))/(16.78-log(ea))
    twb = (0.00066*100.*ta + 4098.*(ea)/pow(t_d+237.3,2)*t_d) \
          /(0.00066*100.+4098.*(ea)/pow(t_d+237.3,2.))
    
    [ierr, twb] = [7, ta] if twb > ta else [ierr, twb]
    
    ##############################################################################################
    ########################### Calculate water equilibrium temperature ##########################
    ##############################################################################################
    
    ## some variables
    alambda = 2.501-ta*2.361e-3
    atmp=101.3*pow((273.15 + ta -0.0065*elev)/(273.15 + ta),5.26)
    gamma=0.00163*atmp/alambda
    airds = airdens(ta, elev)
    
    ## slope of the saturation water vapour curve at the temperatures (kPa deg C-1) 
    deltaa = del_calc(ta)
    deltawb=del_calc(twb)
    
    ## Emissvity of air and water (unitless)
    sradj = srad*0.0864                                     ## convert from W m-2 to MJ m-2 d-1
    
    fcd = cloud_factor(sradj, mth, lat, elev)
    em_a = 1.08*(1.-exp(-pow(ea*10.,(ta+T_abs)/2016.)))*(1+0.22*pow(fcd,2.75))
    em_w=0.97
    
    lradj = em_a*sigma*pow((ta+T_abs),4.) if lrad == -9999 else lrad*0.0864
    
    ## wind function using the method of McJannet, 2012 (MJ m-2 d-1 kPa-1)    
    windf = (2.33+1.65*ut)*pow(fch, -0.1)*alambda
    
    ## calculate equilibrium temperature of the water body (C) Zhao and Gao */
    te = ((0.46*em_a+windf*(deltaa+gamma))*ta + (1.-alb)*sradj - 28.38*(em_w-em_a) -windf*vpd) \
         /(0.46*em_w+windf*(deltaa+gamma))
    
    ###############################################################################################
    ############################## Calculate water column temperature #############################
    ###############################################################################################
    
    ## time constant (d) 
    tau = (waterds*cw*depth)/(4.0*sigma*pow((twb+T_abs),3.)+windf*(deltawb+gamma))
    
    ## water column temperature (deg. C) 
    tw = te+(tw0-te)*exp(-tstep/tau)
    tw = 0. if tw<0. else tw
    
    ## change in heat storage (MJ m-2 d-1)
    heat_stg = waterds*cw*depth*(tw-tw0)/tstep
    
    ################################################################################################
    ################################### Calculate the evaporation ##################################
    ################################################################################################
    
    ## calculate the Penman evaporation
    rn = sradj*(1.-alb)+lradj-em_w*(sigma*pow((ta+T_abs),4.))
    
    le = (deltaa*(rn-heat_stg)+gamma*windf*vpd)/(deltaa+gamma)
    evap_hs = le/alambda
    evap_hs = 0 if evap_hs < 0 else evap_hs
    
    le = (deltaa*(rn)+gamma*windf*vpd)/(deltaa+gamma)
    evap_nohs = le/alambda
    evap_nohs = 0 if evap_nohs < 0 else evap_nohs
    
    return [evap_hs, evap_nohs, ierr]

### An example ##
lat   = 32.085 ## deg
depth = 18.35  ## m
elev  = 171.24 ## m
area  = 75     ## km2
srad  = 207.27 ## W/m2
lrad  = -9999  ## W/m2
ta    = 16.56  ## degC
vpd   = 0.91   ## kPa
ut    = 3.426  ## m/s
tw0   = 11.63  ## degC
fch   = 5200   ## m
mth   = 3

print(equilibrim(lat, depth, elev, area, srad, lrad, ta, vpd, ut, tw0, fch, mth))
