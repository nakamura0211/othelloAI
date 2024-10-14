import abc


class Agent(abc.ABC):
    @abc.abstractmethod
    def __call__(self, othello,color:int)->tuple[int,int]:
        pass

    @abc.abstractmethod
    def act(self,state)->int:
        pass