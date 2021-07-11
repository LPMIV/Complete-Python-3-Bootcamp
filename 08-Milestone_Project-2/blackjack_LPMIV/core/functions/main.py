from IPython.display import clear_output
import time
from core.functions.multiplexer import Log

log = Log()

def elapse(sec,wait=False):
    time.sleep(sec)
    clear_output(wait)


def player_objs(obj):
    '''Sets a user interface and collects players' names, bets and creates a list of Player instances.'''
    
    while True:
        player_count = (input('Input amount of players at the table (max 7): '))
        clear_output()
        # Testing user input
        try:
            int(player_count)
        except ValueError:
            print('Input must be a number, please try again.')
            continue
        else:
            if int(player_count) > 7:
                print('Sorry, too many players! Please try again.')
                continue
            else:
                player_names = [input(f'Player {count}, input your name: ') for count in range(1,int(player_count)+1)]
                clear_output()
                objs = [obj(name) for name in player_names]
                for player in objs:
                    player.place_bet()
                return objs


def insurance_option(dealer,players):
    '''Initiates insurance event and resolves player-insurance condition.'''
    
    # Initiating event
    while dealer.insurance.event_trigger == None:
        if dealer.main_hand.value[0].rank == 'Ace':
            for player in players:
                player.insurance.interface()
            dealer.insurance.event_trigger = 1
        else:
            break
    # Resolving event
    while dealer.initial_deal.log == (0,1):
        for player in players:
            if player.insurance.status.active:
                try:
                    dealer.main_hand.value[1]
                except IndexError:
                    break
                else:
                    if dealer.main_hand.calc == 21:
                        dealer.insurance.condition = 'Win'
                    else:
                        dealer.insurance.condition = 'Lose'
                    for player in players:
                        player.insurance.condition.resolver()
                        player.balance = player.insurance.balance
                    time.sleep(8)
                    break
        break


def resolver(deck,dealer,players):
    '''Resolves player condition for initial and main deals. Does not resolve insurance condition, use insurance_option().'''

    condp = lambda cond: print(cond)
    dview = lambda: print(f'Dealer-Hand | {dealer.main_hand.calc}')
    dhcalc = dealer.main_hand.calc
    # Resolving initial deal.
    if dealer.main_play.ready == 0:
        cycle = 0
        for player in players:
            cycle += 1
            pview = player.view
            phcalc = player.main_hand.calc
            pcond = lambda cond: player.condition(cond,player.main_hand,deck)
            if phcalc == 21 and dhcalc == 21:
                if cycle == 0:
                    dview()
                pview(request='main')
                condp('Push')
                pcond('Push')
                log.resolver = 'Resolved'
                time.sleep(8)
            elif phcalc == 21 and dhcalc != 21:
                if cycle == 0:
                    dview()
                pview(request='main')
                condp('Natural')
                pcond('Natural')
                log.resolver = 'Resolved'
                time.sleep(8)
    # Resolving main deal.
    if dealer.main_play.ready:
        for player in players:
            for hand in player.hands:
                pview = lambda: print(f'\n{player.name}\nMain-Hand | {hand.calc}') if hand == player.main_hand else print(f'\n{player.name}\nOff-Hand | {hand.calc}')
                pcond = lambda cond: player.condition(cond,hand,deck)
                while hand.status.active:
                    if hand.calc == 21 and dhcalc == 21:
                        dview()
                        pview()
                        condp('Push')
                        pcond('Push')
                    elif hand.calc == 21 and dhcalc != 21:
                        dview()
                        pview()
                        condp('Blackjack')
                        pcond('Blackjack')
                    elif hand.calc != 21 and dhcalc == 21:
                        dview()
                        pview()
                        condp('Dealer Blackjack')
                        pcond('Lose')
                    elif hand.calc > dhcalc:
                        dview()
                        pview()
                        condp('Upper Hand')
                        pcond('Win')
                    elif hand.calc < dhcalc:
                        dview()
                        pview()
                        condp('Lower Hand')
                        pcond('Lose')
                        

def replay_feed(players):
    for player in players:
        # Testing user input.
        while True:
            feedback = input(f'{player.name}, would you like to play another round? Use the numpad or type your answer below.\n1:Yes | 0:No')
            clear_output()
            try:
                int(feedback)
            except ValueError:
                if feedback.capitalize() not in ('Yes','No'):
                    print('Sorry, you must answer Yes or No. Please try again')
                    clear_output(True)
                    continue
                elif feedback.capitalize() == 'No':
                    players.pop(players.index(player))
                    break
            else:
                if int(feedback) not in (1,0):
                    print('Sorry, you must answer 1 or 0. Please try again.')
                    clear_output(True)
                    continue
                elif int(feedback) == 0:
                    players.pop(players.index(player))
                    break