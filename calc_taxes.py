import argparse
import csv
import datetime
import copy


def row_gen(input_file):
    with open(input_file) as csv_file:
        dialect = csv.Sniffer().sniff(csv_file.read(1024))
        csv_file.seek(0)
        for csv_dict in csv.DictReader(csv_file, dialect=dialect):
            yield {'date': datetime.datetime.strptime(csv_dict['date'].split(' ')[0], '%Y-%m-%d'),
                   'product': csv_dict['product'], 'side': csv_dict['side'], 'quantity': float(csv_dict['quantity']),
                   'price': float(csv_dict['price'])}


def calc_losses_gains(input_file=None, input_list=None):
    rows = input_list if input_list else list(row_gen(input_file))
    buys = [r for r in rows if r['side'] == 'BUY']
    sells = [r for r in rows if r['side'] == 'SELL']
    losses_gains = []
    new_buys = copy.deepcopy(buys)
    for s in sells:
        left_to_account_for = s['quantity']
        next_new_buys = []
        for b in new_buys:
            if b['product'] == s['product'] and s['date'] > b['date'] and left_to_account_for > 0:
                qty = min(b['quantity'], left_to_account_for)
                b['quantity'] = b['quantity'] - qty
                left_to_account_for = left_to_account_for - qty
                losses_gains.append({'enter': b['date'], 'exit': s['date'],
                                     'difference': (s['price'] - b['price']) * qty})
            next_new_buys.append(b)
        if left_to_account_for > 0:
            raise Exception('No buy to match sale of {}'.format(s['product']))
        new_buys = next_new_buys
    remaining_balances = {}
    for b in buys:
        remaining_balances[b['product']] = (remaining_balances.get(b['product']) or 0) + b['quantity']
    # print 'Remaining Balances: {}'.format(remaining_balances)
    return losses_gains


def calc_losses_gains_by_year(losses_gains):
    ordered_losses_gains = sorted(losses_gains, key=lambda k: k['exit'])
    ret_dict = {}
    for lg in ordered_losses_gains:
        exit_year = lg['exit'].year
        ret_dict[exit_year] = (ret_dict.get(exit_year) or 0) + lg['difference']
    return ret_dict


def taxes_by_year(input_file=None, input_list=None):
    losses_gains = calc_losses_gains(input_file, input_list)
    losses_gains_by_year = calc_losses_gains_by_year(losses_gains)
    # print "Losses, gains, by year: {}".format(losses_gains_by_year)
    gain_years = {k: v for k, v in losses_gains_by_year.iteritems() if v > 0}
    gains_by_enter_exit_disparity = [g for g in sorted(losses_gains, key=lambda k: -(k['exit'] - k['enter']))
                                     if g['difference'] > 0]
    tax_amount_by_year = {gy: {'long_term': 0, 'short_term': 0} for gy in gain_years}
    for gy in gain_years:
        amount_left = losses_gains_by_year[gy]
        for d in gains_by_enter_exit_disparity:
            if d['exit'].year == gy and amount_left > 0:
                amount = min(amount_left, d['difference'])
                amount_left = amount_left - amount
                if (d['exit'] - d['enter']).days > 365:
                    tax_amount_by_year[gy]['long_term'] += amount
                else:
                    tax_amount_by_year[gy]['short_term'] += amount
    return tax_amount_by_year

