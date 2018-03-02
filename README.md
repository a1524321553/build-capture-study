# Build Capture

------

对由makefile控制的工程做一些处理, 以得到各个源文件预处理之后的文件,并保存对应关系

## 使用
* Ubuntu系统下，需安装python2.7

* 以及安装pyinotify工具
> sudo pip install pyinotify

* 将项目文件夹保存在本地，例如:
> /home/wangcong15/Desktop/build-capture

* 使用alias更名并生效([方法请见此处](https://www.zybuluo.com/cmd/))，例如:
> alias bcmake='python /home/wangcong15/Desktop/build-capture/BuildCaptureStart.py'

* 使用Ubuntu控制台，cd到需要进行make的项目中，执行bcmake指令即可运行

* 若是需选用其它shell进行make(例如sh)，可以在指令后添加参数，默认情况下使用bash
> bcmake -s /bin/sh


## 处理结果
* 在执行bcmake指令的文件夹上级目录中，生成了一个单独的BCOUTPUT文件夹，其文件夹中的内容说明如下：
> * line文件夹: 里面保存各行输出的 .i 文件
> * task文件夹: 里面保存输出可执行程序需要的所有 .i 文件
> * all: 保存make输出的所有内容(包括stdout和stderr), 如果进行了打开静默开关的抓取, make的所有内容会保存在这里
> * output: 对all里面结果过滤后的结果, 只有gcc命令以及文件夹切换的命令
> * outputParse: 保存对output文件转化后的各个命令
> * fileMap: 各种 .o .c 等文件的 绝对路经 与 .i 文件的 绝对路径 的对应关系
> * libMap: 各种动态静态链接库的 绝对路径 与 .o 文件的 绝对路径的对应关系
> * tasks.json: 最终结果输出的文件, 包括每个task有哪些文件, 行数统计等信息

### 作者 [@CongWang][1]

[1]: http://congwang.tech

