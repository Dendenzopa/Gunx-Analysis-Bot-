[app]

title = GUNX ANALYSIS BOT
package.name = gunxanalysisbot
package.domain = org.gunx

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt

version = 1.0.0

# Added network and security requirements needed for api.py and markets.py
requirements = python3,kivy==2.3.1,requests,certifi,urllib3

orientation = portrait
fullscreen = 0

android.permissions = INTERNET

android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

p4a.branch = develop

[buildozer]
log_level = 2
warn_on_root = 1
