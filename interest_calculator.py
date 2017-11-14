import random

def calculate_interest(starting_amount, annual_contribution,
                       annual_interest, yearly_tax, final_tax, capital_gains_tax, years, initial_amount=None):
    if years == 0:
        return (starting_amount * (1 - final_tax)) * (1 - capital_gains_tax)
    new_starting_amount = (starting_amount + (annual_contribution * (1 - yearly_tax.pop()))) * (1 + annual_interest)
    return calculate_interest(new_starting_amount, annual_contribution, annual_interest,
                              yearly_tax, final_tax, capital_gains_tax, years - 1,
                              initial_amount if initial_amount is not None else initial_amount)

def break_even_point():

    starting_amount = 0
    annual_contribution = 20000
    annual_interest = .06
    start_yearly_tax = .45
    end_capital_gains_tax = .2
    years = 30

    def years_list(end_yearly_tax):
        ret = []
        for i in range(years):
            ret.append(start_yearly_tax + ((end_yearly_tax - start_yearly_tax) * (i / float(years))))
        return ret


    def get_final_amount_no_401k(end_yearly_tax):
        return calculate_interest(starting_amount, annual_contribution, annual_interest,
                                  years_list(end_yearly_tax), 0, end_capital_gains_tax, years)

    def get_final_amount_with_401k(end_yearly_tax):
        return calculate_interest(starting_amount, annual_contribution, annual_interest,
                                  [0] * years, end_yearly_tax, 0, years)


    end_yearly_tax = start_yearly_tax

    amount_no_401k = get_final_amount_no_401k(end_yearly_tax)
    amount_401k = get_final_amount_with_401k(end_yearly_tax)

    print 'Taxes start: {}; Taxes end: {}; '.format(start_yearly_tax, end_yearly_tax) + \
          'total without 401k: {}'.format(amount_401k, amount_no_401k)

    while amount_401k > amount_no_401k:
        end_yearly_tax += .01
        amount_no_401k = get_final_amount_no_401k(end_yearly_tax)
        amount_401k = get_final_amount_with_401k(end_yearly_tax)

        print 'Taxes start: {}; Taxes end: {}; '.format(start_yearly_tax, end_yearly_tax) + \
              'total without 401k: {}; total with 401k: {}'.format(amount_no_401k, amount_401k)

sp_data = {1928: 0.43810000000000004, 1929: -0.083, 1930: -0.25120000000000003, 1931: -0.43840000000000007,
           1932: -0.0864, 1933: 0.49979999999999997, 1934: -0.011899999999999999, 1935: 0.46740000000000004,
           1936: 0.3194, 1937: -0.35340000000000005, 1938: 0.2928, 1939: -0.011000000000000001, 1940: -0.1067,
           1941: -0.1277, 1942: 0.1917, 1943: 0.2506, 1944: 0.19030000000000002, 1945: 0.3582, 1946: -0.0843,
           1947: 0.052000000000000005, 1948: 0.057, 1949: 0.18300000000000002, 1950: 0.3081, 1951: 0.2368, 1952: 0.1815,
           1953: -0.0121, 1954: 0.5256000000000001, 1955: 0.326, 1956: 0.07440000000000001, 1957: -0.10460000000000001,
           1958: 0.4372, 1959: 0.12060000000000001, 1960: 0.0034000000000000002, 1961: 0.2664,
           1962: -0.08810000000000001, 1963: 0.2261, 1964: 0.1642, 1965: 0.12400000000000001,
           1966: -0.09970000000000001, 1967: 0.23800000000000002, 1968: 0.1081, 1969: -0.0824, 1970: 0.0356,
           1971: 0.14220000000000002, 1972: 0.18760000000000002, 1973: -0.1431, 1974: -0.259, 1975: 0.37,
           1976: 0.23829999999999998, 1977: -0.0698, 1978: 0.0651, 1979: 0.1852, 1980: 0.3174, 1981: -0.047,
           1982: 0.20420000000000002, 1983: 0.22340000000000002, 1984: 0.061500000000000006, 1985: 0.3124,
           1986: 0.18489999999999998, 1987: 0.0581, 1988: 0.1654, 1989: 0.3148, 1990: -0.030600000000000002,
           1991: 0.3023, 1992: 0.07490000000000001, 1993: 0.09970000000000001, 1994: 0.013300000000000001,
           1995: 0.37200000000000005, 1996: 0.2268, 1997: 0.331, 1998: 0.2834, 1999: 0.2089, 2000: -0.09029999999999999,
           2001: -0.1185, 2002: -0.2197, 2003: 0.2836, 2004: 0.10740000000000001, 2005: 0.0483, 2006: 0.1561,
           2007: 0.05480000000000001, 2008: -0.3655, 2009: 0.2594, 2010: 0.1482, 2011: 0.021, 2012: 0.1589,
           2013: 0.3215, 2014: 0.1352, 2015: 0.013600000000000001}



def margin_profits(price_per_share, shares_purchased, shares_borrowed,
                   margin_interest_rate, period_in_days, share_growth_rate=None, price_per_share_end_value=None):
    balance = 0
    balance -= shares_purchased * price_per_share
    loan_amount = shares_borrowed * price_per_share
    for day in range(period_in_days):
        if share_growth_rate:
            price_per_share += (price_per_share * share_growth_rate) / 365.0
        balance -= (loan_amount * margin_interest_rate) / 365.0
    if price_per_share_end_value:
        price_per_share = price_per_share_end_value
    balance += price_per_share * (shares_purchased + shares_borrowed)
    balance -= loan_amount
    return balance


def sp_margin_profits_sim(investment, loan, interest_rate, period_in_years, sims):
    sorted_keys = sorted(k for k in sp_data.keys())
    available_starts = sorted_keys
    if period_in_years > 1:
        available_starts = available_starts[:-(period_in_years - 1)]
    profit = 0
    for i in range(sims):
        start_year = random.choice(available_starts)
        iteration_balance = -investment
        investment_yield_percentage = 1
        for year in [start_year + i for i in range(period_in_years)]:
            iteration_balance -= loan * interest_rate
            investment_yield_percentage = investment_yield_percentage * (1 + sp_data[year])
        iteration_balance += (investment + loan) * investment_yield_percentage
        iteration_balance -= loan
        profit += iteration_balance
    return profit / sims

if __name__ == '__main__':
    print sp_margin_profits_sim(investment=10000, loan=10000, interest_rate=0.0266, period_in_years=1, sims=100000)

