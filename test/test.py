from numba import jit
import numpy as np
# import xarray as xr
from  tiff_nc import tiffs_to_nc
# from tiff_nc import calculate_by_time
# from dask.diagnostics.progress import ProgressBar

@jit(nopython=True)
def max(arr :np.ndarray):
    if np.isnan(arr).any():
        return np.nan
    result = arr[0]
    for value in arr:
        if value > result:
            result = value
    return result
if __name__ == "__main__":
    chunks={
        "valid_time": -1,
        "latitude": 1024,
        "longitude": 1024
    }
    # with xr.open_dataset("test/data/2003.nc",chunks=chunks,engine="h5netcdf") as ds:
    #     with ProgressBar():
    #         txx = calculate_by_time(
    #         func=max,
    #         ds=ds,
    #         var_name="t2m",
    #         time_dim="valid_time",
    #         chunks=chunks,
    #         time_selection="QS-JAN",
    #         ).compute(num_workers=4)
    #     encoding = {
    #         "t2m": {
    #             'zlib': True,
    #             'complevel': 4,  # 平衡速度与压缩率
    #             'chunksizes': (1, 71, 122),
    #             'shuffle': True,
    #         },
    #         'latitude': {'dtype': 'float32'},
    #         'longitude': {'dtype': 'float32'},
    #         'valid_time': {'dtype': 'float64'}
    #     }
    #     txx.to_netcdf("test/output/txx-season.nc",mode="w",engine="h5netcdf",encoding=encoding)
    # nc_to_tiffs(
    #     nc_file="test/output/200301.nc",
    #     tiffs_dir="test/output",
    #     chunks=chunks,
    #     var_name="t2m",
    #     time_dim="valid_time",
    # )
    tiffs_to_nc(
        tiffs_dir="test/data/200301",
        nc_file="test/output/200301.nc",
        var_name="t2m",
        time_dim="valid_time",
        chunks=chunks,
        workers=4,
        attrs={
            "title": "2003quarterly",
            "description": "2003quarterly",
            "source": "2003quarterly",
            "references":"2003quarterly",
        }
    )
    