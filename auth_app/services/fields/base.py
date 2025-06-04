import abc


class BaseFields(abc.ABC):
    cached_fields_str = None

    @classmethod
    @abc.abstractmethod
    def get_fields_list(cls) -> list[str]:
        """Retrieve the list of model fields"""
        pass

    @classmethod
    def get_fields_str(cls) -> str:
        """Retrieve the str containing the model fields"""
        if cls.cached_fields_str is None:
            cls.cached_fields_str = ', '.join(field for field in cls.get_fields_list())
        return cls.cached_fields_str
