from abc import ABC, abstractmethod 


class KeyLimiter(ABC): 
  
    @abstractmethod
    def allow(self, key: str) -> bool:
        """
        tries to allow a call for the key, returns True if allowed, False if throttled
        """
        pass
    
    @abstractmethod
    def limit(self, key: str) -> int:
        """
        how many calls are allowed for the key per "time window"
        """
        pass
    
    @abstractmethod
    def remaining(self, key: str) -> int:
        """
        the number of calls left for the key before being throttled
        """
        pass
    
    @abstractmethod
    def retry_after(self, key: str) -> int: 
        """
        the number of seconds to wait until you can retry again without being throttled
        """
        pass