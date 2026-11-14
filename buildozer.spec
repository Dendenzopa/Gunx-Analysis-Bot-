[app]

# Jina la App yako litakavyoonekana kwenye simu
title = GUNX ANALYSIS BOT

# Jina la kifurushi (package)
package.name = gunxanalysisbot
package.domain = org.gunx

# Folda yenye vyanzo vya programu yako
source.dir = .

# Aina za mafaili yatakayojumuishwa kwenye APK
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt

# Toleo la App yako
version = 1.0.0

# MAHUHUSIO YA MAKTABA (Requirements zilizoongezwa kwa ajili ya api.py na markets.py)
requirements = python3,kivy==2.3.1,requests,certifi,urllib3

# Mwelekeo wa skrini (Portrait = Inayosimama)
orientation = portrait
fullscreen = 0

# Ruhusa za simu (INTERNET ni lazima kwa ajili ya API na market analysis)
android.permissions = INTERNET

# Mapangilio ya Android SDK na NDK
android.api = 31
android.minapi = 28
android.ndk = 25b
android.archs = arm64-v8a

# Tawi la Python-for-Android linalounga mkono Python 3.11
p4a.branch = develop

[buildozer]
# Kiwango cha ukataji wa magogo (log level 2 kwa ajili ya kuona makosa vizuri)
log_level = 2
warn_on_root = 1
