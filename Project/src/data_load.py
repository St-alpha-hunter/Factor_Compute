import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from typing import Optional
from config import get_stock_file_path, FILE_TYPES

def load_data(file_path: str) -> pd.DataFrame:
    """通用的数据加载函数，支持多种编码格式"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    # 尝试不同的编码格式读取文件
    try:
        # 先尝试 gbk 编码（中文Windows常用）
        df = pd.read_csv(file_path, encoding='gbk')
        print(f"成功使用 gbk 编码读取文件: {file_path}")
        return df
    except UnicodeDecodeError:
        try:
            # 如果gbk失败，尝试 gb2312
            df = pd.read_csv(file_path, encoding='gb2312')
            print(f"成功使用 gb2312 编码读取文件: {file_path}")
            return df
        except UnicodeDecodeError:
            try:
                # 如果gb2312失败，尝试 latin1
                df = pd.read_csv(file_path, encoding='latin1')
                print(f"成功使用 latin1 编码读取文件: {file_path}")
                return df
            except UnicodeDecodeError:
                # 最后尝试忽略错误
                df = pd.read_csv(file_path, encoding='utf-8', errors='ignore')
                print(f"使用 utf-8 编码并忽略错误读取文件: {file_path}")
                return df
            

def load_stock_data(stock_code: str, file_type: str) -> pd.DataFrame:
    """加载指定股票的指定类型数据
    
    Args:
        stock_code: 股票代码，如 '000001.SZ'
        file_type: 文件类型，支持 'market', 'order', 'transaction'
    
    Returns:
        DataFrame: 加载的数据
    """
    file_path = get_stock_file_path(stock_code, file_type)
    return load_data(file_path)

def load_multiple_stocks(stock_codes: list, file_type: str) -> dict:
    """批量加载多个股票的同类型数据
    
    Args:
        stock_codes: 股票代码列表
        file_type: 文件类型
        
    Returns:
        dict: {股票代码: DataFrame}
    """
    result = {}
    for code in stock_codes:
        try:
            result[code] = load_stock_data(code, file_type)
            print(f"成功加载 {code} 的 {FILE_TYPES[file_type]} 数据")
        except Exception as e:
            print(f"加载 {code} 的 {FILE_TYPES[file_type]} 数据失败: {e}")
    
    return result




def get_all_stock_codes() -> list:
    """获取data_set目录下的所有股票代码子文件夹名称
    
    Returns:
        list: 股票代码列表，如 ['000001.SZ', '000002.SZ', ...]
    """
    from config import DATA_SET_PATH
    
    if not os.path.exists(DATA_SET_PATH):
        print(f"数据目录不存在: {DATA_SET_PATH}")
        return []
    
    # 获取data_set目录下的所有项目
    all_items = os.listdir(DATA_SET_PATH)
    
    # 筛选出文件夹（排除文件）
    stock_codes = []
    for item in all_items:
        item_path = os.path.join(DATA_SET_PATH, item)
        if os.path.isdir(item_path):  # 只要文件夹
            stock_codes.append(item)
    
    # 按字母顺序排序
    stock_codes.sort()
    
    print(f"找到 {len(stock_codes)} 个股票代码文件夹")
    return stock_codes

def get_stock_codes_by_exchange(exchange: str = None) -> list:
    """按交易所筛选股票代码
    
    Args:
        exchange: 交易所代码，'SZ' 或 'SH'，None则返回全部
    
    Returns:
        list: 筛选后的股票代码列表
    """
    all_codes = get_all_stock_codes()
    
    if exchange is None:
        return all_codes
    
    exchange = exchange.upper()  # 转为大写
    filtered_codes = [code for code in all_codes if code.endswith(f'.{exchange}')]
    
    print(f"找到 {len(filtered_codes)} 个 {exchange} 交易所的股票")
    return filtered_codes