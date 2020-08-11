from typing import Dict, List

# Is the class for a token-object to be passed through
# the business-process-graphs.
class Token:
    def __init__(self, attributes: Dict[str, any] = None):
        if attributes is None:
            self.attributes = {}
        else:
            self.attributes = attributes

    def __change_value(self, key, value):
        if key in self.attributes.keys():
            v_before = self.attributes[key]
            self.attributes[key] = value
            print("Token-State-Changed")
            print('attribute',key,'from', v_before,'to', value)
        else:
            print('ERROR: key', key,"not in token attributes")

    def init_keys(self, keys: List[str]):
        empty_value = 0
        self.attributes.fromkeys(keys, empty_value)

    def new_attribute(self, key, value):
        self.attributes[key] = value

    def change_value(self, key, value):
        self.__change_value(key, value)

    def get_all_attributes(self):
        return self.attributes

    def get_attribute(self, key):
        return self.attributes[key]

    def compare_token(self, other):
        other: Token
        if len(self.attributes) == len(other.attributes):
            for key in self.attributes.keys():
                if key in other.attributes.keys() and \
                        self.attributes[key] == other.attributes[key]:
                    pass
                else:
                    return False
        else:
            return False
        return True

    def __str__(self):
        return "token attribues: " + str(self.attributes)