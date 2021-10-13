class DocumentNotParsed(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class MissingSieve(Exception):
    def __init__(self, msg):
        super().__init__(msg)
