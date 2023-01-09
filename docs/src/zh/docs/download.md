



## 总体上


[数据集摘要信息](https://doi.org/10.6084/m9.figshare.c.6214666)

[在线搜索及下载](http://database.deepsolar.space:18080/dbs/nlfff)


## 原始数据

我们使用 [drms](https://github.com/mbobra/SHARPs) 从 [JSOC](http://jsoc.stanford.edu) 下载 [sharp cea](http://jsoc.stanford.edu/doc/data/hmi/sharp/sharp.htm) 文件 (包括Bp.fits, Bt.fits, Br.fits) 作为原始文件  [raw-202203](https://figshare.com/articles/dataset/NLFFF_Dataset_Information/21760598?backTo=/collections/Archive_Information_of_Three-Dimensional_Solar_Magnetic_Fields_Dataset/6214666) , 可以从[这篇文章](https://todo.com) 找到详细的筛选规则。


## NLFFF文件

产品文件存储在这个文件夹 [archive-202203](https://figshare.com/articles/dataset/NLFFF_Dataset_Information/21760598?backTo=/collections/Archive_Information_of_Three-Dimensional_Solar_Magnetic_Fields_Dataset/6214666) , 样本存储路径可以从数据库里面获得，每个样本通常包括下表这些文件。


**你也可以 [在这里在线搜索下载](http://database.deepsolar.space:18080/dbs/nlfff/). 少量数据(<100GB) 可以直接从网络下载, 对于大量数据(100GB-200TB) 我们推荐先联系我们，然后通过邮寄硬盘等方式传递数据。**

| Generation stage | File name                                                  | Description                                                  |
| ---------------- | ---------------------------------------------------------- | ------------------------------------------------------------ |
| prepare          | grid1.ini,grid2.ini,grid3.ini                              | Information about the grid used for the corresponding level  |
|                  | mask1.dat,mask2.dat,mask3.dat                              | The mask data used for the corresponding level               |
|                  | allboundaries1.dat, allboundaries2.dat, allboundaries3.dat | The boundaries data used for the corresponding level         |
|                  | boundary.ini                                               | Boundary and algorithm information                           |
| process          | Bout.bin                                                   | Nonlinear force-free field                                   |
|                  | B0.bin                                                     | Potential field, due to storage problems, this part of the data is partially saved |
|                  | NLFFFquality1.log, NLFFFquality2.log, NLFFFquality3.log    | Corresponding grade of product quality                       |
|                  | prot1.log, prot2.log, prot3.log                            | Corresponding level iteration log information                |
|                  | step1.log, step2.log, step3.log                            | Information on the number of iterative steps for the corresponding level |
|                  | Energy.log                                                 | Run Energy Log, If you only run to grid1, this part may not have |
| archive          | run.log                                                    | Run Print Detail Log                                         |



## 标签数据

可以从 [这个链接](https://figshare.com/articles/dataset/NLFFF_Dataset_Flare_Label/21760637?backTo=/collections/Archive_Information_of_Three-Dimensional_Solar_Magnetic_Fields_Dataset/6214666) 下载到下表的耀斑标签及中间文件。

| Generation stage | File name                                                    | Description                                                  |
| ---------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| raw_file         | flare_raw | The folder containing the original flare information for download |
| raw_file         | all_harps_with_noaa_ars.txt | Mapping update for HARP number and NOAA number               |
| prepare          | knoaa_vflaretimelist.pickle | The dictionary with key NOAA number,value flare time list is saved as python pickle |
| prepare          | ksharp_vnoaa.pickle | Key is HARP number,value is NOAA number list of dictionaries saved as python pickle |
| process          | label.csv | Sample Label Information                                     |



## 数据库归档

可以从 [sqlite-202203/a202203-nlfff.db](https://figshare.com/articles/dataset/NLFFF_Dataset_and_Flare_Label_Database_Archive/21760658?backTo=/collections/Archive_Information_of_Three-Dimensional_Solar_Magnetic_Fields_Dataset/6214666)下载到数据库摘要及数据库标签的信息。

数据库包括下面内容:

| Col Name                                                     | Type        | Description                                                  |
| ------------------------------------------------------------ | ----------- | ------------------------------------------------------------ |
| harpnum_trec                                                 | timestamp   | HARP number and time from raw fits name                      |
| sync with raw fits                                           | sync raw    | find from http://jsoc.stanford.edu/ajax/lookdata.html?ds=hmi.sharp_cea_720s |
| grid_x                                                       | int4        | we finally can calculate the nx,ny,nz corresponding to the level, that is, the nx,ny,nz corresponding to the saved Bout.bin file |
| grid_y                                                       | int4        |                                                              |
| grid_z                                                       | int4        |                                                              |
| bout_maxlevel                                                | int4        | The final calculated level,The level of the last saved bout  |
| bout_quality_value                                           | float8      | Set to True if quality is less than 30, else False.          |
| bout_quality                                                 | bool        | The final calculated quality,The quality of the last saved bout |
| bout_path                                                    | text        | The path where Bout is saved, and other files in the same subdirectory as Bout |
| bout_md5                                                     | varchar(32) | The md5 of Bout                                              |
| bout_size                                                    | int8        | The size of Bout                                             |
| batch                                                        | int8        | Calculated batches, other calculated batches may be available in the future |
| now_flare_level                                              | int4        | Current Flare Level                                          |
| now_flare_id                                                 | int4        | Current Flare id                                             |
| h6_flare_level, h12_flare_level, h24_flare_level, h48_flare_level | int4        | Maximum flare levels in 6, 12, 24 and 48 hours, respectively |
| h6_flare_id, h12_flare_id, h24_flare_id, h48_flare_id        | int4        | The ids corresponding to the maximum flare levels in 6,12,24,48 hours, respectively |
| h24_posmx                                                    | int8        | 0 - No MX or CMX level flares in hour24 or 48;1 - MX or CMX level flares within hour24 or 48;2 - MX or CMX Flares occur within hour24 or 48 and the sample does not have a MX or CMX level flare at that moment |
| h24_poscmx                                                   | int8        |                                                              |
| h48_posmx                                                    | int8        |                                                              |
| h48_poscmx                                                   | int8        |                                                              |
| h24_delta05                                                  | int8        | Maximum change in grade in 24 hours                          |
| h48_delta05                                                  | int8        | Maximum change in grade in 48 hours                          |

标签数据包括下表内容:

| Col Name       | Type        | Description                                                  |
| -------------- | ----------- | ------------------------------------------------------------ |
| deeps_flare_id | int4        | The id that uniquely identifies the flare information in the deepsolar database system |
| start_datetime | timestamp   | Flare start time                                             |
| peak_datetime  | timestamp   | Flare end time                                               |
| end_datetime   | timestamp   | Flare peaking time                                           |
| xray_class     | varchar(1)  | Flare level class                                            |
| xray_intensity | int4        | Intensity of raw data multiplied by 10                       |
| latitude       | int4        | latitude                                                     |
| longtitude     | int4        | longtitude                                                   |
| noaa_ar        | int4        | Corresponding NOAA active region number                      |
| source         | varchar(16) | Data source                                                  |





