class ValueObject[Value_T]:
    def __init__(self, value: Value_T) -> None:
        self._value = value

    @property
    def value(self) -> Value_T:
        return self._value
