import xarray as xr
import os
import glob
import pyogrio as pyo
import pandas as pd
import numpy as np
import rioxarray as rxr
from dask.diagnostics.progress import ProgressBar
from typing import Optional,Literal

def nc_to_tiffs(
    nc_file:str,
    tiffs_dir:str,
    chunks:int|dict=512,
    var_name:str|list[str]="variable",
    time_dim="valid_time",
    shapefile:str|None=None,
    crs:str="EPSG:4326",
    time_format:Literal['%Y%m%d','%Y%m','%Y']="%Y%m%d",
    workers:int=4,
    ) -> None:
    """
    将nc文件转为多波段tiff文件

    Args:
        nc_file (str): netcdf文件路径
        tiffs_dir (str): TIFF影像保存路径
        chunks (int | dict, optional): 分块大小. Defaults to 512.
        var_name (str | list[str]): 变量名或变量名列表，每个变量对应一个波段. Defaults to "variable".
        time_dim (str, optional): 时间维度名称. Defaults to "valid_time".
        shapefile (str | None, optional): 边界文件路径. Defaults to None.
        crs (str, optional): 坐标参考系统. Defaults to "EPSG:4326".
        time_format (str, optional): 时间格式. Defaults to "%Y%m%d".
        workers (int, optional): 进程数. Defaults to 4.
    """
    # 确保变量名是列表格式
    if isinstance(var_name, str):
        var_names = [var_name]
    else:
        var_names = var_name
    print(var_names)
    out_dir = os.path.join(tiffs_dir, os.path.splitext(os.path.basename(nc_file))[0])
    os.makedirs(out_dir, exist_ok=True)
    
    with xr.open_dataset(nc_file, chunks=chunks, engine="h5netcdf") as ds:
        ds = ds.rio.write_crs(crs)
        
        if shapefile is not None:
            gdf = pyo.read_dataframe(shapefile)
            gdf = gdf.to_crs(crs)
            geometry = gdf.geometry.unary_union
            ds = ds.rio.clip([geometry], drop=True)
            
        py_datetimes = pd.to_datetime(ds[time_dim].values)
        
        with ProgressBar():
            for idx_time, time in enumerate(py_datetimes):
                # 创建空数据集用于存储多波段数据
                datas = {}
                # 遍历所有变量并添加到数据集
                for var in var_names:
                    data = ds[var].isel({time_dim: idx_time}).compute(num_workers=workers)
                    datas[var] = data
                stacked = xr.Dataset(datas)
                # 设置空间参考信息
                stacked.rio.write_crs(crs, inplace=True)
                
                # 输出多波段TIFF
                output_path = f"{out_dir}/{time.strftime(time_format)}.tif"
                stacked.rio.to_raster(
                    output_path,
                    dtype="float32",
                    nodata=np.nan,
                    compress="LZW",
                    tags={"TIFFTAG_DATETIME": time.strftime(time_format)}
                )


def tiffs_to_nc(
    tiffs_dir:str,
    nc_file:str,
    var_name:str|list[str],
    time_dim:str="valid_time",
    chunks:Optional[dict[str, int]] = None,
    time_format:Literal['%Y%m%d','%Y%m','%Y']="%Y%m%d",
    workers:int=4,
    attrs:dict[str, str]={},
    vars_attrs:dict[str, dict[str, str]]={},
    ) -> None:
    """
    将多波段tiff文件转为nc文件

    Args:
        tiffs_dir (str): TIFF影像保存路径
        nc_file (str): netcdf输出路径
        var_name (str | list[str]): 变量名称或变量名列表，每个变量对应一个波段.
        time_dim (str, optional): 时间维度名称. Defaults to "valid_time".
        chunks (Optional[dict[str, int]], optional): 分块大小. Defaults to None.
        time_format (str, optional): 时间格式. Defaults to "%Y%m%d".
        workers (int, optional): 工作进程数. Defaults to 4.
        attrs (dict[str, str], optional): 全局属性. Defaults to {}.
        vars_attrs (dict[str, dict[str, str]], optional): 变量属性. Defaults to {}.

    Raises:
        ValueError: 文件名称为时间字符串格式与Time_format不匹配。
    """
    files = glob.glob(f"{tiffs_dir}/*.tif")
    xds_sets:list[xr.Dataset] = []
    if isinstance(var_name, str):
        var_names = [var_name]
    else:
        var_names = var_name
    for file in files:
        date_str = os.path.basename(file).split('.')[0]
        try:
            date = pd.to_datetime(date_str,format=time_format)
            del date_str
        except ValueError:
            raise ValueError(f"无法解析日期字符串：{date_str}")
        xds = rxr.open_rasterio(file, chunks={
            "x": chunks["longitude"],
            "y": chunks["latitude"],
        })
        xds = xds.assign_coords({time_dim: date})
        del date
        lds = xds.to_dataset(dim="band")
        del xds
        varses = {}
        for var in lds.data_vars:
            varses.update({var:var_names[int(var)-1]})
        lds = lds.rename(varses)
        del varses
        xds_sets.append(lds)
        del lds
    ds = xr.concat(xds_sets, dim=time_dim)
    ds = ds.rename({'y':'latitude', 'x':'longitude'})
    # 添加全局属性
    ds.attrs.update(attrs)
    encoding = {
        **{
            var: {
                "zlib": True,
                "complevel": 4,
                "dtype": "float32",
                "_FillValue": np.nan,
                "chunksizes":(
                                chunks[time_dim] if chunks[time_dim] > 0 else 1,
                                chunks['latitude'] if chunks['latitude'] > 0 else 1,
                                chunks['longitude'] if chunks['longitude'] > 0 else 1),
                **vars_attrs.get(var, {})# 添加变量属性
            }for var in ds.data_vars
        },
        "latitude": {"dtype": "float32"},
        "longitude": {"dtype": "float32"},
        time_dim: {"dtype": "float64"},
    }
    delayed = ds.to_netcdf(nc_file, engine="h5netcdf", compute=False, encoding=encoding)
    
    with ProgressBar():
        delayed.compute(num_workers=workers)