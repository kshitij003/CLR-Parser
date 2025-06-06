from re import *
from collections import OrderedDict

t_list=OrderedDict()
nt_list=OrderedDict()
production_list=[]

# ------------------------------------------------------------------

class Terminal:

    def __init__(self, symbol):
        self.symbol=symbol

    def __str__(self):
        return self.symbol

# ------------------------------------------------------------------

class NonTerminal:

    def __init__(self, symbol):
        self.symbol=symbol
        self.first=set()
        self.follow=set()

    def __str__(self):
        return self.symbol

    def add_first(self, symbols): self.first |= set(symbols) #union operation

    def add_follow(self, symbols): self.follow |= set(symbols)

# ------------------------------------------------------------------


def compute_first(symbol): #chr(1013) corresponds (ϵ) in Unicode



# if X is a terminal then first(X) = X
    if symbol in t_list:
        return set(symbol)

    for prod in production_list:
        head, body=prod.split('->')
        
        if head!=symbol: continue

# if X -> is a production, then first(X) = epsilon
        if body=='':
            nt_list[symbol].add_first(chr(1013))
            continue

        

        for i, Y in enumerate(body):
# for X -> Y1 Y2 ... Yn, first(X) = non-epsilon symbols in first(Y1)
# if first(Y1) contains epsilon, 
#   first(X) = non-epsilon symbols in first(Y2)
#   if first(Y2) contains epsilon
#   ...
            if body[i]==symbol: continue
            t=compute_first(Y)
            nt_list[symbol].add_first(t-set(chr(1013)))
            if chr(1013) not in t:
                break 
# for i=1 to n, if Yi contains epsilon, then first(X)=epsilon
            if i==len(body)-1: 
                nt_list[symbol].add_first(chr(1013))

    return nt_list[symbol].first

# ------------------------------------------------------------------

def get_first(symbol): #wrapper method for compute_first

    return compute_first(symbol)

# ------------------------------------------------------------------

def compute_follow(symbol):



# if A is the start symbol, follow (A) = $
    if symbol == list(nt_list.keys())[0]: #this is okay since I'm using an OrderedDict
        nt_list[symbol].add_follow('$')

    for prod in production_list:    
        head, body=prod.split('->')

        for i, B in enumerate(body):        
            if B != symbol: continue

# for A -> aBb, follow(B) = non-epsilon symbols in first(b)
            if i != len(body)-1:
                nt_list[symbol].add_follow(get_first(body[i+1]) - set(chr(1013)))

# if A -> aBb where first(b) contains epsilon, or A -> aB then follow(B) = follow (A)
            if i == len(body)-1 or chr(1013) in get_first(body[i+1]) and B != head: 
                nt_list[symbol].add_follow(get_follow(head))

# ------------------------------------------------------------------

def get_follow(symbol):


    if symbol in t_list.keys():
        return None
    
    return nt_list[symbol].follow

# ------------------------------------------------------------------    

def main(grammar):
    global production_list, nt_list, t_list
    F = open(grammar,"r")

    ctr=1


    

    for line in F:
            line = line.replace(' ','')
            line = line.replace('\n','')
            production_list.append(line)
            if production_list[-1].lower() in ['end', '']: 
                del production_list[-1]
                break

            head, body=production_list[ctr-1].split('->')

            if head not in nt_list.keys():
                nt_list[head]=NonTerminal(head)

            #for all terminals in the body of the production
            for i in body:
                if not 65<=ord(i)<=90:
                    if i not in t_list.keys(): t_list[i]=Terminal(i)
            #for all non-terminals in the body of the production
                elif  i not in nt_list.keys(): nt_list[i]=NonTerminal(i)
                
            ctr+=1

                
    return 
# ------------------------------------------------------------------

if __name__=='__main__':
    
    main()