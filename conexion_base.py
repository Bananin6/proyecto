from abc import ABC, abstractmethod

class ConexionBase(ABC):
    def __init__(self, db_name='base.db'):
        self.db_name = db_name

    @abstractmethod
    def conectar(self):
        pass