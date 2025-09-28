pyrtlsweeper_logging = False


def set_logging(logging: bool):
    global pyrtlsweeper_logging
    pyrtlsweeper_logging = logging


def _log(msg: str):
    if pyrtlsweeper_logging:
        print(f"[pyrtlsweeper] {msg}")

def _error(msg: str):
    raise Exception(f"[pyrtlsweeper] error: {msg}")
