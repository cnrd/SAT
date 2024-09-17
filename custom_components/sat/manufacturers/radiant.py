from custom_components.sat.manufacturer import Manufacturer


class Radiant(Manufacturer):
    @property
    def name(self) -> str:
        return 'Radiant'
