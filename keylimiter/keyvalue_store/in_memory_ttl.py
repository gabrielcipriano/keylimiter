from . import KeyValueStore

from collections import OrderedDict
from typing import OrderedDict

from time import monotonic

from typing import Callable

class InMemoryTtlStore(KeyValueStore):
    def __init__(self, ttl: int, time_func: Callable[[], float] = monotonic):
        """in memory ttl store
        
        Args:
            ttl (int, optional): ttl in seconds.
        """
        self._ttl = ttl 
        self._store: OrderedDict[str, tuple[str, float]] = OrderedDict() # key -> (value, expires_at)
        self._time = time_func
        
    
    def get(self, key: str) -> any:
        self._cleanup()
        if key not in self._store:
            return None
        
        value, _ = self._store[key]
        return value
    
    def set(self, key: str, value: any) -> None:
        self._store[key] = (value, self._time() + self._ttl,)
        self._store.move_to_end(key)
        
    def _cleanup(self):
        now = self._time()
        marked_to_delete = []
        
        for key, (_, expires_at) in self._store.items():
            if expires_at < now:
                marked_to_delete.append(key)
            else:
                break

        for key in marked_to_delete:
            del self._store[key]
                
        