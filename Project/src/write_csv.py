import os
import sys
import pandas as pd
import csv
from typing import Optional, Dict, Any
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


##把表格展开
def build_row(security_id: str, r: dict) -> dict:
    return {
        "SecurityID": security_id,
        "VOLUME_RATIO": r.get("volume_ratio"),

        # ACT
        "ACT": r.get("act_ratio", {}).get("overall"),
        "L_ACT": r.get("act_ratio", {}).get("by_size", {}).get("L"),
        "M_ACT": r.get("act_ratio", {}).get("by_size", {}).get("M"),
        "S_ACT": r.get("act_ratio", {}).get("by_size", {}).get("S"),
        "X_ACT": r.get("act_ratio", {}).get("by_size", {}).get("X"),

        # ORDER_RATIO
        "XLS_ORDER_RATIO": r.get("order_ratio", {}).get("by_size", {}).get("X"),
        "L_ORDER_RATIO": r.get("order_ratio", {}).get("by_size", {}).get("L"),
        "M_ORDER_RATIO": r.get("order_ratio", {}).get("by_size", {}).get("M"),
        "S_ORDER_RATIO": r.get("order_ratio", {}).get("by_size", {}).get("S"),
    }


def write_csv(results: dict) -> None:
    #rows = [] 避免使用
    # for security_id, r in results.items():
    #     rows.append(build_row(security_id, r)) ##避免使用append
    df = pd.DataFrame([build_row(security_id, r) for security_id, r in results.items()])
    df.to_csv(
        "factorValue_YF.csv",
        index=False,
        encoding="utf-8-sig"
    )

    