# TP-LINK CRM 产品查询工具 - 移动版

基于 Kivy 框架的 TP-LINK CRM 产品查询移动应用。

## 安装依赖

```bash
pip install kivy requests beautifulsoup4
```

## 运行

```bash
python main.py
```

## 打包 APK

### 1. 安装 Buildozer (需要 Linux 环境)

```bash
pip install buildozer
```

### 2. 初始化并打包

```bash
buildozer init
buildozer android debug
```

### 3. 发布版本

```bash
buildozer android release
```

## 项目结构

```
tplink_crm_mobile/
├── main.py              # 主程序入口
├── config.py            # 配置文件
├── buildozer.spec       # 打包配置
├── screens/             # 屏幕层
│   ├── login_screen.py      # 登录屏幕
│   ├── main_screen.py       # 主屏幕（搜索）
│   ├── detail_screen.py     # 详情屏幕
│   └── inventory_screen.py  # 库存屏幕
├── services/            # 服务层
│   ├── auth_service.py      # 认证服务
│   ├── product_service.py   # 产品查询
│   ├── crawler_service.py   # 参数爬虫
│   └── cache_service.py     # 缓存服务
├── models/              # 数据模型
│   └── product.py           # 产品模型
├── utils/               # 工具类
│   └── price_utils.py       # 价格计算
└── assets/              # 资源文件
```

## 功能

- CRM系统登录认证
- 产品型号搜索
- 价格和折扣价格显示
- 库存查询
- 产品参数显示
- 停产产品过滤

## 注意事项

- APK 打包需要在 Linux 环境下进行
- Windows 用户可使用 WSL 或虚拟机
- 缓存文件存放在手机存储的 TPLinkCRM/data 目录
