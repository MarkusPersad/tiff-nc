# TIFF-NC 转换工具

本工具提供了将 NetCDF 文件与多波段 TIFF 文件相互转换的功能，适用于气象、地理等领域的数据处理。
## 安装
```bash
pip install tiff-nc
```

## 功能概述

1. **NetCDF 转 TIFF (`nc_to_tiffs`)**  
   将 NetCDF 文件转换为多波段 TIFF 文件，支持按时间维度切片并输出多个 TIFF 文件。

2. **TIFF 转 NetCDF (`tiffs_to_nc`)**  
   将多波段 TIFF 文件合并为一个 NetCDF 文件，支持按时间维度重新组织数据。

---

## 函数说明

### 1. `nc_to_tiffs`

将 NetCDF 文件转换为多波段 TIFF 文件。

#### 参数
- `nc_file` (str): 输入的 NetCDF 文件路径。
- `tiffs_dir` (str): 输出 TIFF 文件的保存目录。
- `chunks` (int | dict, 可选): 分块大小，默认为 `512`。
- `var_name` (str | list[str]): 变量名或变量名列表，每个变量对应一个波段，默认为 `"variable"`。
- `time_dim` (str, 可选): 时间维度名称，默认为 `"valid_time"`。
- `shapefile` (str | None, 可选): 边界文件路径，默认为 `None`。
- `crs` (str, 可选): 坐标参考系统，默认为 `"EPSG:4326"`。
- `time_format` (str, 可选): 时间格式，默认为 `"%Y%m%d"`。
- `workers` (int, 可选): 进程数，默认为 `4`。

#### 示例
```python
nc_to_tiffs(
    nc_file="input.nc",
    tiffs_dir="output_dir",
    chunks={"valid_time": -1, "latitude": 512, "longitude": 512},
    var_name=["variable1", "variable2"],
    time_dim="valid_time",
    shapefile="boundary.shp",
    crs="EPSG:4326",
)
```

#### 注意
- 该函数将输入的 NetCDF 文件转换为多波段 TIFF 文件，并支持按时间维度进行切片和输出多个 TIFF 文件。
- 该函数支持按时间维度进行切片和输出多个 TIFF 文件，并支持边界裁剪和坐标转换。
- 该函数支持边界裁剪和坐标转换，以适应不同场景的需求。
- 该函数支持多进程并行处理，以加速处理速度。
- chunks dict 的键值对表示每个维度的名称和分块大小。eg: `{"valid_time": -1, "latitude": 512, "longitude": 512}` 
   如果不指定分块大小，则设置为 `-1`，表示该维度不进行分块。

### 2. `tiffs_to_nc`

将多波段 TIFF 文件合并为一个 NetCDF 文件。

#### 参数
- `tiffs_dir` (str): 输入 TIFF 文件的目录路径。
- `nc_file` (str): 输出的 NetCDF 文件路径。
- `var_name` (str | list[str]): 变量名或变量名列表，每个变量对应一个波段。
- `time_dim` (str, 可选): 时间维度名称，默认为 `"valid_time"`。
- `chunks` (dict, 可选): 分块大小，默认为 `None`。
- `time_format` (str, 可选): 时间格式，默认为 `"%Y%m%d"`。
- `workers` (int, 可选): 工作进程数，默认为 `4`。
- `attrs` (dict[str, str], 可选): 全局属性，默认为 `{}`。
- `vars_attrs` (dict[str, dict[str, str]], 可选): 变量属性，默认为 `{}`。例如：`{"variable1": {"units": "m", "long_name": "Height"}, "variable2": {"units": "K", "long_name": "Temperature"}}`。

#### 示例
```python
tiffs_to_nc(
    tiffs_dir="input_dir",
    nc_file="output.nc",
    var_name=["variable1", "variable2"],
    time_dim="valid_time",
    chunks={"valid_time": -1, "latitude": 512, "longitude": 512},
    time_format="%Y%m%d",
    workers=4,
    attrs={"title": "Example Dataset", "institution": "Example Institution"},
    vars_attrs={
        "variable1": {"units": "m", "long_name": "Height"},
        "variable2": {"units": "K", "long_name": "Temperature"}
    }
)
```
#### 注意
- 该函数将输入的多波段 TIFF 文件合并为一个 NetCDF 文件，并支持按时间维度进行重新组织数据。
- 该函数支持按时间维度进行重新组织数据，并支持多进程并行处理，以加速处理速度。
- chunks dict 的键值对表示每个维度的名称和分块大小。eg: `{"valid_time": -1, "latitude": 512, "longitude": 512}` 
  如果不指定分块大小，则设置为 `-1`，表示该维度不进行分块。