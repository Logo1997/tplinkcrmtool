[app]

# (str) Title of your application
title = TP-LINK CRM 产品查询

# (str) Package name
package.name = tplinkcrm

# (str) Package domain (needed for android/ios packaging)
package.domain = com.tplink

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,ttc,ttf

# (list) Source files to exclude (let empty to exclude no files)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to exclude no files)
#source.exclude_dirs = tests, bin, venv

# (list) List of directory to include (let empty to exclude no files)
source.include_dirs = data, assets

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
requirements = python3,kivy,requests,beautifulsoup4,lxml

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/assets/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/assets/icon.png

# (str) Supported orientation (landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) If True, then skip trying to update the Android sdk
android.skip_update = False

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (str) The Android arch to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
