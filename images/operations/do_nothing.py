from .base import Operation


class DoNothingOperation(Operation):
    def construct(self):
        pass

    def run(self, willow, image, env):
        pass
