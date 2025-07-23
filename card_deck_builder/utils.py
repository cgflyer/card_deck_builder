import threading

class IndentedLogger:
    _indent_level = threading.local()

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        if not hasattr(self._indent_level, "value"):
            self._indent_level.value = 0

    class LogBlock:
        def __init__(self, outer, method_name, **params):
            self.outer = outer
            self.method_name = method_name
            self.params = params

        def __enter__(self):
            indent = '    ' * self.outer._indent_level.value
            param_str = ', '.join(f"{k}={v!r}" for k, v in self.params.items())
            self.outer.logger.info(f"{indent}↳ Entering {self.method_name}({param_str})")
            self.outer._indent_level.value += 1
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.outer._indent_level.value -= 1
            indent = '    ' * self.outer._indent_level.value
            self.outer.logger.info(f"{indent}↲ Exiting {self.method_name}")

    def log_block(self, method_name: str, **params):
        return self.LogBlock(self, method_name, **params)

    def info(self, message: str):
        indent = '    ' * self._indent_level.value
        self.logger.info(f"{indent}{message}")

