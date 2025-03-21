from .translate_data import nc_to_tiffs, tiffs_to_nc
from .calculate import calculate_by_dimension,calculate_by_time

__all__ = ["nc_to_tiffs", "tiffs_to_nc","calculate_by_dimension","calculate_by_time"]
def main() -> None:
    print("Hello from tiff-nc!")
