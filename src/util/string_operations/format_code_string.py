import re


def format_code_string(text: str) -> str:
    """
    src = inspect.getsource(my_func) allows to get a string of the original
    source at runtime. But source code contains tabs, new line and alot of
    spaces.
    This function removes all whitespace-characters.
    """
    text = text.replace('\t', '')
    text = text.replace('\n', '')
    text = re.sub(' +', ' ', text)
    return text