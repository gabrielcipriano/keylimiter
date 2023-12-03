from keylimiter import TokenBucketLimiter

from time import sleep


SOME_IP = "127.0.0.1"
OTHER_IP = "192.168.1.1"


def test_allow_until_not_empty():
    limiter = TokenBucketLimiter(bucket_size=3, refill_rate=1)
    
    for _ in range(3):
        assert limiter.allow(SOME_IP) == True
        

def test_allow_until_throtle():
    limiter = TokenBucketLimiter(3, 1)
    
    for _ in range(3):
        assert limiter.allow(SOME_IP) == True
        
    assert limiter.allow(SOME_IP) == False
    
    
def test_keys_has_different_buckets():
    limiter = TokenBucketLimiter(3, 1)
    
    for _ in range(3):
        assert limiter.allow(SOME_IP) == True
        assert limiter.allow(OTHER_IP) == True
        
    assert limiter.allow(SOME_IP) == False
    assert limiter.allow(OTHER_IP) == False


def test_allow_after_refill():
    limiter = TokenBucketLimiter(5, 4)
    
    while limiter.allow(OTHER_IP) == True:
        pass
    
    assert limiter.allow(OTHER_IP) == False
        
    sleep(0.3)

    assert limiter.allow(OTHER_IP) == True


def test_token_bucket_limit():
    limiter = TokenBucketLimiter(5, 4)
    
    assert limiter.limit(SOME_IP) == 5
    

def test_token_bucket_remaining():
    limiter = TokenBucketLimiter(5, 1)
    
    assert limiter.remaining(SOME_IP) == 5
    
    limiter.allow(SOME_IP)
    
    assert limiter.remaining(SOME_IP) == 4
    
    while limiter.allow(SOME_IP) == True:
        pass
    
    assert limiter.remaining(SOME_IP) == 0
    

def test_token_bucket_retry_after():
    limiter = TokenBucketLimiter(5, 4)
    
    assert limiter.retry_after(SOME_IP) == 0
    
    while limiter.allow(SOME_IP) == True:
        pass
    
    assert limiter.retry_after(SOME_IP) == 1
    
    sleep(0.3)
    
    assert limiter.retry_after(SOME_IP) == 0
    
    
def test_token_bucket_retry_after_fraction_refill():
    limiter = TokenBucketLimiter(5, 1/3) # 1 token every 3 seconds
    
    while limiter.allow(SOME_IP) == True:
        pass
    
    assert limiter.retry_after(SOME_IP) == 3

    