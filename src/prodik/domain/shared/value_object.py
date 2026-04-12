class ValueObject[Value_T]:
    def __init__(self, value: Value_T) -> None:
        self._value = value

    def __eq__(self, value: object) -> bool:
        return value == self.value

    def __hash__(self) -> int:
        return hash(self.value)

    @property
    def value(self) -> Value_T:
        return self._value
