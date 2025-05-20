from collections import deque
from collections import OrderedDict
from pprint import pprint
import firstfollow
from firstfollow import production_list, nt_list as ntl, t_list as tl
from lexical_analyzer import generate_tokens2
from django.http import JsonResponse

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
                lastr=list(firstfollow.compute_first(i[i.index('.')+2])-set(chr(1013)))
                
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
        

def parser(request):
    global production_list, ntl, nt_list, tl, t_list    

   
    input_json = request.body.decode('utf-8')
    import json
    input_data = json.loads(input_json)
    code = input_data.get("code", "")

  
    firstfollow.main()
    first_follow_result = {}
    for nt in ntl:
        firstfollow.compute_first(nt)
        firstfollow.compute_follow(nt)
        first_follow_result[nt] = {
            "FIRST": list(firstfollow.get_first(nt)),
            "FOLLOW": list(firstfollow.get_follow(nt))
        }

   
    augment_grammar()
    nt_list = list(ntl.keys())
    t_list = list(tl.keys()) + ['$']

   
    states = calc_states()

    canonical_items = []
    for i, state in enumerate(states):
        canonical_items.append({
            "item_no": i,
            "items": [str(item) for item in state]
        })

   
    clr_table = make_table(states)
    table_display = {}
    sym_list = nt_list + t_list
    for state_no, transitions in clr_table.items():
        row = {}
        for sym in sym_list:
            cell = transitions.get(sym, '')
            if isinstance(cell, set):
                cell = list(cell)[0] if len(cell) == 1 else list(cell)
            row[sym] = cell if cell else ""
        table_display[state_no] = row

   
    Input = generate_tokens2(code) + '$'

    
    stack_steps = []
    try:
        stack = ['0']
        a = list(clr_table.items())
        i = 0
        stack_steps.append({
            "stack": stack.copy(),
            "input": list(Input)
        })

        while Input:
            curr_state = int(stack[-1])
            action = clr_table[curr_state].get(Input[0], None)

            if not action:
                raise ValueError("Invalid transition")

            if isinstance(action, set):
                action = list(action)[0]

            if action.startswith("s"):
                stack.append(Input[0])
                stack.append(action[1:])
                Input = Input[1:]
            elif action.startswith("r"):
                prod_index = int(action[1:])
                prod = production_list[prod_index]
                lhs, rhs = prod.split("->")
                symbols_to_pop = len(rhs) * 2
                stack = stack[:-symbols_to_pop]
                curr_state = int(stack[-1])
                goto_state = clr_table[curr_state][lhs]
                stack.append(lhs)
                stack.append(goto_state)
            elif action == "accept":
                stack_steps.append({
                    "stack": stack.copy(),
                    "input": list(Input),
                    "status": "ACCEPT"
                })
                break

            stack_steps.append({
                "stack": stack.copy(),
                "input": list(Input)
            })

        result = {
            "first_follow": first_follow_result,
            "canonical_items": canonical_items,
            "clr_table": table_display,
            "parsing_steps": stack_steps,
            "status": "Input accepted. Syntactically correct."
        }

    except Exception as e:
        result = {
            "first_follow": first_follow_result,
            "canonical_items": canonical_items,
            "clr_table": table_display,
            "parsing_steps": stack_steps,
            "status": "Input not accepted. Syntactically incorrect.",
            "error": str(e)
        }

    return JsonResponse(result)

# Create your views here.
