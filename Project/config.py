import os

# 基础路径


def find_project_root():
    # 从config.py所在目录开始，向上查找包含data_set的目录
    current = os.path.dirname(os.path.abspath(__file__))
    while current != os.path.dirname(current):  # 不是根目录
        if os.path.exists(os.path.join(current, 'data_set')):
            return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.abspath(__file__))  # 找不到就返回config目录

BASE_PATH = find_project_root()

DATA_SET_PATH = os.path.join(BASE_PATH, 'data_set')

# 路径模板，使用format字符串
STOCK_DATA_PATH_TEMPLATE = os.path.join(DATA_SET_PATH, '{stock_code}')
STOCK_FILE_PATH_TEMPLATE = os.path.join(DATA_SET_PATH, '{stock_code}', '{file_type}.csv')

# 文件类型映射
FILE_TYPES = {
    'market': '行情',
    'order': '逐笔委托', 
    'transaction': '逐笔成交'
}

# 路径构建函数
def get_stock_data_path(stock_code: str) -> str:
    """获取股票数据文件夹路径"""
    return STOCK_DATA_PATH_TEMPLATE.format(stock_code=stock_code)

def get_stock_file_path(stock_code: str, file_type: str) -> str:
    """获取股票数据文件路径
    
    Args:
        stock_code: 股票代码，如 '000001.SZ'
        file_type: 文件类型，支持 'market', 'order', 'transaction'
    """
    if file_type not in FILE_TYPES:
        raise ValueError(f"不支持的文件类型: {file_type}, 支持的类型: {list(FILE_TYPES.keys())}")
    
    file_name = FILE_TYPES[file_type]
    return STOCK_FILE_PATH_TEMPLATE.format(stock_code=stock_code, file_type=file_name)