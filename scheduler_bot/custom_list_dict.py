from typing import Any


class CustomListDict(dict):
    """
    This class inherits main functional from the builtin dict,
    resolving the "get" method
    """
    def get(self, __key) -> Any or []:
        """
        Works same as dict, but returns an empty list if no key
        :param __key: dict key
        :return: Any or an empty list ([])
        """
        if __key in self:
            return self[__key]
        return []
