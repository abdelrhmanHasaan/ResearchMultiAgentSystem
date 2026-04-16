from abc import ABC, abstractmethod
from typing import Dict


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def run(self, data: Dict) -> Dict:
        """
        Each agent receives data and returns updated data
        """
        pass