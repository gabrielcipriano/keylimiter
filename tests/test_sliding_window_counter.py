from keylimiter import SlidingWindowCounterLimiter

SOME_IP = "127.0.0.1"
OTHER_IP = "192.168.1.1"


def test_allow_until_not_empty():
    limiter = SlidingWindowCounterLimiter(max_requests=3, window_unit="second")
    
    for _ in range(3):
        assert limiter.allow(SOME_IP) == True
        

def test_allow_until_throtle():
    limiter = SlidingWindowCounterLimiter(max_requests=3, window_unit="second")
    
    for _ in range(3):
        assert limiter.allow(SOME_IP) == True
        
    assert limiter.allow(SOME_IP) == False
    
    
def test_keys_has_different_buckets():
    limiter = SlidingWindowCounterLimiter(3, 'second')
    
    for _ in range(3):
        assert limiter.allow(SOME_IP) == True
        assert limiter.allow(OTHER_IP) == True
        
    assert limiter.allow(SOME_IP) == False
    assert limiter.allow(OTHER_IP) == False


def test_allow_as_window_moves(time):
    limiter = SlidingWindowCounterLimiter(10, 'second', time_func=time)

    while limiter.allow(SOME_IP) == True:
        pass
    
    time.tick(1.1)

    assert limiter.allow(SOME_IP) == True
    assert limiter.allow(SOME_IP) == False
    
    time.tick(0.1)
    
    assert limiter.allow(SOME_IP) == True


def test_sliding_window_limit():
    limiter = SlidingWindowCounterLimiter(5, 'second')
    
    assert limiter.limit(SOME_IP) == 5
    

def test_sliding_window_remaining(time):
    limiter = SlidingWindowCounterLimiter(5, 'second', time_func=time)
    
    assert limiter.remaining(SOME_IP) == 5
    
    limiter.allow(SOME_IP)
    
    assert limiter.remaining(SOME_IP) == 4
    
    for _ in range(4):
        limiter.allow(SOME_IP)
    
    assert limiter.remaining(SOME_IP) == 0
    assert limiter.allow(SOME_IP) == False
    
    time.tick(1.2)
    
    assert limiter.remaining(SOME_IP) == 1
    assert limiter.allow(SOME_IP) == True
    
    

def test_sliding_window_retry_after():
    limiter = SlidingWindowCounterLimiter(5, 'second')

    assert limiter.retry_after(SOME_IP) == 0
    
    for _ in range(5):
        limiter.allow(SOME_IP)
    
    assert limiter.retry_after(SOME_IP) == 1
    

def test_token_bucket_retry_after_minute(time):
    limiter = SlidingWindowCounterLimiter(5, 'minute', time_func=time)
    
    for _ in range(5):
        limiter.allow(SOME_IP)
        
    assert limiter.retry_after(SOME_IP) == 60
    
    time.tick(45)
    
    assert limiter.retry_after(SOME_IP) == 15

    