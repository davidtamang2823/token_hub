import abc
import typing

class AbstractUserService(abc.ABC):


    @abc.abstractmethod
    async def add_user_to_tenant(self, data: typing.Dict):
        ...
    
    @abc.abstractmethod
    async def remove_user_from_tenant(self, data: typing.Dict):
        ...

    