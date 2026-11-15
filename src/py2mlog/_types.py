# used in mlog/mlog_expressions.py


class Content:
    pass


# there is an actual Color 'builtin' to be generated later
class ColorType:
    """
    Represents an Mlog color literal, e.g. %ffffff.
    Subclass of 'float', so arithmetic is supported.
    """
