from . import KeyLimiter
from .keyvalue_store import InMemoryTtlStore, NamespacedKVStore

from time import monotonic
from math import floor, ceil
from threading import Lock

from typing import Literal, TypedDict, Callable

WindowUnit = Literal['second'] | Literal['minute'] |  Literal['hour']

Window = TypedDict('Window', {'count': int, 'id': int})

class SlidingWindowCounterLimiter(KeyLimiter):
    _max_requests: int
    _window: NamespacedKVStore[Window] # key -> (count, window_id)
    _prev_window: NamespacedKVStore[Window] # key -> (count, window_id)
    _time:  Callable[[], float] 
    _lock: Lock
    
    _window_unit: WindowUnit
    """_window_unit is the unit of the time window: "second" | "minute" | "hour" """
    
    _window_interval: float
    """_window_interval is the number of seconds in a time window"""
    
    
    def __init__(self, max_requests: int, window_unit: WindowUnit, time_func=monotonic):
        """
        :param int max_requests: maximum number of requests in a window
        :param str window_unit: "second" | "minute" | "hour". Default: "minute"
        :param Callable[[], float] time_func: function that returns the current time in seconds. Default: monotonic
        """
        match(window_unit):
            case "second":
                self._window_interval = 1
            case "minute":
                self._window_interval = 60
            case "hour":
                self._window_interval = 60*60
            case _:
                assert False, "Invalid window_unit"
                
        self._window_unit = window_unit
        self._max_requests = max_requests
        self._time = time_func
        self._lock = Lock()
        
        ttl_kvstore = InMemoryTtlStore(self._window_interval*2, time_func)
        
        self._window = NamespacedKVStore[Window]("currw", ttl_kvstore)
        self._prev_window = NamespacedKVStore[Window]("prevw", ttl_kvstore)
    
    
    def allow(self, key: str) -> bool:
        with self._lock:
            return self._allow(key)
    
    def _allow(self, key: str) -> bool:
        self._tick(key)
        if (self._count_rolling_window(key) < self._max_requests):
            window = self._window.get(key)
            window['count'] += 1
            return True
        return False
    
    
    def limit(self, key: str) -> int:
        return self._max_requests
    
    
    def remaining(self, key: str) -> int:
        with self._lock:
            return self._remaining(key)
        
    def _remaining(self, key: str) -> int:
        self._tick(key)
        return self._max_requests - self._count_rolling_window(key)
    
    
    def retry_after(self, key: str) -> int:
        with self._lock:
            return self._retry_after(key)
        
    def _retry_after(self, key: str) -> int:
        if (self._remaining(key) > 0):
            return 0
        
        curr_time = self._time()

        elapsed = curr_time % self._window_interval	
        
        return ceil(self._window_interval - elapsed)
    
    
    def _count_rolling_window(self, key: str) -> int:
        """counts the number of requests in the rolling window for the given key."""
        
        curr_window_id = self._curr_window_id()
        
        curr_window = self._window.get(key)
        prev_window = self._prev_window.get(key)
        
        curr_count = 0
        prev_count = 0
        
        if curr_window is not None and curr_window['id'] == curr_window_id:
            curr_count = curr_window['count']
            
        if prev_window is not None and prev_window['id'] == curr_window_id-1:
            prev_count = prev_window['count']
            
        if prev_count == 0:
            return curr_count
        
        curr_time = self._time()
        
        elapsed_curr_window = curr_time % self._window_interval
        diff_prev_window = self._window_interval - elapsed_curr_window
        
        prev_count_fraction = diff_prev_window / self._window_interval
        
        count = floor(curr_count + (prev_count_fraction * prev_count))
        
        return count
        
    
    def _tick(self, key: str) -> None:
        """ _tick resolves the current window and the previous window for the given key."""
        
        curr_window_id = self._curr_window_id()
        
        curr_window = self._window.get(key)
        
        if curr_window is None: # the key was never seen before (or ttl expired)
            self._window.set(key, {'count': 0, 'id': curr_window_id})
            return
        
        if curr_window['id'] < curr_window_id-1: # the current key window is way older
            curr_window['id'] = curr_window_id # reset the window
            curr_window['count'] = 0
            return
        
        if curr_window['id'] == curr_window_id-1: # the current key window is actually the previous window
            self._window.set(key, {'count': 0, 'id': curr_window_id})
            self._prev_window.set(key, curr_window)

        # the key window is the current window


    def _curr_window_id(self) -> int:
        return floor(self._time() / self._window_interval)