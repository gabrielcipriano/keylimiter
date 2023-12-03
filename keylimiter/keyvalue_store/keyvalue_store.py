from abc import ABC, abstractmethod 
from typing import TypeVar, Generic

class KeyValueStore(ABC): 
  
    @abstractmethod
    def get(self, key: str) -> any:
        """
        returns the value for the key, or None if the key doesn't exist
        """
        pass
    
    @abstractmethod
    def set(self, key: str, value: any) -> None:
        """
        Sets the value for the key
        """
        pass
    
    
T = TypeVar('T')

class NamespacedKVStore(KeyValueStore, Generic[T]): 
    def __init__(self, namespace: str, store: KeyValueStore):
        self.namespace = namespace + "::"
        self.store = store
    
    def get(self, key: str) -> T:
        return self.store.get(self.namespace + key)
    
    def set(self, key: str, value: T) -> None:
        self.store.set(self.namespace + key, value)
