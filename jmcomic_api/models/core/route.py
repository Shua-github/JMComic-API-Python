from typing import List
from abc import ABC, abstractmethod

class Route(ABC):
    path:str
    method:List
    
    @abstractmethod
    async def route_def(self):
        pass