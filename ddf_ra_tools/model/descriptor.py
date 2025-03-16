from dataclasses import dataclass


@dataclass
class Descriptor:
    obj_name: str

    def __repr__(self):
        return str(self.__dict__)

    def __hash__(self):
        return hash((self.obj_name))

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return all(v == getattr(other, k) for k, v in vars(self).items())
        else:
            return all(
                v == getattr(other, k)
                for k, v in vars(self).items()
                if k in vars(other).keys()
            )
