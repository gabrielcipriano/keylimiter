import pytest

class FakeTime:
    def __init__(self):
        self.time = 0
        
    def __call__(self):
        return self.time
    
    def tick(self, seconds):
        self.time += seconds
        
@pytest.fixture
def time():
    return FakeTime()