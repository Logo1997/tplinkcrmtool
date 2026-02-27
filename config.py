# -*- coding: utf-8 -*-
"""
TP-LINK CRM Mobile 配置文件
"""

import sys
import shutil
from pathlib import Path

_platform = None

def get_platform():
    global _platform
    if _platform is None:
        try:
            from kivy.utils import platform as kivy_platform
            _platform = kivy_platform
        except:
            _platform = ''
    return _platform

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

CRM_CONFIG = {
    'base_url': 'https://sales.tp-link.net',
    'api_login': '/api/login',
    'api_price_query': '/api/line/findByPage',
    'api_inventory_query': '/api/inv/findInvQtyTab',
}

WEBSITE_CONFIG = {
    'base_url': 'https://www.tp-link.com.cn',
    'product_url_template': 'https://www.tp-link.com.cn/product_{id}.html',
    'search_url': 'https://www.tp-link.com.cn/search.html',
    'max_product_id': 6000,
}

QUERY_CONFIG = {
    'timeout': 30,
    'verify_ssl': False,
    'delay_min': 0.3,
    'delay_max': 0.8,
    'max_retries': 3,
}

STORAGE_CONFIG = {
    'data_dir': BASE_DIR / 'data',
    'cache_file': BASE_DIR / 'data' / 'product_cache.json',
    'session_file': BASE_DIR / 'data' / '.session',
}

CRAWLER_CONFIG = {
    'concurrent_workers': 5,
    'request_delay': 0.5,
    'timeout': 15,
}

PRICE_QUERY_FIELDS = {
    'line_id': 'lineId',
    'product_id': 'productId',
    'line_code': 'lineCode',
    'product_model': 'productModel',
    'product_name': 'productName',
    'price': 'price',
    'wholesale_price': 'wholesalePrice',
    'catalog_price': 'catalogPrice',
    'business_discount': 'businessDiscount',
    'brand': 'brandValue',
    'series': 'seriesValue',
    'life_cycle': 'lifeCycle',
    'life_cycle_meaning': 'lifeCycleMeaning',
    'start_qty': 'startQty',
    'end_qty': 'endQty',
    'valid': 'valid',
    'creation_date': 'creationDate',
    'last_update_date': 'lastUpdateDate',
}

INVENTORY_QUERY_FIELDS = {
    'product_model': 'productModel',
    'product_name': 'productName',
    'life_cycle_meaning': 'lifeCycleMeaning',
    'sub_inventory': 'subInventory',
    'quantity': 'quantity',
    'in_transit': 'inTransitQty',
    'today_out': 'todayOutQty',
}

STORAGE_CONFIG['data_dir'].mkdir(parents=True, exist_ok=True)


def init_android_assets():
    platform = get_platform()
    if platform != 'android':
        return
    
    try:
        from android.storage import primary_external_storage_path
        external_dir = Path(primary_external_storage_path()) / 'TPLinkCRM' / 'data'
        external_dir.mkdir(parents=True, exist_ok=True)
        
        import os
        app_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        
        if os.path.exists(app_data_dir):
            cache_src = os.path.join(app_data_dir, 'product_cache.json')
            cache_dst = external_dir / 'product_cache.json'
            
            if os.path.exists(cache_src) and not cache_dst.exists():
                shutil.copy2(cache_src, str(cache_dst))
                print(f"已复制缓存文件到: {cache_dst}")
    except Exception as e:
        print(f"初始化 Android 资源失败: {e}")
