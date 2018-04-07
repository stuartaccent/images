from .base import Operation


class FormatOperation(Operation):
    def construct(self, fmt):
        self.format = fmt

        if self.format not in ['jpeg', 'png', 'gif']:
            raise ValueError("Format must be either 'jpeg', 'png' or 'gif'")

    def run(self, willow, image, env):
        env['output-format'] = self.format
