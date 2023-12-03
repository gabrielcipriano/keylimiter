# pylimiter
popular rate limiter algorithms wrote in python

## token bucket

```python
""":param int bucket_size: maximum number of tokens in the bucket
   :param float refill_rate: token refill rate in seconds
"""
limiter = TokenBucketLimiter(bucket_size=3, refill_rate=1)

for _ in range(3):
    assert limiter.allow(SOME_IP) == True
    
assert limiter.allow(SOME_IP) == False
```

![token bucket](.readme/token-bucket.svg)

## sliding window counter 
![sliding window counter](.readme/sliding-window-counter.svg)
