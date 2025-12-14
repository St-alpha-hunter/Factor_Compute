### 项目名称 ###

自动化计算高频因子工作流

### 项目描述 ###

该项目是一个计算高频因子的工作流，支持用户一键完成对多个高频因子的快速生成及复现

### 项目结构 ###

```
YanFeng/
├── Project/
│   ├── main.py                    # 主程序入口
│   ├── config.py                  # 配置文件
│   ├── factorValue_YF.csv         # 输出的因子值文件
│   ├── example_csv_write.py       # CSV写入示例
│   ├── practice_03.ipynb          # 开发调试notebook
│   │
│   ├── src/                       # 核心代码模块
│   │   ├── __init__.py
│   │   ├── data_load.py          # 数据加载模块
│   │   ├── factor_cal.py         # 因子计算模块
│   │   ├── write_csv.py          # CSV写入模块
│   │   └── data_clean.py         # 数据清洗模块
│   │
│   ├── data_set/                 # 原始数据目录
│   │   ├── 000001.SZ/           # 股票数据文件夹
│   │   │   ├── 行情.csv
│   │   │   ├── 逐笔委托.csv
│   │   │   └── 逐笔成交.csv
│   │   ├── 000002.SZ/
│   │   ├── 600000.SH/
│   │   └── ...                  # 更多股票数据
│   │
│   ├── factor_cal/              # 因子计算相关
│   ├── factor_writen/           # 因子输出相关
│   │
│   └── utils/                   # 工具函数
│       ├── __init__.py
│       └── path_helper.py       # 路径辅助函数
│
└── README.MD                    # 项目说明文档
```


### 环境要求 ###

pip install -r requirements.txt

### 操作流程 ###

1,把清洗好的沪深tick级数据放置到data_set文件夹下
2,确保工作目录在/Project下面， python main.py  一键生成因子表

### 作者信息 ###
王立豪 2025 12.13# Factor_Compute
