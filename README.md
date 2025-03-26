# TIFF-NC 转换工具

本工具提供了将 NetCDF 文件与多波段 TIFF 文件相互转换的功能，适用于气象、地理等领域的数据处理。
**地理数据及必须包含latitude、longitude两个维度。**
## 安装
```bash
pip install tiff-nc
```

## 功能概述

1. **NetCDF 转 TIFF (`nc_to_tiffs`)**  
   将 NetCDF 文件转换为多波段 TIFF 文件，支持按时间维度切片并输出多个 TIFF 文件。

2. **TIFF 转 NetCDF (`tiffs_to_nc`)**  
   将多波段 TIFF 文件合并为一个 NetCDF 文件，支持按时间维度重新组织数据。

3. **计算函数 (`calculate_by_dimension`)**  
   对数据集进行计算，支持自定义函数。

4. **计算函数 (`calculate_by_time`)**  
   对数据集进行计算，支持自定义函数和时间粒度。
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
- `nodata` (int, 可选): 缺失值，默认为 `-9999`。
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
    nodata= -9999,
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

## 3、 `calculate_by_dimension`

沿指定维度对数据集进行计算，支持自定义函数。

### 参数
- `func` (Callable): 需包含`numpy.ndarray`参数的计算函数（支持numba加速）
- `ds` (xr.Dataset): 输入数据集
- `dim` (str|list[str]): 维度名称，默认为 `"valid_time"`
- `kwargs` (dict): 传递给`func`的额外参数
- `chunks` (dict): 分块配置（键为维度名，值为分块大小）
- `var_name` (str): 数据变量名，默认为 `"variable"`

### 示例
```python
# 计算时间维度的平均值
def mean_func(ndarray):
    return ndarray.mean(axis=0)

result = calculate_by_dimension(
    func=mean_func,
    ds=ds,
    dim="valid_time",
    var_name="precipitation"
)
```

### 注意
- 时间维度必须存在于输入数据集中
- func必须包含numpy.ndarray类型的参数
- 支持通过time_selection参数实现时间维度的聚合计算
- 分块配置中若维度不存在或分块大小超过维度长度将抛出异常



## 4. `calculate_by_time`

按时间维度对数据集进行计算，支持自定义时间粒度。

### 参数
- `func` (Callable): 需包含`numpy.ndarray`参数的计算函数（支持numba加速）
- `ds` (xr.Dataset): 输入数据集
- `time_dim` (str, 可选): 时间维度名称，默认为 `"valid_time"`
- `kwargs` (Mapping[str,Any] | None): 传递给`func`的额外参数，默认为`None`
- `chunks` (dict[str,int] | None): 分块配置（键为维度名，值为分块大小），默认为`None`
- `var_name` (str): 数据变量名，默认为 `"variable"`
- `time_selection` (Literal['YE', 'ME', 'QS-DEC', 'QS-JAN']): 时间粒度选择：
  - `YE`: 按年聚合
  - `ME`: 按月聚合
  - `QS-DEC`: 以12月为年末的季度
  - `QS-JAN`: 以1月为年末的季度，默认为`YE`

### 示例
```python
# 计算年度最大值
def max_func(ndarray):
    return ndarray.max(axis=0)

result = calculate_by_time(
    func=max_func,
    ds=ds,
    time_dim="valid_time",
    var_name="temperature",
    time_selection="YE"
)
```
### 注意
- 时间维度必须存在于输入数据集中
- func必须包含numpy.ndarray类型的参数
- 支持通过time_selection参数实现时间维度的聚合计算
- 分块配置中若维度不存在或分块大小超过维度长度将抛出异常