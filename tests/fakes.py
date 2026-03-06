class FakeLLM:
    def __init__(self, reply="(fake) hello", fail=False, timeout=False):
        self.reply = reply
        self.fail = fail
        self.timeout = timeout
        self.calls = [] # track inputs for assertions

    def generate(self, user_input: str) -> str:
        self.calls.append(user_input)
        if self.timeout:
            raise TimeoutError("Fake timeout")
        if self.fail:
            raise Exception("Fake failure")
        return self.reply