import random
import time
from IPython.display import clear_output
from traitlets.traitlets import EventHandler
from core.functions.multiplexer import crncy
from .plugins import HandMixin,InsurancePlugin,DoubleDownPlugin,SplitPlugin

# Card Class Prerequisites
ranks = ('Ace','Two','Three','Four','Five','Six','Seven','Eight','Nine','Ten','Jack','Queen','King')
suits = ('Clubs','Diamonds','Hearts','Spades')
values = {'Ace':11,'Two':2,'Three':3,'Four':4,'Five':5,'Six':6,'Seven':7,'Eight':8,'Nine':9,
         'Ten':10,'Jack':10,'Queen':10,'King':10}
# Game Conditions
conditions = ('Lose','Win','Natural','Blackjack','Push','Bust')


class Card:
    def __init__(self,rank,suit):
        self.rank = rank
        self.suit = suit
        self.value = values[rank]
        
    def __str__(self):
        return f'{self.rank} of {self.suit}' 


class Deck:
    def __init__(self, multiplier=6):
        '''Input a multiplier, one through eight, for how many decks to be created'''
        self.__cards = []
        for _ in range(multiplier):
            for rank in ranks:
                for suit in suits:
                    self.__cards.append(Card(rank,suit))
                    
    def shuffle(self):
        random.shuffle(self.__cards)
    
    def deal(self):
        return self.__cards.pop(0)
    
    def collect(self,hand):
        self.__cards.extend(hand)
        hand.clear()


class Player:
    def __init__(self,name,debug_mode=0):
        '''Input player name.'''
        
        self.name = name
        self.__debug_mode = debug_mode
        self.__bet = 0
        self.balance = 0
        self.main_hand = HandMixin('Active')
        self.off_hand = HandMixin('Inactive')
        self.hands = (self.main_hand,self.off_hand)
        self.__double_down = DoubleDownPlugin()
        self.__split = SplitPlugin()

        if debug_mode:
            self.place_bet()
    
    def place_bet(self):
        while True:
            if self.__debug_mode:
                bet = 400
            else:
                bet = (input(f'{self.name}, place your bet (min $2, max $500): '))
                clear_output()
            # Testing user input
            try:
                int(bet)
            except ValueError:
                print('You must input a number, please try again.')
                continue
            else:
                if int(bet) < 2 or int(bet) > 500:
                    print('Amount out of range, please try again.')
                    clear_output(True)
                    continue
                else:
                    self.__bet = int(bet)
                    self.__insurance = InsurancePlugin('Player',self.name,self.__bet,self.balance)
                    break
        
    def hit(self,hand,card):
        hand.value.append(card)
    
    @property
    def split(self):
        return self.__split
    
    @split.setter
    def split(self,rank):
        card_split = [card for card in self.main_hand.value if card.rank == rank][0]
        self.off_hand.value.append(self.main_hand.value.pop(self.main_hand.value.index(card_split)))
        self.off_hand.status = 'Active'
        
    @property
    def double_down(self):
        return self.__double_down
    
    @double_down.setter
    def double_down(self,boolean):
        # Testing argument
        while boolean != 1:
            raise ValueError('expected argument True as boolean')
        # Executing
        if boolean == 1:
            self.__bet = self.__bet * 2
    
    @property
    def insurance(self):
        return self.__insurance

    @insurance.setter
    def insurance(self,arg):
        while arg == arg:
            raise ValueError('insurance property cannot be set outside of class.')

    def condition(self,game_cond,hand,deck):
        # Testing argument.
        while game_cond not in conditions:
            raise ValueError('expected game condition as string.')
        while hand not in self.hands:
            raise ValueError('hand is not in self.hands.')
        # Executing.
        if game_cond == 'Lose' or game_cond == 'Bust':
            view = f'-{crncy(self.__bet)}'
        elif game_cond == 'Win':
            view = f'+{crncy(self.__bet * 2)}'
            self.balance = self.balance + (self.__bet * 2)
        elif game_cond == 'Natural':
            view = f'+{crncy((self.__bet * .5) + (self.__bet * 2))}'
            self.balance = self.balance + (self.__bet * .5) + (self.__bet * 2)
        elif game_cond == 'Blackjack':
            view = f'+{crncy(self.__bet * 2)}'
            self.balance = self.balance + (self.__bet * 2)
        elif game_cond == 'Push':
            view = f'+{crncy(self.__bet)}'
            self.balance = self.balance + self.__bet
        self.__bet = 0
        deck.collect(hand.value)
        print(view)
        hand.status = 'Inactive'
    
    def interface(self,deck,dealer):
        for hand in self.hands:
            while hand.stand == 0 and hand.status.active:
                # Defining temporary variables.
                hand_select = 'main' if hand == self.main_hand else 'off'
                comms = ('Hit','Stand','Double Down','Split')
                deflt_view = ['Hit','Stand']
                mod_view = ['Double Down','Split']
                ranks = [card.rank for card in hand.value]
                unique_ranks = set(ranks)
                rank_splits = [rank for rank in unique_ranks if ranks.count(rank) >= 2]
                # Defining boolean conditions.
                double_down_append = 0
                split_append = 0
                # Modifying default view.
                while len(self.main_hand.value) == 2:
                    if self.main_hand.calc in (9,10,11):
                        deflt_view.append(mod_view[0])
                        double_down_append = 1
                    break
                while len(self.main_hand.value) == 2 and self.off_hand.status.inactive:
                    if len(rank_splits) > 0:
                        deflt_view.append(mod_view[1])
                        split_append = 1
                    break
                new_view = [f'\n{index}:{view}' for index,view in enumerate(deflt_view)]
                # Testing user input.
                dealer.view()
                self.view(1,hand_select,1)
                projection = input(f"{self.name}, use the numpad or type out your choice.{''.join(new_view)}\n")
                clear_output()
                try:
                    int(projection)
                except ValueError:
                    if projection.capitalize() not in deflt_view:
                        print('Sorry, invalid argument. Please try again.')
                        clear_output(True)
                        continue
                    else:
                        user_cmd = projection.capitalize()
                else:
                    if int(projection) not in [index for index,view in enumerate(deflt_view)]:
                        print('Sorry, invalid argument. Please try again.')
                        clear_output(True)
                        continue
                    else:
                        user_cmd = deflt_view[int(projection)]
                # Executing
                if double_down_append and user_cmd == 'Double Down':
                    self.hit(self.main_hand,deck.deal())
                    self.double_down.status = 'Active'
                    break
                elif split_append and user_cmd == 'Split':
                    deflt_view.pop(deflt_view.index('Split'))
                    user_rank = self.__split.interface(rank_splits)
                    self.split = user_rank
                    continue
                elif user_cmd == 'Hit':
                    self.hit(hand,deck.deal())
                    if hand.calc > 21:
                        print(f'{self.name} | Bust: {hand.calc}')
                        self.condition('Bust',hand,deck)
                        break
                    else:
                        continue
                elif user_cmd == 'Stand':
                    hand.stand = 1

    def view(self,new_line=0,request=0,header=0):
        '''Specify a hand request as 'main' or 'off' if request paramater is specified.
        Header paramater prints by default unless request paramater is specified, change header respectively.
        '''
        
        # Testing argument.
        while request not in (0,'main','off'):
            raise ValueError("Hand request paramater must be 'main' or 'off' as string, or False as boolean.")
        for argument in (new_line,header):
            while argument not in (1,0):
                raise ValueError(f'{argument} paramater must be True or False as boolean.')
        # Defining temporary variables.
        header_view = f'{self.name} | Round Bet: {crncy(self.__bet)} | Total Earned: {crncy(self.balance)}'
        _main = f'Main-Hand: [{self.main_hand.view}] | Total Hand: {self.main_hand.calc}'
        _off = f'Off-Hand: [{self.off_hand.view}] | Total Hand: {self.off_hand.calc}'
        hands = {self.main_hand:_main, self.off_hand:_off}
        hands_select = [hands[hand] for hand in hands if hand.status.active]
        hands_request = {'main':_main,'off':_off}
        # Executing
        if request == 0:
            if new_line:
                print('\n'+header_view)
                for hand in hands_select:
                    print(hand)
            else:
                print(header_view)
                for hand in hands_select:
                    print(hand)
        # Printing one hand if specified.
        else:
            if new_line:
                if header:
                    print('\n'+header_view)
                    print(hands_request[request])
                else:
                    print(f'\n{self.name} | {hands_request[request]}')
            else:
                if header:
                    print(header_view)
                    print(hands_request[request])
                else:
                    print(f'{self.name} | {hands_request[request]}')        


class Dealer(Player):
    def __init__(self):
        ''''''
        Player.__init__(self,name='Dealer')
        self.__insurance = InsurancePlugin('Dealer',None,None,None)
    
    @property
    def event(self):
        return self.__event

    @event.setter
    def event(self,arg):
        while arg == arg:
            raise ValueError('event can only be returned')
    
    @property
    def log(self):
        return tuple(self.__log)

    @log.setter
    def log(self,arg):
        while arg == arg:
            raise ValueError('log can only be returned.')
    
    @property
    def initial_deal(self):
        self.__event = self.__init_event
        self.__log = self.__init_log
        return self
    
    @initial_deal.setter
    def initial_deal(self,arg=None):
        # Testing argument
        while arg != None and arg not in (1,0):
            raise ValueError('expected argument True or False as boolean')
        try:
            self.__init_event
        except AttributeError:
            pass
        else:
            while self.__init_event == 1 and arg == 1:
                raise ValueError(f'cannot accept argument as {bool(arg)} if initial deal is already {bool(self.__init_event)}.')
        # Executing
        if arg != None:
            self.__init_event = arg
            try:
                self.__init_log
            except AttributeError:
                self.__init_log = [arg]
            else:
                self.__init_log.insert(0,arg)
                if len(self.__init_log) == 3:
                    self.__init_log.pop(2)
    
    @property
    def main_play(self):
        try:
            self.__main
        except AttributeError:
            self.__main = 0
        return self

    @property
    def ready(self):
        return self.__main
    
    def automate(self,deck):
        '''Automates the Dealer.hit method for the main play.'''
        
        while self.main_hand.calc < 17:
            self.hit(self.main_hand,deck.deal())
            self.view()
            time.sleep(4)
            clear_output(True)
        self.__main = 1
        self.stand = 1

    @property
    def insurance(self):
        return self.__insurance
    
    def view(self,new_line=0):
        # Defining temporary variables.
        hand = f'Dealer-Hand: [{self.main_hand.view}] | Total Hand: {self.main_hand.calc}'
        hand_len = len(self.main_hand.value)
        init_index = self.main_hand.view.index(',') if hand_len > 1 else None
        init_hand = f'Dealer-hand: [{self.main_hand.view[0:init_index]}, Card Face Down]' if hand_len > 1 else None
        # Executing.
        if self.initial_deal.event:
            if hand_len == 1:
                if new_line:
                    print('\n'+hand)
                else:
                    print(hand)
            else:
                if new_line:
                    print('\n'+init_hand)
                else:
                    print(init_hand)
        else:
            if new_line:
                print('\n'+hand)
            else:
                print(hand)