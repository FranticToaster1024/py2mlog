# used in mlog/mlog_expressions.py


class Content:
    pass


class _Color:  # pyright: ignore[reportUnusedClass]
    """
    Represents an Mlog color literal, e.g. %ffffff.
    Subclass of 'float', so arithmetic is supported.
    """
