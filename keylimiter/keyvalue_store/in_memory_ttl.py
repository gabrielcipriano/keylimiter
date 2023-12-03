from . import KeyValueStore

from collections import OrderedDict
from typing import OrderedDict

from time import time

class InMemoryTtlStore(KeyValueStore):
    def __init__(self, ttl: int):
        """in memory ttl store
        
        Args:
            ttl (int, optional): ttl in seconds.
        """
        self._ttl = ttl 
        self.store: OrderedDict[str, tuple[str, int]] = OrderedDict() # key -> (value, expires_at)
    
    def get(self, key: str) -> any:
        self._cleanup()
        if key not in self.store:
            return None
        
        value, _ = self.store[key]
        return value
    
    def set(self, key: str, value: any) -> None:
        self.store[key] = (value, int(time()) + self._ttl,)
        self.store.move_to_end(key)
        
    def _cleanup(self):
        now = time()
        marked_to_delete = []
        
        for key, (_, expires_at) in self.store.items():
            if expires_at < now:
                marked_to_delete.append(key)
            else:
                break

        for key in marked_to_delete:
            del self.store[key]
                
        