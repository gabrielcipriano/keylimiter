from keylimiter import TokenBucketLimiter, KeyLimiter, SlidingWindowCounterLimiter
from fixtures.time import FakeTime
from random import randint, random

from threading import Thread

def run(limiter: KeyLimiter, time, iters):
    rand_normal_key = lambda: keys[randint(0, 99)]
    rand_orphan_key = lambda: str(random())
    
    
    # a small chance to generate an orphan key
    some_key = lambda: rand_normal_key() if random() < 0.9 else rand_orphan_key()
    
    
    for _ in range(iters):
        cmd = random()
        
        if cmd < 0.7:
            limiter.allow(some_key())
        elif cmd < 0.85:
            limiter.remaining(some_key())
        elif cmd < 0.95:
            limiter.retry_after(some_key())
        else:
            limiter.limit(some_key())
            
        if random() < 0.1:
            time.tick(random())

def span_threads_and_block(num_threads, target, limiter: KeyLimiter, time, iters):
    threads = []
    
    for _ in range(num_threads):
        threads.append(Thread(target=target, args=(limiter, time, iters)))
    
    for t in threads:
        t.start()

    for t in threads:
        t.join()
        
        
def race_conditions_token_bucket():
    time = FakeTime()
    
    limiter = TokenBucketLimiter(6, 3, time_func=time)
    
    span_threads_and_block(5, run, limiter, time, 10000)

        
        
def race_conditions_sliding_window():
    time = FakeTime()
    
    limiter = SlidingWindowCounterLimiter(10, "second", time_func=time)
    
    span_threads_and_block(5, run, limiter, time, 10000)


if __name__ == '__main__':
    import timeit
    
    keys = []
    
    for i in range(100):
        keys.append(str(i))
        
    ITERATIONS = 200
        
    functions_to_measure = [
        "race_conditions_token_bucket()",  # time:  234.91510925701004
        "race_conditions_sliding_window()" # time:  247.48728842198034
    ]
    
    for function in functions_to_measure:
        print(function)
        print("time: ", timeit.timeit(function, globals=locals(), number=ITERATIONS))
        print()
