# keylimiter - A Thread-safe rate limiter for Python

[![PyPI version](https://badge.fury.io/py/keylimiter.svg)](https://badge.fury.io/py/keylimiter)
[![License: MIT](https://img.shields.io/badge/Multi_thread-safe-green.svg)](https://github.com/gabrielcipriano/keylimiter/blob/main/tests/bench_perf.py)
[![License: MIT](https://img.shields.io/badge/License-GNU_3-yellow.svg)](https://opensource.org/license/gpl-3-0/)

Two of the most popular rate limiter algorithms: token bucket and sliding window counter.


it's "key"limiter to enphasize that it's a key based rate limiter, not a ip based rate limiter, so the key can be anything, like an ip, an user id, an url, etc.

Some use cases:
- limit the number of requests per ip
- limit likes per user in a post
- limit the number of notifications per user

## token bucket

```python
SOME_IP = "111.222.1.1"

"""
:param int bucket_size: maximum number of tokens in the bucket
:param float refill_rate: token refill rate in seconds
:param Callable[[], float] time_func: function that returns the current time in seconds. Default: monotonic
"""
limiter = TokenBucketLimiter(bucket_size=3, refill_rate=1)

for _ in range(3):
    assert limiter.allow(SOME_IP) == True
    
assert limiter.allow(SOME_IP) == False
```

![token bucket](https://raw.githubusercontent.com/gabrielcipriano/keylimiter/main/.readme/token-bucket.svg)

## sliding window counter 

```python
SOME_IP = "111.222.1.1"

"""
:param int max_requests: maximum number of requests in a window
:param str window_unit: "second" | "minute" | "hour". Default: "minute"
:param Callable[[], float] time_func: function that returns the current time in seconds. Default: monotonic
"""
limiter = SlidingWindowCounterLimiter(max_requests=3, window_unit="second")

for _ in range(3):
    assert limiter.allow(SOME_IP) == True
    
assert limiter.allow(SOME_IP) == False
```

![sliding window counter](https://raw.githubusercontent.com/gabrielcipriano/keylimiter/main/.readme/sliding-window-counter.svg)
