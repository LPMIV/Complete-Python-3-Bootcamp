from core.functions.main import insurance_option
from IPython.display import clear_output
from core.functions.multiplexer import crncy

class StatusPlugin:
    def __init__(self,state):
        class StatusProperties:
            def __init__(self,boolean):
                if boolean:
                    self.active = True
                    self.inactive = False
                    self.__view = 'Active'
                else:
                    self.active = False
                    self.inactive = True
                    self.__view = 'Inactive'
                    
            def view(self):
                print(self.__view)
        
        self.__prop1 = StatusProperties(1)
        self.__prop0 = StatusProperties(0)
        # Testing argument.
        while state not in ('Active', 'Inactive'):
            raise ValueError("expected argument 'Active' or 'Inactive' as string.")
        # Initializing.
        if state == 'Active':
            self.__status = self.__prop1
        elif state == 'Inactive':
            self.__status = self.__prop0
    
    @property
    def status(self):
        return self.__status
    
    @status.setter
    def status(self,state):
        # Testing argument.
        while state not in ('Active','Inactive'):
            raise ValueError("expected argument 'Active' or 'Inactive' as string.")
        while state == self.__status.view:
            raise ValueError(f'cannot change status if status is already {state}.')
        # Changing state.
        if state == 'Active':
            self.__status = self.__prop1
        elif state == 'Inactive':
            self.__status = self.__prop0


class StandPlugin:
    def __init__(self):
        self.__stand = 0
        
    @property
    def stand(self):
        return bool(self.__stand)
    
    @stand.setter
    def stand(self,boolean):
        # Testing argument.
        while boolean not in (1,0):
            raise ValueError(f'expected argument True or False as boolean, got {type(boolean)}.')
        while boolean == self.__stand:
            raise ValueError(f'cannot change stand if stand is already {bool(boolean)}')
        # Changing stand.
        self.__stand = boolean


class HandMixin(StatusPlugin,StandPlugin):
    def __init__(self,state):
        StatusPlugin.__init__(self,state)
        StandPlugin.__init__(self)
        self.value = []
        
    @property
    def calc(self):
        # Seperating Ace's from immutable game-cards.
        base = sum([card.value for card in self.value if card.rank != 'Ace'])
        # Starting hard_soft variable with all hard Ace's.
        hard_soft = [card.value for card in self.value if card.rank == 'Ace']
        # Changing each hard Ace to soft until player hand is <= 21 or iterable is exhausted.
        while sum(hard_soft) + base > 21:
            if len([value for value in hard_soft if value == 1]) == len(hard_soft):
                break
            else:
                hard_soft[hard_soft.index(11)] = 1
        return base + sum(hard_soft)
    
    @property
    def view(self):
        concat = ', '.join
        return concat([str(card) for card in self.value])


class InsurancePlugin(StatusPlugin):
    __event_trigger = None
    __condition = None
    
    def __init__(self,opponent,name,round_bet,balance):
        # Testing argument
        while opponent not in ('Dealer','Player'):
            raise ValueError("expected argument 'Dealer' or 'Player' as string.")
        # Initializing
        StatusPlugin.__init__(self,state='Inactive')
        self.__opponent = opponent
        self.__bet = 0
        if opponent == 'Player':
            self.__name = name
            self.__roundbet = round_bet
            self.balance = balance

    @property
    def bet(self):
        return self.__bet

    @bet.setter
    def bet(self,arg):
        # Testing argument
        while self.status.inactive:
            raise ValueError('cannot place bet when status is Inactive')
        # Executing.
        self.__bet = arg
        
    @property
    def event_trigger(self):
        return InsurancePlugin.__event_trigger
    
    @event_trigger.setter
    def event_trigger(self,arg):
        # Testing argument.
        if self.__opponent == 'Dealer':
            while arg not in (1,0):
                raise ValueError('expected argument True or False as boolean.')
        else:
            while arg == arg:
                raise ValueError('event cannot be set by player.')
        # Setting event.
        InsurancePlugin.__event_trigger = arg
         
    @property
    def condition(self):
        while InsurancePlugin.__condition == None:
            raise ValueError('condition was not set and cannot be returned')
        if self.__opponent == 'Player':
            if InsurancePlugin.__condition:
                self.__cond = False
                return self
            else:
                self.__cond = True
                return self
        else:
            cond = {1:'Win',0:'Lose'}
            return f"Dealer : {cond[InsurancePlugin.__condition]}"
    
    @condition.setter
    def condition(self,arg):
        # Testing argument.
        if self.__opponent == 'Dealer':
            while arg not in ('Win','Lose'):
                raise ValueError("expected argument 'Win' or 'Lose' as string.")
        else:
            while arg == arg:
                raise ValueError('condition cannot be set by player.')
        # Changing condition.
        if arg == 'Win':
            InsurancePlugin.__condition = True
        else:
            InsurancePlugin.__condition = False

    def resolver(self):
        if self.__opponent == 'Player':
            while self.status.active:
                if self.__cond:
                    view = f'+{crncy(self.__bet + (self.__bet * 2))}'
                    self.balance += self.__bet + (self.__bet * 2)
                else:
                    view = f'-{crncy(self.__bet)}'
                    self.__bet = 0
                print(f'{self.__name} | {view}')
                self.status = 'Inactive'

    def interface(self):
        # Testing user input.
        while True:
            projection = input(f'{self.__name}, would you like to place insurance? Use the numpad or type out your answer.\n1:YES | 0:NO')
            clear_output()
            try:
                int(projection)
            except ValueError:
                if projection.upper() not in ('YES','NO'):
                    print('Invalid argument, please try again.')
                    clear_output(True)
                    continue
                # Executing
                elif projection.upper() == 'YES':
                    self.status = 'Active'
                    break
                else:
                    break
            else:
                if int(projection) not in (1,0):
                    print('Invalid argument, please try again.')
                    clear_output(True)
                    continue
                # Executing
                elif int(projection):
                    self.status = 'Active'
                    break
                else:
                    break
        # Testing user input.
        while self.status.active:
            projection = input(f'Place your bet up to half of your round bet ({crncy(self.__roundbet / 2)} Max).\n')
            clear_output()
            try:
                int(projection)
            except ValueError:
                print('Argument was not a number, please try again.')
                clear_output(True)
                continue
            else:
                if int(projection) > (self.__roundbet * 0.5):
                    print('Amount is too large, please try again.')
                    clear_output(True)
                    continue
            # Executing
            self.__bet = int(projection)
            break

class DoubleDownPlugin(StatusPlugin):
    def __init__(self):
        StatusPlugin.__init__(self,state='Inactive')

class SplitPlugin:
    def interface(self,rank_splits):
        split_view = [f'\n{index}:{rank}' for index,rank in enumerate(rank_splits)]
        concat = ', '.join
        # Testing user input
        while True:
            projection = input(f"Which rank of your paired cards would you like to split? Use numpad or type out your answer.{''.join(split_view)}")
            clear_output()
            try:
                int(projection)
            except ValueError:
                if projection.capitalize() not in rank_splits:
                    print('Invalid argument,please try again.')
                    clear_output(True)
                    continue
                else:
                    return projection.capitalize()
            else:
                if int(projection) not in [index for index,value in enumerate(rank_splits)]:
                    print('Invalid argument, please try again.')
                    clear_output(True)
                    continue
                else:
                    return rank_splits[int(projection)]