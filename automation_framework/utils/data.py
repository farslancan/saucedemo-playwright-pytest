import random
import string


def random_letters(length: int = 6) -> str:
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def random_digits(length: int = 4) -> str:
    return "".join(random.choice(string.digits) for _ in range(length))



__all__ = ["random_letters", "random_digits"]