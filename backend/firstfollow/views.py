from django.http import JsonResponse
from collections import OrderedDict
import json

class Terminal:
    def __init__(self, symbol):
        self.symbol = symbol

    def __str__(self):
        return self.symbol

class NonTerminal:
    def __init__(self, symbol):
        self.symbol = symbol
        self.first = set()
        self.follow = set()

    def __str__(self):
        return self.symbol

    def add_first(self, symbols):
        self.first |= set(symbols)

    def add_follow(self, symbols):
        self.follow |= set(symbols)

def firstfollow(request):
    production_list = []
    t_list = OrderedDict()
    nt_list = OrderedDict()

    if request.method == "POST":
        try:
            if request.content_type == 'application/json':
                body = json.loads(request.body)
                data = body.get('productions', [])
            else:
                data = request.POST.getlist('productions[]')
        except Exception as e:
            return JsonResponse({'error': f'Invalid input format: {str(e)}'})

        # Parse productions
        for prod in data:
            prod = prod.replace(" ", "")
            if prod.lower() in ['end', '']:
                continue

            production_list.append(prod)
            head, body = prod.split('->')

            if head not in nt_list:
                nt_list[head] = NonTerminal(head)

            for symbol in body:
                if not symbol.isupper():
                    if symbol not in t_list:
                        t_list[symbol] = Terminal(symbol)
                else:
                    if symbol not in nt_list:
                        nt_list[symbol] = NonTerminal(symbol)

        # FIRST
        def compute_first(symbol):
            if symbol in t_list:
                return set(symbol)

            for prod in production_list:
                head, body = prod.split('->')
                if head != symbol:
                    continue

                if body == '':
                    nt_list[symbol].add_first(chr(1013))
                    continue

                for i, Y in enumerate(body):
                    if body[i] == symbol:
                        continue
                    t = compute_first(Y)
                    nt_list[symbol].add_first(t - set(chr(1013)))
                    if chr(1013) not in t:
                        break
                    if i == len(body) - 1:
                        nt_list[symbol].add_first(chr(1013))
            return nt_list[symbol].first

        def get_first(symbol):
            return compute_first(symbol)

        # FOLLOW
        def compute_follow(symbol):
            if symbol == list(nt_list.keys())[0]:
                nt_list[symbol].add_follow('$')

            for prod in production_list:
                head, body = prod.split('->')
                for i, B in enumerate(body):
                    if B != symbol:
                        continue
                    if i != len(body) - 1:
                        nt_list[symbol].add_follow(get_first(body[i + 1]) - set(chr(1013)))
                    if i == len(body) - 1 or chr(1013) in get_first(body[i + 1]):
                        if B != head:
                            nt_list[symbol].add_follow(get_follow(head))

        def get_follow(symbol):
            if symbol in t_list:
                return None
            return nt_list[symbol].follow

        # Execute
        for nt in nt_list:
            compute_first(nt)
        for nt in nt_list:
            compute_follow(nt)

        # Result formatting
        result = {
            nt: {
                'FIRST': sorted(list(nt_list[nt].first)),
                'FOLLOW': sorted(list(nt_list[nt].follow))
            } for nt in nt_list
        }

        return JsonResponse({'result': result}, status=200)

    return JsonResponse({'error': 'Only POST method allowed'}, status=405)
