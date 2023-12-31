from html import escape


def sanitize_xss(**kwargs) -> dict:
    new_args = {}

    for k, v in kwargs.items():
        new_args[k] = escape(str(v))

    return new_args
