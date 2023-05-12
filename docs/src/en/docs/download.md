## Overall

The dataset is divided into three main parts: **3D magnetic field data file** , **sample label file** and **database archive file**.

### 1 3D magnetic field data file

is divided into two parts: summary information and specific data information.

+ summary information including
    + Raw data header information
    + Information generated in the 3D magnetic field extrapolation
+ Specific files include
    + Raw files
    + Preprocessing files
    + 3D magnetic field product files
    + Visualization files

#### 1.1 Download of summary information
<iframe src="https://widgets.figshare.com/articles/21760598/embed?show_title=1" width="568" height="351" allowfullscreen frameborder="0 "></iframe>
> In which we also provide basic usage guidelines.

#### 1.2 Dataset sample file query and download

##### 1.2.1 Raw data
Download [sharp cea](http://jsoc.stanford.edu/doc/data/hmi/) from [JSOC](http://jsoc.stanford.edu) using [drms](https://github.com/mbobra/SHARPs) sharp/sharp.htm) files (including Bp.bits, Bt.bits, Br.bits) as raw files.


##### 1.2.2 Product data search via the project website

The project website is located at: http://database.deepsolar.space:18080/dbs/nlfff/

##### 1.2.3 Product data is accessed via identifiers jump

identifiers repository address <https://registry.identifiers.org/registry/nlfff>

> Single sample access and reference example: <https://identifiers.org/nlfff:345201101230312003>

> where 345(harp number)20110123(date)031200(time)3(Max grid level).

##### 1.2.4 Massive product data

For large amounts of data (100GB-200TB) we recommend contacting us first and then sending the data via hard disk, etc. Emails can be found on the **Contact** page.




### 2 Sample label files

The sample tag file can be downloaded from the following address.

<iframe src="https://widgets.figshare.com/articles/21760637/embed?show_title=1" width="568" height="351" allowfullscreen frameborder="0 "></iframe>
> In which we also provide basic usage guidelines.



### 3 Database archive files

The database archive file, including sample information, label information, and flare information, can be downloaded at the following address.
<iframe src="https://widgets.figshare.com/articles/21760658/embed?show_title=1" width="568" height="351" allowfullscreen frameborder="0 "></iframe>
> In it we also provide basic usage guidelines.


> Download demo notebook can be [click here to download](https://github.com/deepsolar/pynlfff/blob/main/test/guide/Dataset_nlfff_and_pynlfff_base_use_en.ipynb), or [click here to open in Huawei Modelart](https://developer.huaweicloud.com/develop/aigallery/notebook/detail?id=f9e4f1ea-49a3-460b-abc9-41bbf82c0e0a), or [click here to open it in google colab](https://colab.research.google.com/drive/1KNS2lf-kUAYd3QDhd4Y3lOnaE8UBKUHf?usp=sharing), and the html version can be viewed [here](https://nlfff.dataset.deepsolar.space/en/guide/Dataset_nlfff_and_pynlfff_base_use_en.html)


