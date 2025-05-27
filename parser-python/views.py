from collections import OrderedDict
import main.firstfollow
from main.firstfollow import production_list, nt_list as ntl, t_list as tl
from main.lexical_analyzer import generate_tokens2
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
nt_list, t_list=[], []

class State:

    _id=0
    def __init__(self, closure):
        self.closure=closure
        self.no=State._id
        State._id+=1

class Item(str):
    def __new__(cls, item, lookahead=list()):
        self=str.__new__(cls, item)
        self.lookahead=lookahead
        return self

    def __str__(self):
        return super(Item, self).__str__()+", "+'|'.join(self.lookahead)
        


def closure(items):

    def exists(newitem, items):

        for i in items:
            if i==newitem and sorted(set(i.lookahead))==sorted(set(newitem.lookahead)):
                return True
        return False


    global production_list

    while True:
        flag=0
        for i in items: 
            
            if i.index('.')==len(i)-1: continue

            Y=i.split('->')[1].split('.')[1][0]

            if i.index('.')+1<len(i)-1:
                lastr=list(main.firstfollow.compute_first(i[i.index('.')+2])-set(chr(1013)))
                
            else:
                lastr=i.lookahead
            
            for prod in production_list:
                head, body=prod.split('->')
                
                if head!=Y: continue
                
                newitem=Item(Y+'->.'+body, lastr)

                if not exists(newitem, items):
                    items.append(newitem)
                    flag=1
        if flag==0: break

    return items

def goto(items, symbol):

    global production_list
    initial=[]

    for i in items:
        if i.index('.')==len(i)-1: continue

        head, body=i.split('->')
        seen, unseen=body.split('.')


        if unseen[0]==symbol and len(unseen) >= 1:
            initial.append(Item(head+'->'+seen+unseen[0]+'.'+unseen[1:], i.lookahead))

    return closure(initial)


def calc_states():

    def contains(states, t):

        for s in states:
            if len(s) != len(t): continue

            if sorted(s)==sorted(t):
                for i in range(len(s)):
                        if s[i].lookahead!=t[i].lookahead: break
                else: return True

        return False

    global production_list, nt_list, t_list

    head, body=production_list[0].split('->')


    states=[closure([Item(head+'->.'+body, ['$'])])]
    
    while True:
        flag=0
        for s in states:

            for e in nt_list+t_list:
                
                t=goto(s, e)
                if t == [] or contains(states, t): continue

                states.append(t)
                flag=1

        if not flag: break
    
    return states 

def serialize_table(table):
    serializable_table = {}
    for state_no, transitions in table.items():
        serializable_table[state_no] = {}
        for symbol, action in transitions.items():
            if isinstance(action, set):
                serializable_table[state_no][symbol] = list(action)
            else:
                serializable_table[state_no][symbol] = action
    return serializable_table

def make_table(states):

    global nt_list, t_list

    def getstateno(t):

        for s in states:
            if len(s.closure) != len(t): continue

            if sorted(s.closure)==sorted(t):
                for i in range(len(s.closure)):
                        if s.closure[i].lookahead!=t[i].lookahead: break
                else: return s.no

        return -1

    def getprodno(closure):

        closure=''.join(closure).replace('.', '')
        return production_list.index(closure)

    SLR_Table=OrderedDict()
    
    for i in range(len(states)):
        states[i]=State(states[i])

    for s in states:
        SLR_Table[s.no]=OrderedDict()

        for item in s.closure:
            head, body=item.split('->')
            if body=='.': 
                for term in item.lookahead: 
                    if term not in SLR_Table[s.no].keys():
                        SLR_Table[s.no][term]={'r'+str(getprodno(item))}
                    else: SLR_Table[s.no][term] |= {'r'+str(getprodno(item))}
                continue

            nextsym=body.split('.')[1]
            if nextsym=='':
                if getprodno(item)==0:
                    SLR_Table[s.no]['$']='accept'
                else:
                    for term in item.lookahead: 
                        if term not in SLR_Table[s.no].keys():
                            SLR_Table[s.no][term]={'r'+str(getprodno(item))}
                        else: SLR_Table[s.no][term] |= {'r'+str(getprodno(item))}
                continue

            nextsym=nextsym[0]
            t=goto(s.closure, nextsym)
            if t != []: 
                if nextsym in t_list:
                    if nextsym not in SLR_Table[s.no].keys():
                        SLR_Table[s.no][nextsym]={'s'+str(getstateno(t))}
                    else: SLR_Table[s.no][nextsym] |= {'s'+str(getstateno(t))}

                else: SLR_Table[s.no][nextsym] = str(getstateno(t))

    return SLR_Table

def augment_grammar():

    for i in range(ord('Z'), ord('A')-1, -1):
        if chr(i) not in nt_list:
            start_prod=production_list[0]
            production_list.insert(0, chr(i)+'->'+start_prod.split('->')[0]) 
            return
        
@csrf_exempt
def parser_CLR(request):
     
    input_json = request.body.decode('utf-8')
    input_data = json.loads(input_json)
    code = input_data.get("code", "")
    grammar = input_data.get("grammar", "")
    if code:

     with open("main/temp_input_code.txt", "w") as f:
        f.write(code)
    else:
        input_filename = "main/input_code_7.txt"
        Input = generate_tokens2(input_filename) + '$'

  
    global production_list, ntl, nt_list, tl, t_list 

    main.firstfollow.main(grammar)
    print('\n\n__________________________________________________________________________________________________________________________________________________\n')
    print("FIRST AND FOLLOW OF NON-TERMINALS\n")
    first_follow = {}

    for nt in ntl:
        main.firstfollow.compute_first(nt)
        main.firstfollow.compute_follow(nt)
    
        first_follow[nt] = {
            "first": list(main.firstfollow.get_first(nt)),
            "follow": list(main.firstfollow.get_follow(nt))
        }
        print(nt)
        print("\tFIRST:\t", first_follow[nt]["first"])
        print("\tFOLLOW:\t", first_follow[nt]["follow"], "\n")
        

    augment_grammar()
    nt_list=list(ntl.keys())
    t_list=list(tl.keys()) + ['$']

    print('\n__________________________________________________________________________________________________________________________________________________\n')
    print("NON TERMINALS : {}\n".format(nt_list))
    print("TERMINALS : {}".format(t_list))

    j=calc_states()

    ctr=0
    print('\n__________________________________________________________________________________________________________________________________________________\n')
    print("CANONICAL ITEMSETS\n")
    for s in j:
        print("ITEM {}:".format(ctr))
        for i in s:
            print("\t", i)
        ctr+=1

    canonical_items = []
    for idx, state in enumerate(j):
        state_dict = {
            "state_no": idx,
            "items": [str(item) for item in state]  # Ensure each item is a string
        }
        canonical_items.append(state_dict)

    table=make_table(j)
    print('\n__________________________________________________________________________________________________________________________________________________\n')
    print("\nCLR(1) TABLE\n")
    sym_list = nt_list + t_list
    sr, rr=0, 0
    print('\t|  ','\t|  '.join(sym_list),'\t\t|')
    print('\n__________________________________________________________________________________________________________________________________________________\n')
    for i, j in table.items():
            
        print(i, "\t|  ", '\t|  '.join(list(j.get(sym,' ') if type(j.get(sym))in (str , None) else next(iter(j.get(sym,' ')))  for sym in sym_list)),'\t\t|')
        s, r=0, 0

        for p in j.values():
            if p!='accept' and len(p)>1:
                p=list(p)
                if('r' in p[0]): r+=1
                else: s+=1
                if('r' in p[1]): r+=1
                else: s+=1      
        if r>0 and s>0: sr+=1
        elif r>0: rr+=1
    print('\n_____________________________________________________________________________________________________________________________________________\n')
    print("\nRESULTS OF CLR\n")
    print("\n", sr, "s/r conflicts |", rr, "r/r conflicts")
    print('\n_____________________________________________________________________________________________________________________________________________\n')
    print("\n\nPHASE 2 OF A COMPILER : SYNTAX ANALYSIS")
    print("ENTER THE FILENAME OF THE INPUT PROGRAM TO BE PARSED\n(syntax analysis will be performed on this program according to the grammar provided)")
    Input = generate_tokens2("main/temp_input_code.txt") + '$'
    print('\n_____________________________________________________________________________________________________________________________________________\n')
    print("INPUT PROGRAM IN THE FORM OF STRING OF TOKENS\n")
    print(Input)
    try:
        parsing_steps = []
        stack = ['0']
        a = list(table.items())

        while len(Input) != 0:
            step = {}
            curr_state = int(stack[-1])
            symbol = Input[0]
            action = list(a[curr_state][1][symbol])[0]

            step['stack'] = ''.join(stack)
            step['input'] = ''.join(Input)

            if action[0] == "s":
                step['action'] = f"Shift {symbol}"
                stack.append(symbol)
                stack.append(action[1:])
                Input = Input[1:]

            elif action[0] == "r":
                rule_num = int(action[1:])
                production = production_list[rule_num]  # e.g. B → b
                lhs = production[0]
                rhs_len = len(production[3:])  # skip '→'
                stack = stack[:-2 * rhs_len]  # pop 2 * |RHS| (symbol + state)
                goto_state = a[int(stack[-1])][1][lhs]
                stack.append(lhs)
                stack.append(goto_state)
                step['action'] = f"Reduce using {production}"

            elif action[0] == "a":
                step['action'] = "Accept"
                step['stack'] = ''.join(stack)
                step['input'] = ''.join(Input)
                parsing_steps.append(step)
                break

            parsing_steps.append(step)

    
        result = {
            "first_follow": first_follow,
            "canonical_items": [
                {
                    "state_no": i,
                    "items": [str(item) for item in state]
                }
                for i, state in enumerate(j)
            ],
            "clr_table": serialize_table(table),
            "parsing_steps": parsing_steps,
            "status": "Input accepted. Syntactically correct."
        }

    except Exception as e:
        result = {
            "first_follow": first_follow,
            "canonical_items":canonical_items,
            "clr_table": serialize_table(table),
            "parsing_steps": parsing_steps,
            "status": "Input not accepted. Syntactically incorrect.",
            "error": str(e)
        }
    return JsonResponse(result,safe=False)


@csrf_exempt
def parser_SLR(request):
    global production_list, ntl, nt_list, tl, t_list

    firstfollow.main()
    print('\n\n__________________________________________________________________________________________________________________________________________________\n')
    print("FIRST AND FOLLOW OF NON-TERMINALS\n")
    for nt in ntl:
        firstfollow.compute_first(nt)
        firstfollow.compute_follow(nt)
        print(nt)
        print("\tFIRST:\t", firstfollow.get_first(nt))
        print("\tFOLLOW:\t", firstfollow.get_follow(nt), "\n")

    augment_grammar()
    nt_list = list(ntl.keys())
    t_list = list(tl.keys()) + ['$']

    print('\n__________________________________________________________________________________________________________________________________________________\n')
    print("NON TERMINALS : {}\n".format(nt_list))
    print("TERMINALS : {}".format(t_list))

    j = calc_states()

    ctr = 0
    print('\n__________________________________________________________________________________________________________________________________________________\n')
    print("CANONICAL ITEMSETS\n")
    for s in j:
        print("ITEM {}:".format(ctr))
        for i in s:
            print("\t", i)
        ctr += 1

    table = make_table(j)
    print('\n__________________________________________________________________________________________________________________________________________________\n')
    print("\nSLR(1) TABLE\n")
    sym_list = nt_list + t_list
    sr, rr = 0, 0
    print('\t|  ', '\t|  '.join(sym_list), '\t\t|')
    print('\n__________________________________________________________________________________________________________________________________________________\n')
    for i, j in table.items():
        print(i, "\t|  ", '\t|  '.join(
            list(j.get(sym, ' ') if type(j.get(sym)) in (str, None) else next(iter(j.get(sym, ' '))) for sym in sym_list)),
            '\t\t|')
        s, r = 0, 0
        for p in j.values():
            if p != 'accept' and len(p) > 1:
                p = list(p)
                if ('r' in p[0]):
                    r += 1
                else:
                    s += 1
                if ('r' in p[1]):
                    r += 1
                else:
                    s += 1
        if r > 0 and s > 0:
            sr += 1
        elif r > 0:
            rr += 1
    print('\n_____________________________________________________________________________________________________________________________________________\n')
    print("\nRESULTS OF SLR\n")
    print("\n", sr, "s/r conflicts |", rr, "r/r conflicts")
    print('\n_____________________________________________________________________________________________________________________________________________\n')
    print("\n\nPHASE 2 OF A COMPILER : SYNTAX ANALYSIS")
    print("ENTER THE FILENAME OF THE INPUT PROGRAM TO BE PARSED\n(syntax analysis will be performed on this program according to the grammar provided)")
    input_filename = input()
    Input = generate_tokens2(input_filename) + '$'
    print('\n_____________________________________________________________________________________________________________________________________________\n')
    print("INPUT PROGRAM IN THE FORM OF STRING OF TOKENS\n")
    print(Input)
    try:
        stack = ['0']
        a = list(table.items())
        print('\n_____________________________________________________________________________________________________________________________________________\n')
        print("PRODUCTIONS\t:", production_list)
        print('\n_____________________________________________________________________________________________________________________________________________\n')
        print('\n\n_____________________________________________________________________________________________________________________________________________\n')
        print('STACK', "\t\t\t\t\t", 'INPUT')
        print('_____________________________________________________________________________________________________________________________________________\n')
        print(*stack, "\t\t\t\t\t", *Input, sep="")
        while len(Input) != 0:
            top_state = int(stack[-1])
            current_token = Input[0]

            if current_token not in table[top_state]:
                raise Exception("Parsing error: token not in table")

            actions = table[top_state][current_token]
            # actions is either a string or a set of actions, take one (if multiple, conflicts exist)
            if isinstance(actions, set):
                action = next(iter(actions))
            else:
                action = actions

            if action[0] == "s":
                # shift action
                stack.append(current_token)
                stack.append(action[1:])
                Input = Input[1:]
                print(*stack, "\t\t\t\t\t", *Input, sep="")
            elif action[0] == "r":
                # reduce action
                prod_num = int(action[1:])
                prod = production_list[prod_num]
                head, body = prod.split('->')
                body_len = len(body)
                if body == 'ε':  # epsilon production special case
                    pop_len = 0
                else:
                    pop_len = 2 * body_len  # because stack stores states and symbols
                stack = stack[:-pop_len]
                top_state = int(stack[-1])
                goto_state = table[top_state][head]
                if isinstance(goto_state, set):
                    goto_state = next(iter(goto_state))
                stack.append(head)
                stack.append(goto_state if isinstance(goto_state, str) else str(goto_state))
                print(*stack, "\t \t\t \t", *Input, sep="")
            elif action == "accept":
                print('\n_____________________________________________________________________________________________________________________________________________\n')
                print("RESULT\n")
                print("STRING ACCEPTED. INPUT PROGRAM IS SYNTACTICALLY CORRECT")
                print('\n_____________________________________________________________________________________________________________________________________________\n')
                break
            else:
                raise Exception("Unknown action")
    except:
        print('\n_____________________________________________________________________________________________________________________________________________\n')
        print("RESULT\n")
        print('\nxx STRING NOT ACCEPTED. INPUT PROGRAM IS SYNTACTICALLY WRONG xx\n')
        print('\n_____________________________________________________________________________________________________________________________________________\n')
    return
