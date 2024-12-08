import numpy as np
import statsmodels.robust as rb
from scipy import stats

def all_floats_approx_equal(lst, tolerance=1e-8):
    base_value = lst[0]
    
    for value in lst[1:]:
        if abs(value - base_value) > tolerance:
            return False
    
    return True

def statistics(values):
    maxium = max(values)
    minium = min(values)
    range_ = maxium - minium 
    midrange = (maxium+minium)*0.5
    mean = np.mean(values)
    std = np.std(values)
    var = np.var(values)
    be_mid,mid,fomid = np.percentile(values, [25, 50, 75])
    MAD = rb.scale.mad(values)
    variation = np.std(values)/np.mean(values)
    sum_ = sum(values)
    number = len(values)
    if number < 2:
        kurtosis = 3.0
        skew = 0.0
    elif all_floats_approx_equal(values):
        kurtosis = 3.0
        skew = 0.0
    else:
        kurtosis = stats.kurtosis(values)
        skew = stats.skew(values)
        kurtosis = 3.0 if np.isnan(kurtosis) else kurtosis
        skew = 0.0 if np.isnan(skew) else skew
    tilt = 0 if mean>mid else 1
    return [maxium, minium, range_, midrange, mean, std, var, be_mid, mid,
            fomid, MAD, variation, sum_, number, kurtosis, skew, tilt]


def amount_indicator(values):
    amounts_in = values['in']
    amounts_out = values['out']
    
    amounts_in_sum = sum(amounts_in)
    amounts_out_sum = sum(amounts_out)
    difference = amounts_in_sum - amounts_out_sum
    
    if len(amounts_in) != 0:
        maxium_in = max(amounts_in)
        minum_in = min(amounts_in)
        difference_in = maxium_in-minum_in
        std_in = np.std(amounts_in)
        mean_in = np.mean(amounts_in)
        variation_in = float(std_in)/mean_in
        var_in = np.var(amounts_in)
    else:
        maxium_in = 0
        minum_in = 0
        difference_in = 0
        std_in = 0
        mean_in = 0
        variation_in = 0
        var_in = 0

    if len(amounts_out) != 0:
        maxium_out = max(amounts_out)
        minum_out = min(amounts_out)
        difference_out = maxium_out-minum_out
        difference_in_out = difference_in-difference_out
        std_out = np.std(amounts_out)
        mean_out = np.mean(amounts_out)
        variation_out = float(std_out)/mean_out
        var_out = np.var(amounts_out)
    else:
        maxium_out = 0
        minum_out = 0
        difference_out = 0
        difference_in_out = 0
        std_out = 0
        mean_out = 0
        variation_out = 0
        var_out = 0

    return [amounts_in_sum, amounts_out_sum, difference, maxium_in, minum_in,
            difference_in, maxium_out, minum_out, difference_out, difference_in_out, 
            std_in, std_out, mean_in, mean_out, var_in, var_out, variation_in, variation_out]


def tx_degree_indicator(tx_embedding):
    in_degree = 0
    out_degree = 0
    for inner_key in tx_embedding['in'].keys():
        in_degree+=1
    for inner_key in tx_embedding['out'].keys():
        out_degree+=1
    
    all_degree = in_degree + out_degree
    difference = in_degree - out_degree

    return [in_degree, out_degree, all_degree, difference]

def addr_degree_indicator(data_in, data_out):
    in_degree = len(set(data_in['block']))
    out_degree = len(set(data_out['block']))
    
    all_degree = in_degree + out_degree
    difference = in_degree - out_degree

    return [in_degree, out_degree, all_degree, difference]


def time_indicator(istx, data):
    if istx:
        return [0]
    else:
        tss = list(data['ts'])
        max_ts = max(tss)
        min_ts = min(tss)
        life = (max_ts - min_ts) / 86400000
        return [life]

