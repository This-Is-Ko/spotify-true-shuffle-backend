class MockAsyncResult:
    def __init__(self, id):
        self.id = id

    @property
    def status(self):
        return "SUCCESS"

    @property
    def result(self):
        return "Shuffled playlist"
