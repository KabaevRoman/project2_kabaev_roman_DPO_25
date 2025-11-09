class InvalidTypeException(Exception):
    def __init__(self, *args) -> None:
        self.message = "invalid column type provided"
        super().__init__(*args)


class TableExistsException(Exception):
    def __init__(self, *args) -> None:
        self.message = "table already exists"
        super().__init__(*args)


class TableMissingException(Exception):
    def __init__(self, *args) -> None:
        self.message = "table does not exist"
        super().__init__(*args)
