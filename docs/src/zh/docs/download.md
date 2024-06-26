



## 总体上

数据集分为 **三维磁场数据文件** 、**样本标签文件** 和 **数据库归档文件** 三大部分。

### 1 三维磁场数据文件

分为摘要信息和具体数据信息两部分：

+ 摘要信息包括
    + 原始数据头文件信息
    + 三维磁场外推中生成的信息
+ 具体文件包括
    + 原始文件
    + 预处理文件
    + 三维磁场产品文件
    + 可视化文件

#### 1.1 摘要信息的下载
<iframe src="https://widgets.figshare.com/articles/21760598/embed?show_title=1" width="568" height="351" allowfullscreen frameborder="0"></iframe>
> 在其中我们也提供基本使用指南。

#### 1.2 数据集样本文件的查询和下载

##### 1.2.1 原始数据
使用 [drms](https://github.com/mbobra/SHARPs) 从 [JSOC](http://jsoc.stanford.edu) 下载 [sharp cea](http://jsoc.stanford.edu/doc/data/hmi/sharp/sharp.htm) 文件 (包括Bp.fits, Bt.fits, Br.fits) 作为原始文件。


##### 1.2.2 产品数据通过项目网站查询

项目网站地址：http://database.deepsolar.space:18080/dbs/nlfff/

##### 1.2.3 产品数据通过identifiers跳转访问

identifiers仓库地址 <https://registry.identifiers.org/registry/nlfff>

> 单个样本访问和引用例子：<https://identifiers.org/nlfff:345201101230312003>

> 其中 345(harp number)20110123(date)031200(time)3(Max grid level).

##### 1.2.4 大量产品数据

对于大量数据(100GB-200TB) 我们推荐先联系我们，然后通过邮寄硬盘等方式传递数据。可在 **联系** 页面找到电子邮件。




### 2 样本标签文件

样本标签文件可从下面地址下载：

<iframe src="https://widgets.figshare.com/articles/21760637/embed?show_title=1" width="568" height="351" allowfullscreen frameborder="0"></iframe>
> 在其中我们也提供基本使用指南。



### 3 数据库归档文件

数据库归档文件，包括样本信息、标签信息和耀斑信息，可以通过下面地址下载：
<iframe src="https://widgets.figshare.com/articles/21760658/embed?show_title=1" width="568" height="351" allowfullscreen frameborder="0"></iframe>
> 在其中我们也提供基本使用指南。


> 下载数据集演示的notebook可以[点击这里下载](https://github.com/deepsolar/pynlfff/blob/main/test/guide/Dataset_nlfff_and_pynlfff_base_use_zh.ipynb)，可以[点击这里在华为modelart打开](https://developer.huaweicloud.com/develop/aigallery/notebook/detail?id=f9e4f1ea-49a3-460b-abc9-41bbf82c0e0a)，也可以[点击这里在google colab中打开](https://colab.research.google.com/drive/1tbDwW0dr25txDv9L_SeepnRBbmHB2j9p?usp=sharing)， html版本可以在[这里查看](https://nlfff.dataset.deepsolar.space/zh/guide/Dataset_nlfff_and_pynlfff_base_use_zh.html)




