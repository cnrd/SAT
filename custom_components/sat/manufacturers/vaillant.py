from custom_components.sat.manufacturer import Manufacturer


class Vaillant(Manufacturer):
    @property
    def name(self) -> str:
        return 'Vaillant'
