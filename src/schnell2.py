from typing import Dict, Union, Optional


class Token(dict):
    # taken from
    # https://dev.to/0xbf/use-dot-syntax-to-access-dictionary-key-python-tips-10ec
    def __init__(self, attributes: Optional[Dict[str, Union[str, bool, int, float]]] = None) -> None:
        if attributes is not None:
            for attribute_key in attributes.keys():
                self.__setattr__(key=attribute_key, value=attributes[attribute_key])

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __repr__(self):
        return '<DictX ' + dict.__repr__(self) + '>'



if __name__ == '__main__':
    t = Token()
    t.card_inserted = True
    t['no'] = False
    rule = "t.card_inserted == True and t.no == False"
    print(eval(rule))

    t = Token(attributes={'a':1})
    rule = "t.a == 1"
    print(eval(rule))



    # try:
    #     print(eval(rule))
    # except NameError:
    #     print('NameError: You probably forget to put t. in front of every attribute')
    # except AttributeError:
    #     print('AttributeError: Your defined attribute is not present in the token')