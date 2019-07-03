import random
import calendar
import csv
import calendar
import sim_intervals
import datetime
import calc_taxes
import numpy


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


def _get_amount_owed(cash, margin):
    return max(cash * margin - cash, 0)


# class InvestmentState(object):
#
#     def __init__(self, total_investment, equitive):

def simulate_month(ordered_date_price_tuples, index, percent_change_std):
    date_string = ordered_date_price_tuples[index][0].strip()
    month_abbr = date_string.split(' ')[0]
    month_number = list(calendar.month_abbr).index(month_abbr)
    year = int(date_string.split(' ')[-1])
    num_days = calendar.monthrange(year, month_number)[-1]
    current_price = price_for_index(ordered_date_price_tuples, index)
    beginning_of_next_month_price = price_for_index(ordered_date_price_tuples, index + 1)
    return [current_price] + sim_intervals.sim_intervals(current_price, beginning_of_next_month_price, num_days, percent_change_std)[:-1]


def price_for_index(ordered_date_price_tuples, index):
    return float(ordered_date_price_tuples[index][1].replace(',', ''))


class InvestmentTrials(object):

    def __init__(self, monte_carlo, num_trials, seed_cash, initial_margin, annualized_interest_rate,
                 duration_in_months, monthly_cash, monthly_margin, max_allowed_margin,
                 long_term_tax_rate, short_term_tax_rate):
        self.monte_carlo = monte_carlo
        self.num_trials = num_trials
        self.seed_cash = seed_cash
        self.initial_margin = initial_margin
        self.annualized_interest_rate = annualized_interest_rate
        self.duration_in_months = duration_in_months
        self.monthly_cash = monthly_cash
        self.monthly_margin = monthly_margin
        self.daily_std = estimate_daily_std()
        self.max_allowed_margin = max_allowed_margin
        self.long_term_tax_rate = long_term_tax_rate
        self.short_term_tax_rate = short_term_tax_rate
        if self.monte_carlo and self.num_trials:
            raise Exception('Either define monte carlo or num trials, not both. Set one to None')

    def simulate_trials(self):
        possible_starting_positions = len(ordered_date_price_tuples) - self.duration_in_months
        if self.monte_carlo:
            print "Simulating one trial at all {} possible starting positions".format(possible_starting_positions)
            start_pos_gen = xrange(possible_starting_positions)
        else:
            print "Selecting randomly from {} possible starting positions to simulate {} trials"\
                .format(possible_starting_positions, self.num_trials)
            start_pos_gen = (random.randint(0, possible_starting_positions - 1) for _ in range(self.num_trials))
        self.trials = [InvestmentTrial(self.seed_cash, self.initial_margin, self.annualized_interest_rate,
                                       self.duration_in_months, self.monthly_cash, self.monthly_margin,
                                    self.max_allowed_margin, self.long_term_tax_rate,
                                       self.short_term_tax_rate, self.daily_std, fixed_start_index=i)
                       for i in start_pos_gen]
        print "Initialized {} trials".format(len(self.trials))
        for i, t in enumerate(self.trials):
            t.simulate_trial()
            print "Finished simulating {} of {} trials".format(i + 1, len(self.trials))

    def print_deciles(self):
        values = [t.portfolio_value() for t in self.trials]
        print "Portfolio Value Deciles with config: "
        print "Seed cash={}".format(self.seed_cash)
        print "Initial Margin Ratio={}".format(self.initial_margin)
        print "Monthly cash={}".format(self.monthly_cash)
        print "Monthly Margin Ratio={}".format(self.monthly_margin)
        print "Annual Interest Rate={}".format(self.annualized_interest_rate)
        print "Max allowed Margin={}".format(self.max_allowed_margin)
        print "Duration in Months={}".format(self.duration_in_months)
        print "Short term tax rate={}".format(self.short_term_tax_rate)
        print "Long term tax rate={}".format(self.long_term_tax_rate)
        if self.monte_carlo:
            print "Used monte carlo strategy"
        else:
            print "Simulated {} random trials".format(self.num_trials)
        print "MEAN: {}".format(numpy.mean(values))
        print "10th percentile: {}".format(numpy.percentile(values, 10))
        print "20th percentile: {}".format(numpy.percentile(values, 20))
        print "30th percentile: {}".format(numpy.percentile(values, 30))
        print "40th percentile: {}".format(numpy.percentile(values, 40))
        print "50th percentile: {}".format(numpy.percentile(values, 50))
        print "60th percentile: {}".format(numpy.percentile(values, 60))
        print "70th percentile: {}".format(numpy.percentile(values, 70))
        print "80th percentile: {}".format(numpy.percentile(values, 80))
        print "90th percentile: {}".format(numpy.percentile(values, 90))


class InvestmentTrial(object):

    monthly_deposit_day = 14
    monthly_interest_pay_day = 27

    def __init__(self, seed_cash, initial_margin, annualized_interest_rate, duration_in_months,
                 monthly_cash, monthly_margin, max_allowed_margin,
                 long_term_tax_rate, short_term_tax_rate, daily_std, fixed_start_index=None):
        self.daily_interest_rate = annualized_interest_rate / 365.0
        self.seed_cash = seed_cash
        self.initial_margin = initial_margin
        self.duration_in_months = duration_in_months
        self.monthly_cash = monthly_cash
        self.monthly_margin = monthly_margin
        self.start_month_index = fixed_start_index if fixed_start_index \
            else random.randint(0, len(ordered_date_price_tuples) - duration_in_months)
        self.yesterday_close_price = None
        self.today_close_price = None
        self.month_index = None
        self.day_index = None
        self.short = 0
        self.total_shares = 0
        self.max_allowed_margin = max_allowed_margin
        self.transaction_history = []
        self.deposited_money = 0
        self.daily_percent_change_std = daily_std
        self.long_term_tax_rate = long_term_tax_rate
        self.short_term_tax_rate = short_term_tax_rate

    def portfolio_value(self):
        return self.long() - self.short

    def long(self):
        return self.total_shares * self.today_close_price

    def _max_purchase_amount(self):
        if self.short == self.long():
            raise Exception('Margin Call')
        return (self.max_allowed_margin - 1) * self.long() - (self.max_allowed_margin * self.short)

    def _deposit_money(self):
        if self.month_index == self.start_month_index and self.day_index == 0:
            deposit_amount = self.seed_cash
        elif self.month_index > self.start_month_index and self.day_index == self.monthly_deposit_day:
            deposit_amount = self.monthly_cash
        else:
            deposit_amount = 0
        self.short -= deposit_amount
        self.deposited_money += deposit_amount

    def _todays_date(self):
        return self._date_for_month_day(self.month_index, self.day_index)

    def _date_for_month_day(self, month_index, day_index):
        date_string = ordered_date_price_tuples[month_index][0].strip()
        day = day_index + 1
        year = int(date_string.split(' ')[-1])
        month_abbr = date_string.split(' ')[0]
        month_number = list(calendar.month_abbr).index(month_abbr)
        return datetime.date(year, month_number, day)

    def _purchase(self):
        """
        Purchase the scheduled amount based on the day unless
        we've exceeded max margin, in which case sell appropriately
        :return: True if we can keep investing; False if we're bankrupt
        """
        if self.month_index == self.start_month_index and self.day_index == 0:
            purchase_amount = self.seed_cash * self.initial_margin
        elif self.month_index > self.start_month_index and self.day_index == self.monthly_deposit_day:
            purchase_amount = self.monthly_cash * self.monthly_margin
        else:
            purchase_amount = 0.0
        net_purchase_amount = min(purchase_amount, self._max_purchase_amount())
        net_shares = net_purchase_amount / self.today_close_price
        self.total_shares += net_shares
        self.short += net_purchase_amount
        if self.total_shares < 0:
            self.short += (0 - self.total_shares) * self.today_close_price
            self.total_shares = 0
            return False
        if net_purchase_amount != 0:
            self.transaction_history.append({'date': self._todays_date(), 'product': 'SP',
                                             'side': 'BUY' if net_purchase_amount > 0 else 'SELL',
                                             'price': self.today_close_price, 'quantity': abs(net_shares)})
        return True

    def _pay_interest(self):
        self.short *= (1 + self.daily_interest_rate)

    def _exit_positions(self):
        if self._is_last_day_of_trial() and self.total_shares > 0:
            self.transaction_history.append({'date': self._todays_date(), 'product': 'SP',
                                            'side': 'SELL', 'price': self.today_close_price,
                                             'quantity': self.total_shares})
            self.short -= self.total_shares * self.today_close_price
            self.total_shares = 0

    def _pay_taxes(self):
        if self._todays_date().month == 12 and self._todays_date().day == 31 or  self._is_last_day_of_trial():
            result = calc_taxes.taxes_by_year(input_list=self.transaction_history)
            if self._todays_date().year in result:
                # withdraw taxes
                self.short += result[self._todays_date().year]['long_term'] * self.long_term_tax_rate + \
                              result[self._todays_date().year]['short_term'] * self.short_term_tax_rate

    def _is_last_day_of_trial(self):
        return (self.month_index - self.start_month_index == self.duration_in_months and
                self.day_index == calendar.monthrange(self._todays_date().year, self._todays_date().month)[-1] - 1)

    def process_day(self):
        """
        :return: True if we can keep investing; False if we're bankrupt
        """
        self._deposit_money()
        return_result = self._purchase()
        self._pay_interest()
        self._exit_positions()
        self._pay_taxes()
        return return_result

    def simulate_trial(self):
        bankrupt_indices = None
        for self.month_index in range(self.start_month_index, self.duration_in_months + self.start_month_index):
            if not bankrupt_indices:
                for (self.day_index, self.today_close_price) in \
                        enumerate(simulate_month(ordered_date_price_tuples, self.month_index, self.daily_percent_change_std)):
                    if not self.process_day():
                        bankrupt_indices = self.month_index, self.day_index
                        break
        if bankrupt_indices:
            print "Went bankrupt after {} months and {} days".format(bankrupt_indices[0] - self.start_month_index,
                                                                     bankrupt_indices[1])
        # print "Portfolio Value: {}".format(self.long() - self.short)
        # print "Total Invested: {}".format(self.deposited_money)


def load_monthly_sp(adjust_for_inflation):
    filename = 'monthly_sp_inflation_adjusted.csv' if adjust_for_inflation else 'monthly_sp.csv'
    with open(filename) as csv_file:
        data = list(csv.reader(csv_file, delimiter='\t'))
    return data[-1:0:-1]


def estimate_daily_std():
    prices = [price_for_index(ordered_date_price_tuples, i) for i in range(len(ordered_date_price_tuples))]
    percent_changes = [(price_for_index(ordered_date_price_tuples, i) - price_for_index(ordered_date_price_tuples, i-1)) / price_for_index(ordered_date_price_tuples, i-1)
                       for i in range(1, len(prices))]
    monthly_std = numpy.std(percent_changes)
    return monthly_std / 30**(1.0/2.0) # https://www.investopedia.com/articles/04/021804.asp


ordered_date_price_tuples = load_monthly_sp(adjust_for_inflation=False)

its = InvestmentTrials(
    monte_carlo=True,
    num_trials=None,
    seed_cash=100000,
    initial_margin=2.0,
    annualized_interest_rate=0.0318,
    duration_in_months=12*20,
    monthly_cash=1500,
    monthly_margin=2.0,
    max_allowed_margin=2.0,
    long_term_tax_rate=0.15,
    short_term_tax_rate=0.32
)
its.simulate_trials()
its.print_deciles()

its = InvestmentTrials(
    monte_carlo=True,
    num_trials=None,
    seed_cash=100000,
    initial_margin=1.75,
    annualized_interest_rate=0.0318,
    duration_in_months=12*20,
    monthly_cash=1500,
    monthly_margin=1.75,
    max_allowed_margin=2.0,
    long_term_tax_rate=0.15,
    short_term_tax_rate=0.32
)
its.simulate_trials()
its.print_deciles()

its = InvestmentTrials(
    monte_carlo=True,
    num_trials=None,
    seed_cash=100000,
    initial_margin=1.5,
    annualized_interest_rate=0.0318,
    duration_in_months=12*20,
    monthly_cash=1500,
    monthly_margin=1.5,
    max_allowed_margin=2.0,
    long_term_tax_rate=0.15,
    short_term_tax_rate=0.32
)
its.simulate_trials()
its.print_deciles()

its = InvestmentTrials(
    monte_carlo=True,
    num_trials=None,
    seed_cash=100000,
    initial_margin=1.25,
    annualized_interest_rate=0.0318,
    duration_in_months=12*20,
    monthly_cash=1500,
    monthly_margin=1.25,
    max_allowed_margin=2.0,
    long_term_tax_rate=0.15,
    short_term_tax_rate=0.32
)
its.simulate_trials()
its.print_deciles()

its = InvestmentTrials(
    monte_carlo=True,
    num_trials=None,
    seed_cash=100000,
    initial_margin=1.0,
    annualized_interest_rate=0.0318,
    duration_in_months=12*20,
    monthly_cash=1500,
    monthly_margin=1.0,
    max_allowed_margin=2.0,
    long_term_tax_rate=0.15,
    short_term_tax_rate=0.32
)
its.simulate_trials()
its.print_deciles()

its = InvestmentTrials(
    monte_carlo=True,
    num_trials=None,
    seed_cash=100000,
    initial_margin=2.0,
    annualized_interest_rate=0.0318,
    duration_in_months=12*20,
    monthly_cash=1500,
    monthly_margin=1.5,
    max_allowed_margin=2.0,
    long_term_tax_rate=0.15,
    short_term_tax_rate=0.32
)
its.simulate_trials()
its.print_deciles()
