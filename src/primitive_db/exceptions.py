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


class InvalidValueCountException(Exception):
    def __init__(self, *args) -> None:
        self.message = "invalid number of values provided"
        super().__init__(*args)


class InvalidValueTypeException(Exception):
    def __init__(self, column_name: str, expected_type: str, *args) -> None:
        self.message = f"invalid type for column '{column_name}': expected {expected_type}"
        super().__init__(*args)


class NoRecordsFoundException(Exception):
    def __init__(self, *args) -> None:
        self.message = "no records found matching the criteria"
        super().__init__(*args)
