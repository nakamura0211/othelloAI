import numpy as np
import abc

State = np.ndarray[np.ndarray[np.ndarray[np.uint8]]]
Action = np.uint8 | tuple[np.uint8, np.uint8]


class Agent(abc.ABC):
    @abc.abstractmethod
    def act(self, state: State) -> Action:
        pass
