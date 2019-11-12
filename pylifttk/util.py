
import typing as _typing

# External dependencies
try:
    # Python 3
    from enum import Enum as _Enum
except ImportError:  # pragma: no cover
    no_enum = True

    # Python 2 fallbacks
    try:
        from aenum import Enum as _Enum
        no_enum = False
    except ImportError:
        try:
            from enum34 import Enum as _Enum
            no_enum = False
        except ImportError:
            pass

    if no_enum:
        raise RuntimeError(
            """
            This package requires an `Enum` object type. These are available
            as part of the standard library in Python 3.4+, but otherwise
            require a third-party library, either `enum34` or `aenum`.

            => You can install it with `pip` or `pipenv`:
                    pip install --user aenum
               or
                    pipenv install aenum
            """)

# =============================================================================


def is_stringable(obj):
    # type: (str) -> bool
    try:
        str(obj)
    except:
        return False
    return True


def is_noarg_callable(obj):
    # type: (_typing.Any) -> bool
    try:
        obj()
    except:
        return False
    return True


def robust_str(obj, default="N/A"):
    # type: (_typing.Any, str) -> str
    obj_str = default
    if is_stringable(obj):
        obj_str = str(obj)
    return obj_str


def robust_float(obj, default=0.0):
    # type: (_typing.Any, _typing.Any) -> _typing.Union[float, _typing.Any]
    obj_float = default
    try:
        obj_float = float(obj)
    except ValueError:
        pass
    return obj_float


# =============================================================================


class DocEnum(_Enum):
    def __init__(self, value, doc):
        # type: (str, str) -> None
        try:
            super().__init__()
        except TypeError: # pragma: no cover
            # Python 2: the super() syntax was only introduced in Python 3.x
            super(DocEnum, self).__init__()
        self._value_ = value
        self.__doc__ = doc


# =============================================================================
