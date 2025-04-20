from django.http import JsonResponse
from collections import OrderedDict


first_sets = {}
follow_sets = {}
nt_list = []
t_list = []

def clr_states(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        
        productions = data.get('productions', [])
        firstfollow_data = data.get('firstfollow', {}) 

        global production_list, nt_list, t_list, first_sets, follow_sets
        production_list.clear()
        nt_list.clear()
        t_list.clear()
        first_sets.clear()
        follow_sets.clear()

        for prod in productions:
            prod = prod.replace(' ', '')
            if '->' in prod:
                head, body = prod.split('->')
                production_list.append(f"{head}->{body}")
                if head not in nt_list:
                    nt_list.append(head)
                for sym in body:
                    if not sym.isupper() and sym not in t_list:
                        t_list.append(sym)

        if '$' not in t_list:
            t_list.append('$')

        for nt, sets in firstfollow_data.items():
            if nt not in nt_list:
                nt_list.append(nt)
            first_sets[nt] = sets.get('first', [])
            follow_sets[nt] = sets.get('follow', [])

        augment_grammar()

        nt_list = list({prod.split('->')[0] for prod in production_list})
        t_list = list({sym for prod in production_list for sym in prod.split('->')[1] if not sym.isupper()}) + ['$']

        def compute_first(symbols):
            result = set()
            for sym in symbols:
                if sym == '':
                    continue
                if sym not in first_sets:
                    result.add(sym)
                    break
                result.update(first_sets[sym])
                if 'ε' not in first_sets[sym]:
                    break
            return result

        def patched_closure(items):
            def exists(newitem, items):
                for i in items:
                    if i == newitem and sorted(set(i.lookahead)) == sorted(set(newitem.lookahead)):
                        return True
                return False

            while True:
                flag = 0
                for i in items[:]:
                    if i.index('.') == len(i) - 1:
                        continue
                    Y = i.split('->')[1].split('.')[1][0]
                    if i.index('.') + 1 < len(i) - 1:
                        rest = i[i.index('.')+2:]
                        lastr = list(compute_first(rest) - set(['ε']))
                    else:
                        lastr = i.lookahead

                    for prod in production_list:
                        head, body = prod.split('->')
                        if head != Y:
                            continue
                        newitem = Item(Y + '->.' + body, lastr)
                        if not exists(newitem, items):
                            items.append(newitem)
                            flag = 1
                if flag == 0:
                    break
            return items

        import types
        from . import clrparser
        clrparser.closure = types.FunctionType(patched_closure._code_, globals())

        states = calc_states()

        states_json = OrderedDict()
        for i, state in enumerate(states):
            state_json = OrderedDict()
            for j, item in enumerate(state):
                state_json[str(j)] = str(item)
            states_json[str(i)] = state_json

        return JsonResponse({'states': states_json})