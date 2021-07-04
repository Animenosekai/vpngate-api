class VPNGateException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class RequestError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ParseError(VPNGateException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)