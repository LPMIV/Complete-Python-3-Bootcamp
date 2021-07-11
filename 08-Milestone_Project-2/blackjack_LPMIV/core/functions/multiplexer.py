from babel.numbers import format_currency

def crncy(currency):
    return format_currency(currency,'USD',locale='en_US')


class Log:
    def __init__(self):
        pass

    @property
    def resolver(self):
        try:
            self.__resolve
        except AttributeError:
            return 'Not Resolved'
        else:
            return self.__resolve

    @resolver.setter
    def resolver(self,arg):
        # Testing argument.
        while arg != 'Resolved':
            raise ValueError("expected argument 'Resolved', as string.")
        # Executing.
        self.__resolve = arg


class Debug:
    def __init__(self):
        self.__log = []
        
    @property
    def log(self):
        for i in self.__log:
            print(i)
            
    def clear(self):
        self.__log.clear()
    
    def __call__(self,string):
        try:
            cycle
        except NameError:
            pass
        else:
            view = f'Cycle:{cycle}, {string} | Dealer Log: {dealer.initial_deal.log}'
            self.__log.append(view)
debug = Debug()