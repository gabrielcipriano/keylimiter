from . import KeyLimiter
from .keyvalue_store import InMemoryTtlStore, NamespacedKVStore

from time import monotonic
from math import ceil, floor

from threading import Lock

from typing import Callable

class TokenBucketLimiter(KeyLimiter):
    bucket_size: int
    refill_rate: float
    buckets: NamespacedKVStore[tuple[int,int]] # key -> (tokens, last_seen)
    _time:  Callable[[], float] 
    
    
    def __init__(self, bucket_size: int, refill_rate: float, time_func=monotonic):
        """
        :param int bucket_size: maximum number of tokens in the bucket
        :param float refill_rate: token refill rate in seconds
        :param Callable[[], float] time_func: function that returns the current time in seconds. Default: monotonic
        """
        assert bucket_size > 0
        assert refill_rate >= 0
        assert time_func is not None
        
        self._time = time_func
        
        self.bucket_size = bucket_size
        self.refill_rate = refill_rate
        
        max_refill_time = ceil(bucket_size / refill_rate) 
        
        self._lock = Lock()
        
        ttl_kvstore = InMemoryTtlStore(max_refill_time, time_func)

        self.buckets = NamespacedKVStore[tuple[int,int]]("bucket", ttl_kvstore)
    
    def allow(self, key: str) -> bool:
        with self._lock:
            return self._allow(key)
            
    def _allow(self, key: str) -> bool:
        tokens = self._remaining(key)
        if tokens > 0:
            self._set_tokens(key, tokens - 1)
            return True
        return False
    
    def limit(self, _: str) -> int:
        return self.bucket_size
    
    def remaining(self, key: str) -> int:
        with self._lock:
            return self._remaining(key)
        
    def _remaining(self, key: str) -> int:
        self._refill(key)
        tokens, _ = self.buckets.get(key)
        return tokens
    
    def retry_after(self, key: str) -> int:
        with self._lock:
            return self._retry_after(key)
            
    def _retry_after(self, key: str) -> int:
            tokens = self._remaining(key)
            if tokens > 0:
                return 0
            return ceil(1 / self.refill_rate)
    
    def _refill(self, key: str) -> None:
        bucket = self.buckets.get(key)
        if bucket is None:
            self._fill(key)
            return
        
        tokens, last_seen = self.buckets.get(key)
        
        new_tokens = floor((self._time() - last_seen) * self.refill_rate)
        
        if new_tokens <= 0:
            return
        
        tokens = min(tokens + new_tokens, self.bucket_size) # sink overflow
        
        self._set_tokens(key, tokens) # has race conditions in multi-threaded environments
    
    def _fill(self, key: str) -> None:
        self._set_tokens(key, self.bucket_size)
        
    def _set_tokens(self, key: str, tokens: int) -> None:
        self.buckets.set(key, (tokens, self._time(),))
    