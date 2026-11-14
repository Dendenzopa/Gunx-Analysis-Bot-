
[app]

title = GUNX ANALYSIS BOT
package.name = gunxanalysisbot
package.domain = org.gunx

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt

version = 1.0.0

requirements = python3,kivy==2.3.1,requests,certifi,urllib3

orientation = portrait
fullscreen = 0

android.permissions = INTERNET

android.api = 31
android.minapi = 21
android.ndk = 28c
android.archs = arm64-v8a

android.accept_sdk_license = True

p4a.branch = develop

[buildozer]

log_level = 2
warn_on_root = 1
