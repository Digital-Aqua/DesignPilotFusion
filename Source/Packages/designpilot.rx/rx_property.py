_dep_ctx_stack: list[set[RxEvent]] = []


class ReactivePropertyBase(
    GetterMixin[TClass, TValue], # GetterMixin first
    Generic[TClass, TValue]
):
    """
    A base class for reactive properties.
    """

    def __init__(self, value: TValue):
        self.value = value

    def get(self) -> TValue:
        return self.value

    def set(self, value: TValue):
        self.value = value

    def __str__(self):
        return f"{self.__class__.__name__}(value={self.value})"

    def __repr__(self):
        return f"{self.__class__.__name__}(value={self.value})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ReactivePropertyBase):
            return self.value == other.value
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.value)

    def __iter__(self):
        return iter([self.value])

    def __next__(self):
        return next(iter(self))

    def __contains__(self, item: TValue) -> bool:
        return item == self.value

    def __len__(self):
        return 1

    def __getitem__(self, index: int) -> TValue:
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        return self.value

    def __setitem__(self, index: int, value: TValue):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = value

    def __delitem__(self, index: int):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = None

    def __iter__(self):
        return iter([self.value])

    def __next__(self):
        return next(iter(self))

    def __contains__(self, item: TValue) -> bool:
        return item == self.value

    def __len__(self):
        return 1

    def __getitem__(self, index: int) -> TValue:
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        return self.value

    def __setitem__(self, index: int, value: TValue):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = value

    def __delitem__(self, index: int):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = None

    def __iter__(self):
        return iter([self.value])

    def __next__(self):
        return next(iter(self))

    def __contains__(self, item: TValue) -> bool:
        return item == self.value

    def __len__(self):
        return 1

    def __getitem__(self, index: int) -> TValue:
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        return self.value

    def __setitem__(self, index: int, value: TValue):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = value

    def __delitem__(self, index: int):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = None

    def __iter__(self):
        return iter([self.value])

    def __next__(self):
        return next(iter(self))

    def __contains__(self, item: TValue) -> bool:
        return item == self.value

    def __len__(self):
        return 1

    def __getitem__(self, index: int) -> TValue:
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        return self.value

    def __setitem__(self, index: int, value: TValue):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = value

    def __delitem__(self, index: int):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = None

    def __iter__(self):
        return iter([self.value])

    def __next__(self):
        return next(iter(self))

    def __contains__(self, item: TValue) -> bool:
        return item == self.value

    def __len__(self):
        return 1

    def __getitem__(self, index: int) -> TValue:
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        return self.value

    def __setitem__(self, index: int, value: TValue):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = value

    def __delitem__(self, index: int):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = None

    def __iter__(self):
        return iter([self.value])

    def __next__(self):
        return next(iter(self))

    def __contains__(self, item: TValue) -> bool:
        return item == self.value

    def __len__(self):
        return 1

    def __getitem__(self, index: int) -> TValue:
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        return self.value

    def __setitem__(self, index: int, value: TValue):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = value

    def __delitem__(self, index: int):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = None

    def __iter__(self):
        return iter([self.value])

    def __next__(self):
        return next(iter(self))

    def __contains__(self, item: TValue) -> bool:
        return item == self.value

    def __len__(self):
        return 1

    def __getitem__(self, index: int) -> TValue:
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        return self.value

    def __setitem__(self, index: int, value: TValue):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = value

    def __delitem__(self, index: int):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = None

    def __iter__(self):
        return iter([self.value])

    def __next__(self):
        return next(iter(self))

    def __contains__(self, item: TValue) -> bool:
        return item == self.value

    def __len__(self):
        return 1

    def __getitem__(self, index: int) -> TValue:
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        return self.value

    def __setitem__(self, index: int, value: TValue):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = value

    def __delitem__(self, index: int):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = None

    def __iter__(self):
        return iter([self.value])

    def __next__(self):
        return next(iter(self))

    def __contains__(self, item: TValue) -> bool:
        return item == self.value

    def __len__(self):
        return 1

    def __getitem__(self, index: int) -> TValue:
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        return self.value

    def __setitem__(self, index: int, value: TValue):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = value

    def __delitem__(self, index: int):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = None

    def __iter__(self):
        return iter([self.value])

    def __next__(self):
        return next(iter(self))

    def __contains__(self, item: TValue) -> bool:
        return item == self.value

    def __len__(self):
        return 1

    def __getitem__(self, index: int) -> TValue:
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        return self.value

    def __setitem__(self, index: int, value: TValue):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = value

    def __delitem__(self, index: int):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = None

    def __iter__(self):
        return iter([self.value])

    def __next__(self):
        return next(iter(self))

    def __contains__(self, item: TValue) -> bool:
        return item == self.value

    def __len__(self):
        return 1

    def __getitem__(self, index: int) -> TValue:
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        return self.value

    def __setitem__(self, index: int, value: TValue):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = value

    def __delitem__(self, index: int):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = None

    def __iter__(self):
        return iter([self.value])

    def __next__(self):
        return next(iter(self))

    def __contains__(self, item: TValue) -> bool:
        return item == self.value

    def __len__(self):
        return 1

    def __getitem__(self, index: int) -> TValue:
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        return self.value

    def __setitem__(self, index: int, value: TValue):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = value

    def __delitem__(self, index: int):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = None

    def __iter__(self):
        return iter([self.value])

    def __next__(self):
        return next(iter(self))

    def __contains__(self, item: TValue) -> bool:
        return item == self.value

    def __len__(self):
        return 1

    def __getitem__(self, index: int) -> TValue:
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        return self.value

    def __setitem__(self, index: int, value: TValue):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = value

    def __delitem__(self, index: int):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = None

    def __iter__(self):
        return iter([self.value])

    def __next__(self):
        return next(iter(self))

    def __contains__(self, item: TValue) -> bool:
        return item == self.value

    def __len__(self):
        return 1

    def __getitem__(self, index: int) -> TValue:
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        return self.value

    def __setitem__(self, index: int, value: TValue):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = value

    def __delitem__(self, index: int):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = None

    def __iter__(self):
        return iter([self.value])

    def __next__(self):
        return next(iter(self))

    def __contains__(self, item: TValue) -> bool:
        return item == self.value

    def __len__(self):
        return 1

    def __getitem__(self, index: int) -> TValue:
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        return self.value

    def __setitem__(self, index: int, value: TValue):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = value

    def __delitem__(self, index: int):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = None

    def __iter__(self):
        return iter([self.value])

    def __next__(self):
        return next(iter(self))

    def __contains__(self, item: TValue) -> bool:
        return item == self.value

    def __len__(self):
        return 1

    def __getitem__(self, index: int) -> TValue:
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        return self.value

    def __setitem__(self, index: int, value: TValue):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = value

    def __delitem__(self, index: int):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = None

    def __iter__(self):
        return iter([self.value])

    def __next__(self):
        return next(iter(self))

    def __contains__(self, item: TValue) -> bool:
        return item == self.value

    def __len__(self):
        return 1

    def __getitem__(self, index: int) -> TValue:
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        return self.value

    def __setitem__(self, index: int, value: TValue):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = value

    def __delitem__(self, index: int):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = None

    def __iter__(self):
        return iter([self.value])

    def __next__(self):
        return next(iter(self))

    def __contains__(self, item: TValue) -> bool:
        return item == self.value

    def __len__(self):
        return 1

    def __getitem__(self, index: int) -> TValue:
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        return self.value

    def __setitem__(self, index: int, value: TValue):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = value

    def __delitem__(self, index: int):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = None

    def __iter__(self):
        return iter([self.value])

    def __next__(self):
        return next(iter(self))

    def __contains__(self, item: TValue) -> bool:
        return item == self.value

    def __len__(self):
        return 1

    def __getitem__(self, index: int) -> TValue:
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        return self.value

    def __setitem__(self, index: int, value: TValue):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = value

    def __delitem__(self, index: int):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = None

    def __iter__(self):
        return iter([self.value])

    def __next__(self):
        return next(iter(self))

    def __contains__(self, item: TValue) -> bool:
        return item == self.value

    def __len__(self):
        return 1

    def __getitem__(self, index: int) -> TValue:
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        return self.value

    def __setitem__(self, index: int, value: TValue):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = value

    def __delitem__(self, index: int):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = None

    def __iter__(self):
        return iter([self.value])

    def __next__(self):
        return next(iter(self))

    def __contains__(self, item: TValue) -> bool:
        return item == self.value

    def __len__(self):
        return 1

    def __getitem__(self, index: int) -> TValue:
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        return self.value

    def __setitem__(self, index: int, value: TValue):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = value

    def __delitem__(self, index: int):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = None

    def __iter__(self):
        return iter([self.value])

    def __next__(self):
        return next(iter(self))

    def __contains__(self, item: TValue) -> bool:
        return item == self.value

    def __len__(self):
        return 1

    def __getitem__(self, index: int) -> TValue:
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        return self.value

    def __setitem__(self, index: int, value: TValue):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = value

    def __delitem__(self, index: int):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = None

    def __iter__(self):
        return iter([self.value])

    def __next__(self):
        return next(iter(self))

    def __contains__(self, item: TValue) -> bool:
        return item == self.value

    def __len__(self):
        return 1

    def __getitem__(self, index: int) -> TValue:
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        return self.value

    def __setitem__(self, index: int, value: TValue):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = value

    def __delitem__(self, index: int):
        if index != 0:
            raise IndexError("ReactivePropertyBase is a single-element container")
        self.value = None

    def __iter__(self):
        return iter([self.value])

 