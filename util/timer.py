class fucked_up_timer:
    def __init__(self):
        import time
        self.epoch_seconds = int(time.time())
    def get(self):
        self.epoch_seconds += 1
        return self.epoch_seconds