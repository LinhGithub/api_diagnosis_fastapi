from mongo_connect import mongo_create
from datetime import datetime, timedelta

mydb = mongo_create()

def assert_fact(fact,facts):
    fact_new = None
    if not fact in facts:
        fact_new = fact
    
    return {'facts':fact_new}

def check_assert(rules, facts):
    is_changed = True
    factsNew = facts.copy()

    if rules:
        while is_changed:
            is_changed = False
            for fact in factsNew:
                for rule in rules:
                    if len(rule[0]) == 1:
                        if fact[0] == rule[0][0]:
                            result = assert_fact([rule[1],fact[1]], factsNew)
                            if result.get('facts'):
                                is_changed = True
                                factsNew.append(result.get('facts'))
                    else:
                        _check = True
                        fact_exists = []
                        for f in factsNew:
                            fact_exists.append(f[0])
                        
                        for r in rule[0]:
                            if r not in fact_exists:
                                _check=False
                                break

                        if _check:
                            result = assert_fact([rule[1],fact[1]], factsNew)
                            if result.get('facts'):
                                is_changed = True
                                factsNew.append(result.get('facts'))

    return {"facts": factsNew}

def get_now():
    return datetime.now() + timedelta(hours=7)