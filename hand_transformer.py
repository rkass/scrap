import argparse
import string
import random
import os


def format_money(input):
    return '${:,.2f}'.format(float(input)).replace(',', '')


def find_in_player_seat_balance(player_seat_balance_, player):
    for psb in player_seat_balance_:
        if psb['player'] == player:
            return psb


def transform_blind_sentence(original):
    original_split = original.split(' ')
    if 'big' in original:
        size = 'big'
    elif 'small' in original:
        size = 'small'
    else:
        raise Exception('weird blind situation ' + original)
    screen_name, amount = original_split[0], original_split[-1]
    return screen_name + ': posts ' + size + ' blind ' + format_money(amount)

def line_at_index(lines, index):
    return lines[index].rstrip()


class Hand(object):

    def __init__(self, lines, index, table_name):
        self.board = None
        split_first = line_at_index(lines, 0).split(' ')
        self.output_lines = []
        self.output_lines.append('*********** # {} **************'.format(index))
        self.hand_number = split_first[1].replace('#', '').replace('-', '')
        self.date_string = split_first[3].replace('-', '/') + ' ' + split_first[4] + ' ET'
        split_second = line_at_index(lines, 1).split(' ')
        small, big = split_second[-1].split('/')
        self.small = format_money(small)
        self.big = format_money(big)
        self.output_lines.append('PokerStars Hand #{}:  Omaha Pot Limit ({}/{} USD) - {}'.format(self.hand_number,
                                                                                             self.small,
                                                                                             self.big,
                                                                                             self.date_string))

        player_seat_balance = []
        for index in range(4, len(lines)):
            l = line_at_index(lines, index)
            if 'waiting' in l or 'sitting out' in l:
                continue
            if not l.startswith('Seat '):
                break
            colon_split = l.split(':')
            seat = colon_split[0]
            raw_player, raw_balance = colon_split[1].rstrip().lstrip().split(' ')
            player = raw_player.rstrip()
            balance = format_money(raw_balance.rstrip().replace('(', '').replace(')', ''))
            player_seat_balance.append({'player': player, 'balance': balance, 'seat': seat})

        button_player = line_at_index(lines, index).split(' ')[0]
        button_player_seat_balance = find_in_player_seat_balance(player_seat_balance, button_player)
        button_seat_split = button_player_seat_balance['seat'].split(' ')
        button_sentence = button_seat_split[0] + ' #' + button_seat_split[1] + ' is the button'
        full_button_sentence = "Table '" + table_name + "' 6-max " + button_sentence
        self.output_lines.append(full_button_sentence)
        for psb in player_seat_balance:
            self.output_lines.append(psb['seat'] + ': ' + psb['player'] + ' (' + psb['balance'] + ' in chips)')

        index += 1
        small_blind_line = line_at_index(lines, index)
        index += 1
        big_blind_line = line_at_index(lines, index)
        self.output_lines.append(transform_blind_sentence(small_blind_line))
        penultimate_bet = None
        last_bet = float(big_blind_line.split(' ')[-1])
        self.output_lines.append(transform_blind_sentence(big_blind_line))
        self.output_lines.append('*** HOLE CARDS ***')
        index += 2
        if 'Dealt to' not in line_at_index(lines, index):
            raise Exception('player not in current hand')
        self.output_lines.append(line_at_index(lines, index))
        index += 1
        for index in range(index, len(lines)):
            l = line_at_index(lines, index)
            all_in = False
            split_line = l.split(' ')
            if 'raises' in l:
                if '(All-in)' in l:
                    all_in = True
                    l = l.replace('(All-in)', '')
                    split_line = l.split(' ')
                if penultimate_bet is None:
                    min_raise = last_bet * 2
                else:
                    min_raise = last_bet + (last_bet - penultimate_bet)
                penultimate_bet = last_bet
                amt = float(split_line[-1])
                last_bet = amt
                action_string = 'raises ' + format_money(min_raise) + ' to ' + format_money(amt)
                ol = split_line[0] + ': ' + action_string
                if all_in:
                    ol += ' and is all-in'
                self.output_lines.append(ol)
            elif 'calls' in l:
                if '(All - in)' in l:
                    all_in = True
                    l = l.replace('(All-in)', '')
                    split_line = l.split(' ')
                amt = split_line[-1]
                ol = split_line[0] + ': calls ' + format_money(amt)
                if all_in:
                    ol += ' and is all-in'
                self.output_lines.append(ol)
            elif 'bets' in l:
                if '(All-in)' in l:
                    all_in = True
                    l = l.replace('(All-in)', '')
                    split_line = l.split(' ')
                amt = split_line[-1]
                last_bet = float(amt)
                ol = split_line[0] + ': bets ' + format_money(amt)
                if all_in:
                    ol += ' and is all-in'
                self.output_lines.append(ol)
            elif 'folds' in l:
                self.output_lines.append(split_line[0] + ': folds')
            elif 'checks' in l:
                self.output_lines.append(split_line[0] + ': checks')
            elif 'shows' in l:
                self.output_lines.append(split_line[0] + ': shows' + ' '.join(split_line[2:]))
            elif 'wins' in l:
                amt = lines[index].split('(')[1].split(')')[0]
                self.output_lines.append(split_line[0] + ' collected ' + format_money(amt) + ' from pot')
            elif 'refunded' in l:
                self.output_lines.append('Uncalled bet (' + format_money(split_line[-1]) + ')' + ' returned to ' + split_line[0])
            elif 'Rake' in l:
                rake = split_line[1].replace('(', '').replace(')', '')
                pot = split_line[3].replace('(', '').replace(')', '')
                self.output_lines.append('*** SUMMARY ***')
                self.output_lines.append('Total pot ' + format_money(pot) + ' | Rake ' + format_money(rake))
                if self.board:
                    self.output_lines.append('Board ' + self.board)
            elif '** Flop **' in l:
                self.board = '[' + l.split('[')[-1]
                last_bet = None
                penultimate_bet = None
                cards = '['+ l.split('[')[1]
                self.output_lines.append('*** FLOP *** ' + cards)
            elif '** Turn **' in l:
                self.board = self.board[:-1] + ' ' + l.split('[')[-1]
                last_bet = None
                penultimate_bet = None
                cards = '['+ l.split('[')[1]
                self.output_lines.append('*** TURN *** ' + cards)
            elif '** River **' in l:
                self.board = self.board[:-1] + ' ' + l.split('[')[-1]
                last_bet = None
                penultimate_bet = None
                cards = '['+ l.split('[')[1]
                self.output_lines.append('*** RIVER *** ' + cards)
            elif '** Pot Show Down **' in l:
                self.output_lines.append('*** SHOW DOWN ***')


def parse_file(f):
    table_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    hands = []
    hand_count = 0
    output_lines = []
    hand_started = False
    for line in f:
        if line.startswith('Hand #'):
            hand_started = True
        elif line.strip() == '' and hand_started:
            hand_count += 1
            try:
                hands.append(Hand(output_lines, hand_count, table_name))
            except Exception as e:
                print e
                import traceback
                traceback.print_exc()
                print 'failed to parse hand'
            hand_started = False
            output_lines = []
        if hand_started:
            output_lines.append(line)
    return hands

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, help="Path to input file", required=True)
    parser.add_argument("--output_dir", type=str, default=None, help="Path to output file", required=True)
    args = parser.parse_args()
    output_lines = []

    for index, filename in enumerate(os.listdir(args.input_dir)):
        with open(os.path.join(args.input_dir, filename), 'r') as input_file:

            hands = parse_file(input_file)
            with open(os.path.join(args.output_dir, str(index + 1)), 'w+') as output_f:
                for h in hands:
                    output_f.writelines(h.output_lines)
                    output_f.write('\n')

