import inspect

from images.exceptions import InvalidFilterSpecError


class Operation:
    def __init__(self, method, *args):
        self.method = method
        self.args = args

        # Check arguments
        try:
            inspect.getcallargs(self.construct, *args)
        except TypeError as e:
            raise InvalidFilterSpecError(e)

        # Call construct
        try:
            self.construct(*args)
        except ValueError as e:
            raise InvalidFilterSpecError(e)

    def construct(self, *args):
        raise NotImplementedError

    def run(self, willow, image, env):
        raise NotImplementedError
