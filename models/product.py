# -*- coding: utf-8 -*-
"""
数据模型定义
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class ProductInfo:
    product_model: str = ''
    product_name: str = ''
    product_id: int = 0
    line_id: int = 0
    brand: str = ''
    series: str = ''
    life_cycle: str = ''
    life_cycle_meaning: str = ''
    price: float = 0.0
    wholesale_price: float = 0.0
    catalog_price: float = 0.0
    business_discount: str = ''
    high_discount_price: Optional[int] = None
    low_discount_price: Optional[int] = None
    start_qty: int = 0
    end_qty: int = 0
    valid: bool = True
    last_update_date: str = ''
    is_exact_match: bool = False
    
    def to_dict(self) -> dict:
        return {
            'product_model': self.product_model,
            'product_name': self.product_name,
            'product_id': self.product_id,
            'line_id': self.line_id,
            'brand': self.brand,
            'series': self.series,
            'life_cycle': self.life_cycle,
            'life_cycle_meaning': self.life_cycle_meaning,
            'price': self.price,
            'wholesale_price': self.wholesale_price,
            'catalog_price': self.catalog_price,
            'business_discount': self.business_discount,
            'high_discount_price': self.high_discount_price,
            'low_discount_price': self.low_discount_price,
            'start_qty': self.start_qty,
            'end_qty': self.end_qty,
            'valid': self.valid,
            'last_update_date': self.last_update_date,
            'is_exact_match': self.is_exact_match,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProductInfo':
        return cls(
            product_model=data.get('product_model', ''),
            product_name=data.get('product_name', ''),
            product_id=data.get('product_id', 0),
            line_id=data.get('line_id', 0),
            brand=data.get('brand', ''),
            series=data.get('series', ''),
            life_cycle=data.get('life_cycle', ''),
            life_cycle_meaning=data.get('life_cycle_meaning', ''),
            price=data.get('price', 0.0),
            wholesale_price=data.get('wholesale_price', 0.0),
            catalog_price=data.get('catalog_price', 0.0),
            business_discount=data.get('business_discount', ''),
            high_discount_price=data.get('high_discount_price'),
            low_discount_price=data.get('low_discount_price'),
            start_qty=data.get('start_qty', 0),
            end_qty=data.get('end_qty', 0),
            valid=data.get('valid', True),
            last_update_date=data.get('last_update_date', ''),
            is_exact_match=data.get('is_exact_match', False),
        )


@dataclass
class ProductFeatures:
    product_model: str = ''
    product_name: str = ''
    product_id: int = 0
    url: str = ''
    features: List[str] = field(default_factory=list)
    crawl_time: str = ''
    
    def to_dict(self) -> dict:
        return {
            'product_model': self.product_model,
            'product_name': self.product_name,
            'product_id': self.product_id,
            'url': self.url,
            'features': self.features,
            'crawl_time': self.crawl_time,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProductFeatures':
        return cls(
            product_model=data.get('product_model', ''),
            product_name=data.get('product_name', ''),
            product_id=data.get('product_id', 0),
            url=data.get('url', ''),
            features=data.get('features', []),
            crawl_time=data.get('crawl_time', ''),
        )
    
    def get_features_text(self) -> str:
        return '\n'.join(f"{i+1}. {f}" for i, f in enumerate(self.features))


@dataclass
class InventoryInfo:
    product_model: str = ''
    product_name: str = ''
    life_cycle_meaning: str = ''
    sub_inventory: str = ''
    quantity: int = 0
    in_transit: int = 0
    today_out: int = 0
    box_number: str = ''
    price_info: str = ''
    
    def to_dict(self) -> dict:
        return {
            'product_model': self.product_model,
            'product_name': self.product_name,
            'life_cycle_meaning': self.life_cycle_meaning,
            'sub_inventory': self.sub_inventory,
            'quantity': self.quantity,
            'in_transit': self.in_transit,
            'today_out': self.today_out,
            'box_number': self.box_number,
            'price_info': self.price_info,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'InventoryInfo':
        return cls(
            product_model=data.get('product_model', ''),
            product_name=data.get('product_name', ''),
            life_cycle_meaning=data.get('life_cycle_meaning', ''),
            sub_inventory=data.get('sub_inventory', ''),
            quantity=data.get('quantity', 0),
            in_transit=data.get('in_transit', 0),
            today_out=data.get('today_out', 0),
            box_number=data.get('box_number', ''),
            price_info=data.get('price_info', ''),
        )


@dataclass
class LoginResult:
    success: bool = False
    message: str = ''
    user_name: str = ''
    office_name: str = ''
