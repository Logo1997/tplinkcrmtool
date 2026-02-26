# -*- coding: utf-8 -*-
"""
价格计算工具
"""

from typing import Tuple, Optional


def round_price(price: float) -> int:
    """
    根据价格位数进行向上取整
    - 二位数和三位数：向上取整为5的倍数
    - 四位数：向上取整为10的倍数
    - 五位数及以上：向上取整为100的倍数
    """
    if price <= 0:
        return 0
    
    price_int = int(price)
    
    if price_int < 100:
        if price_int % 5 == 0:
            return price_int
        return ((price_int // 5) + 1) * 5
    elif price_int < 1000:
        if price_int % 5 == 0:
            return price_int
        return ((price_int // 5) + 1) * 5
    elif price_int < 10000:
        if price_int % 10 == 0:
            return price_int
        return ((price_int // 10) + 1) * 10
    else:
        if price_int % 100 == 0:
            return price_int
        return ((price_int // 100) + 1) * 100


def calculate_discount_prices(price: float, business_discount: str) -> Tuple[Optional[int], Optional[int]]:
    """
    计算高折扣价格和低折扣价格
    
    Args:
        price: 产品价格
        business_discount: 业务折扣字符串，如 "0.5~0.45" 或 "0.5-0.45"
        
    Returns:
        (高折扣价格, 低折扣价格) 元组
    """
    if not price or not business_discount:
        return None, None
    
    try:
        parts = None
        for separator in ['~', '-']:
            if separator in business_discount:
                parts = business_discount.split(separator)
                break
        
        if not parts or len(parts) != 2:
            return None, None
        
        high_discount = float(parts[0].strip())
        low_discount = float(parts[1].strip())
        
        high_price = price * high_discount
        low_price = price * low_discount
        
        high_rounded = round_price(high_price)
        low_rounded = round_price(low_price)
        
        return high_rounded, low_rounded
        
    except (ValueError, AttributeError):
        return None, None
