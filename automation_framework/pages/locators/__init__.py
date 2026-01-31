from .products_locators import *
from .burger_menu_locators import *
from .login_locators import *

__all__ = []
__all__ += [name for name in globals().keys() if name.isupper()]

