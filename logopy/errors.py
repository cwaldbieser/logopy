import attr


class LogoError(Exception):
    pass


class ExpectedEndError(LogoError):
    pass


class StopSignal(Exception):
    pass


@attr.s
class OutputSignal(Exception):
    value = attr.ib()


class HaltSignal(Exception):
    pass
