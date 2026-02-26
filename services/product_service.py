# -*- coding: utf-8 -*-
"""
产品查询服务
"""

import time
import logging
from typing import List, Dict, Optional

from config import CRM_CONFIG, PRICE_QUERY_FIELDS
from models import ProductInfo, InventoryInfo
from services.auth_service import AuthService
from utils import calculate_discount_prices

logger = logging.getLogger(__name__)


class ProductService:
    """产品查询服务"""
    
    def __init__(self, auth_service: AuthService):
        self.auth = auth_service
        self.price_api = CRM_CONFIG['api_price_query']
        self.inventory_api = CRM_CONFIG['api_inventory_query']
    
    def search_products(self, model: str, limit: int = 50) -> List[ProductInfo]:
        """
        搜索产品
        
        Args:
            model: 产品型号
            limit: 返回数量限制
            
        Returns:
            产品列表
        """
        logger.info(f"搜索产品: {model}")
        
        params = {
            '_dc': int(time.time() * 1000),
            'blurValue': model,
            'undefined': 'on',
            'start': 0,
            'limit': limit
        }
        
        result = self.auth.get(self.price_api, params=params)
        
        if not result:
            logger.error("产品搜索失败")
            return []
        
        data = result.get('results', result.get('data', result.get('list', [])))
        
        products = []
        for item in data:
            product = self._parse_product(item, model)
            products.append(product)
        
        products = self._deduplicate(products)
        
        logger.info(f"搜索到 {len(products)} 个产品")
        return products
    
    def _parse_product(self, raw_data: dict, query_model: str) -> ProductInfo:
        """解析产品数据"""
        product = ProductInfo()
        
        for field_name, field_key in PRICE_QUERY_FIELDS.items():
            raw_value = raw_data.get(field_key, '')
            
            if 'price' in field_name.lower() and raw_value:
                try:
                    setattr(product, field_name, float(raw_value))
                except (ValueError, TypeError):
                    setattr(product, field_name, raw_value)
            elif 'qty' in field_name.lower() and raw_value:
                try:
                    setattr(product, field_name, int(raw_value))
                except (ValueError, TypeError):
                    setattr(product, field_name, raw_value)
            elif field_name == 'product_model':
                product.product_model = raw_value
            elif field_name == 'product_name':
                product.product_name = raw_value
            elif field_name == 'product_id':
                product.product_id = int(raw_value) if raw_value else 0
            elif field_name == 'line_id':
                product.line_id = int(raw_value) if raw_value else 0
            elif field_name == 'brand':
                product.brand = raw_value
            elif field_name == 'series':
                product.series = raw_value
            elif field_name == 'life_cycle':
                product.life_cycle = raw_value
            elif field_name == 'life_cycle_meaning':
                product.life_cycle_meaning = raw_value
            elif field_name == 'business_discount':
                product.business_discount = raw_value
            elif field_name == 'valid':
                product.valid = bool(raw_value)
            elif field_name == 'last_update_date':
                product.last_update_date = raw_value
        
        product.is_exact_match = (product.product_model.lower() == query_model.lower())
        
        high_price, low_price = calculate_discount_prices(product.price, product.business_discount)
        product.high_discount_price = high_price
        product.low_discount_price = low_price
        
        return product
    
    def _deduplicate(self, products: List[ProductInfo]) -> List[ProductInfo]:
        """去重，保留最低阶梯价格"""
        product_map = {}
        
        for product in products:
            model_key = product.product_model
            
            if model_key:
                if model_key not in product_map:
                    product_map[model_key] = product
                else:
                    existing = product_map[model_key]
                    if product.start_qty < existing.start_qty:
                        product_map[model_key] = product
        
        return list(product_map.values())
    
    def query_inventory(self, model: str) -> List[InventoryInfo]:
        """
        查询库存
        
        Args:
            model: 产品型号
            
        Returns:
            库存列表
        """
        logger.info(f"查询库存: {model}")
        
        params = {
            '_dc': int(time.time() * 1000),
            'blurValue': '',
            'invIdList': '',
            'productModel': model,
            'brandIdList': '',
            'seriesIdList': '',
            'firstCategoryInternalIdList': '',
            'secondCategoryInternalIdList': '',
            'showPrice': 'true',
            'start': 0
        }
        
        result = self.auth.get(self.inventory_api, params=params)
        
        if not result:
            logger.error("库存查询失败")
            return []
        
        data = result.get('results', result.get('data', result.get('list', [])))
        
        inventory_list = []
        for item in data:
            product_model = item.get('model', item.get('productModel', ''))
            
            if product_model.lower() != model.lower():
                continue
            
            inventory = InventoryInfo(
                product_model=product_model,
                product_name=item.get('productName', ''),
                life_cycle_meaning=item.get('lifeCycle', item.get('lifeCycleMeaning', '')),
                sub_inventory=item.get('invName', ''),
                quantity=item.get('qty', item.get('quantity', 0)),
                in_transit=item.get('orderIntransitNum', item.get('inTransitQty', 0)),
                today_out=item.get('todayOutQty', 0),
                box_number=item.get('boxNumber', ''),
                price_info=item.get('priceInfo', ''),
            )
            inventory_list.append(inventory)
        
        logger.info(f"查询到 {len(inventory_list)} 条库存记录")
        return inventory_list
