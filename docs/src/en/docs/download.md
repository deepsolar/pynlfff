
## Overall


[Summary Information](https://doi.org/10.6084/m9.figshare.c.6214666)

[Search Online](http://database.deepsolar.space:18080/dbs/nlfff/)


## Raw File Data

We use [drms](https://github.com/mbobra/SHARPs) to download the [sharp cea](http://jsoc.stanford.edu/doc/data/hmi/sharp/sharp.htm) file (Bp.fits, Bt.fits, Br.fits) from [JSOC](http://jsoc.stanford.edu) as raw file and save it in the [raw-202203](https://figshare.com/articles/dataset/NLFFF_Dataset_Information/21760598?backTo=/collections/Archive_Information_of_Three-Dimensional_Solar_Magnetic_Fields_Dataset/6214666) folder, which can be found in [this article](https://todo.com) with detailed filtering criteria.


## NLFFF File Data

The product files are stored in the [archive-202203](https://figshare.com/articles/dataset/NLFFF_Dataset_Information/21760598?backTo=/collections/Archive_Information_of_Three-Dimensional_Solar_Magnetic_Fields_Dataset/6214666) folder, the folder naming convention can be found in this article or read in this sqlite database, each folder has the contents listed in the table below


**You can also [filter and query here](http://database.deepsolar.space:18080/dbs/nlfff/). For small amounts of data (<100GB) you can try downloading directly through the web, for large amounts of data (100GB-200TB) we recommend contacting us first to deliver it by sending a hard drive, etc.**

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



## Label File Data

This is the data generated when generating the label, which you can access through [the links](https://figshare.com/articles/dataset/NLFFF_Dataset_Flare_Label/21760637?backTo=/collections/Archive_Information_of_Three-Dimensional_Solar_Magnetic_Fields_Dataset/6214666) in the table below.

| Generation stage | File name                                                    | Description                                                  |
| ---------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| raw_file         | flare_raw | The folder containing the original flare information for download |
| raw_file         | all_harps_with_noaa_ars.txt | Mapping update for HARP number and NOAA number               |
| prepare          | knoaa_vflaretimelist.pickle | The dictionary with key NOAA number,value flare time list is saved as python pickle |
| prepare          | ksharp_vnoaa.pickle | Key is HARP number,value is NOAA number list of dictionaries saved as python pickle |
| process          | label.csv | Sample Label Information                                     |



## NLFFF and flare info in sqlite database

You can download the sqlite database file with nlfff and flare information from [sqlite-202203/a202203-nlfff.db](https://figshare.com/articles/dataset/NLFFF_Dataset_and_Flare_Label_Database_Archive/21760658?backTo=/collections/Archive_Information_of_Three-Dimensional_Solar_Magnetic_Fields_Dataset/6214666).

For NLFFF data is described in the following table:

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

For flare data is described in the following table:

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





