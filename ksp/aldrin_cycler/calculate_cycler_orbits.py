#!/usr/bin/python3

import numpy as np

def find_orbits(SMA_inner, SOI_inner, T_synod, T_inner, n_mult=1, n=None):
    modulo = np.modf(T_synod)[0]
    n_round = 1 / modulo
    if n is None:
        n = n_round * n_mult
    n_periods = T_synod * n_round
    cycle_length = n_periods * T_inner

    r = np.arange(1, n_periods)
    peri = SMA_inner - SOI_inner * 1.01

    P = cycle_length * n / (n_round * r + n % n_round)
    a = (P/T_inner) ** (2/3) * SMA_inner
    e = 1 - peri / a
    apo = a * (1 + e)
    p = a * (1 - e**2)
    omega = np.arccos((p - SMA_inner) / (SMA_inner * e))

    result = np.column_stack([p, apo, omega])
    print(result)
    return result

kerbin_sma = 13599840256  # metres
kerbin_soi = 84159286  # metres
kerbin_year = 106.5  # days

find_orbits(kerbin_sma, kerbin_soi, 2+1/7, kerbin_year)  # Kerbin with an almost Duna
