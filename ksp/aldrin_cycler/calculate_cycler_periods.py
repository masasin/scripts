def calculate_periods(precision=1e-1, periods_to_check=1000, print_first_n=7):
    """Calculate optimal orbital periods for a Kerbin-Duna cycler.
    
    This assumes that the cyclers will have the same orbital period as the
    synodic period. Multiples of this period are also acceptable, but the
    results will need to be modified accordingly.
    
    All arguments are optional.

    Args:
        precision: Acceptable absolute error. Default is 0.1 (10.65 days)
        periods_to_check: Number of future cycles to check. Default is 1000.
        print_first_n: Detail the first n successful cycles.

    Returns:
        A list of the cycles in which the cycler returns to Kerbin.
    
    Examples:
        >>> periods = calculate_periods(print_first_n=2)
        7 cycles (14.9421 years): Kerbin would be -58.83 SOI radii behind.
        8 cycles (17.0766 years): Kerbin would be 77.81 SOI radii ahead.
    """
    kerbin_year = 9203545  # seconds
    duna_year = 17315400  # seconds
    synod = (1/(1/kerbin_year - 1/duna_year)) / kerbin_year  # ~2.135 years
 
    kerbin_vel = 9284.5  # m/s around Kerbol
    kerbin_soi = 84159286  # m
 
    years_count = synod*np.arange(periods_to_check)
    offset = years_count - np.round(years_count)  # How far are we off from a full year?
    good_cycles = np.where(np.isclose(offset, 0, atol=precision))  # See where it is close.
 
    # Print the results
    for results in good_cycles:
        for i, n_cycles in enumerate(results):
            if i == 0:  # Skip the initial result (all zeros)
                continue
            if i > print_first_n:  # Stop printing
                break
            n_years = synod*n_cycles
            dist = (n_years - np.round(n_years)) * kerbin_year * kerbin_vel / kerbin_soi
            direction = "ahead" if dist > 0 else "behind"
            
            time_string = "{:d} cycles ({:.4f} years):".format(n_cycles, n_years)
            dist_string = "Kerbin would be {:.2f} SOI radii {}.".format(dist,direction)
            
            print(time_string, dist_string)
 
    return good_cycles
