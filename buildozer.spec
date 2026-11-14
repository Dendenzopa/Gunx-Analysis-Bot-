[app]

title = GUNX ANALYSIS BOT
package.name = gunxanalysisbot
package.domain = org.gunx

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json

version = 1.0.0

requirements = python3,kivy

orientation = portrait
fullscreen = 0

android.permissions = INTERNET

android.api = 35
android.minapi = 23

android.archs = arm64-v8a, armeabi-v7a

p4a.branch = master

[buildozer]

log_level = 2
warn_on_root = 1
