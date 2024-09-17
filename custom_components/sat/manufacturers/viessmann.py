from custom_components.sat.manufacturer import Manufacturer


class Viessmann(Manufacturer):
    @property
    def name(self) -> str:
        return 'Viessmann'
