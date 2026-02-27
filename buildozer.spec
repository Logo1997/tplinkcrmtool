[app]

title = TP-LINK CRM 产品查询

package.name = tplinkcrm

package.domain = com.tplink

source.dir = .

source.include_exts = py,png,jpg,kv,atlas,json,ttc,ttf

source.exclude_dirs = tests, bin, venv, __pycache__, .git, .github, data

version = 1.0.0

requirements = python3,kivy==2.3.0,requests,beautifulsoup4,lxml

p4a.branch = master

orientation = portrait

fullscreen = 0

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 33

android.minapi = 21

android.ndk = 25b

android.skip_update = False

android.accept_sdk_license = True

android.archs = arm64-v8a

android.allow_backup = True

android.release_artifact = aab

[buildozer]

log_level = 2

warn_on_root = 1
