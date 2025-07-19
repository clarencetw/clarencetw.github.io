---
title: Mac 系統管理指令
weight: 210
menu:
  notes:
    name: Mac Commands
    identifier: notes-mac-commands
    parent: notes-mac
    weight: 10
---

<!-- Launchpad 管理 -->
{{< note title="Launchpad 管理" >}}

```bash
# 重置 Launchpad 排列
defaults write com.apple.dock ResetLaunchPad -bool true
killall Dock

# 設定 Launchpad 每頁顯示的 app 數量
# 設定每行顯示數量 (預設 7)
defaults write com.apple.dock springboard-columns -int 8
# 設定每列顯示數量 (預設 5)  
defaults write com.apple.dock springboard-rows -int 6
killall Dock

# 恢復預設設定
defaults delete com.apple.dock springboard-columns
defaults delete com.apple.dock springboard-rows
killall Dock
```

{{< /note >}}

<!-- Dock 設定 -->
{{< note title="Dock 設定" >}}

```bash
# 隱藏/顯示 Dock
defaults write com.apple.dock autohide -bool true
defaults write com.apple.dock autohide -bool false
killall Dock

# 設定 Dock 大小
defaults write com.apple.dock tilesize -int 50
killall Dock

# 設定 Dock 位置 (left, bottom, right)
defaults write com.apple.dock orientation -string "left"
killall Dock

# 移除 Dock 中所有 app (只保留 Finder 和垃圾桶)
defaults write com.apple.dock persistent-apps -array
killall Dock

# 顯示隱藏的 app 圖示 (半透明效果)
defaults write com.apple.dock showhidden -bool true
killall Dock

# 加快 Dock 動畫速度
defaults write com.apple.dock autohide-time-modifier -float 0.5
killall Dock
```

{{< /note >}}

<!-- Finder 設定 -->
{{< note title="Finder 設定" >}}

```bash
# 顯示隱藏檔案
defaults write com.apple.finder AppleShowAllFiles -bool true
killall Finder

# 隱藏隱藏檔案
defaults write com.apple.finder AppleShowAllFiles -bool false
killall Finder

# 顯示副檔名
defaults write NSGlobalDomain AppleShowAllExtensions -bool true
killall Finder

# 顯示路徑列
defaults write com.apple.finder ShowPathbar -bool true

# 顯示狀態列
defaults write com.apple.finder ShowStatusBar -bool true

# 設定預設檢視方式 (icnv=圖示, Nlsv=列表, clmv=欄位, Flwv=Cover Flow)
defaults write com.apple.finder FXPreferredViewStyle -string "Nlsv"

# 設定新 Finder 視窗開啟位置為家目錄
defaults write com.apple.finder NewWindowTarget -string "PfHm"

# 停用清空垃圾桶警告
defaults write com.apple.finder WarnOnEmptyTrash -bool false
```

{{< /note >}}

<!-- 截圖設定 -->
{{< note title="截圖設定" >}}

```bash
# 更改截圖儲存位置
defaults write com.apple.screencapture location ~/Desktop/Screenshots
killall SystemUIServer

# 更改截圖檔案格式 (png, jpg, gif, pdf, tiff)
defaults write com.apple.screencapture type -string "jpg"

# 移除截圖檔名中的陰影
defaults write com.apple.screencapture disable-shadow -bool true

# 截圖不顯示浮動縮圖
defaults write com.apple.screencapture show-thumbnail -bool false

# 截圖快捷鍵
# Cmd+Shift+3: 全螢幕截圖
# Cmd+Shift+4: 選取區域截圖  
# Cmd+Shift+4+Space: 視窗截圖
# Cmd+Shift+5: 截圖工具列
```

{{< /note >}}

<!-- 系統資訊查詢 -->
{{< note title="系統資訊查詢" >}}

```bash
# 查看 macOS 版本
sw_vers
sw_vers -productVersion

# 查看系統資訊
system_profiler SPSoftwareDataType
system_profiler SPHardwareDataType

# 查看 CPU 資訊
sysctl -n machdep.cpu.brand_string
sysctl -n hw.ncpu  # CPU 核心數

# 查看記憶體資訊
sysctl -n hw.memsize  # 總記憶體 (bytes)
vm_stat  # 記憶體使用統計

# 查看磁碟使用情況
df -h
diskutil list

# 查看網路介面
ifconfig
networksetup -listallhardwareports

# 查看已安裝的應用程式
ls /Applications
system_profiler SPApplicationsDataType
```

{{< /note >}}

<!-- 網路設定 -->
{{< note title="網路設定" >}}

```bash
# 查看網路設定
networksetup -listallhardwareports
networksetup -getinfo "Wi-Fi"

# 設定 DNS
sudo networksetup -setdnsservers "Wi-Fi" 8.8.8.8 1.1.1.1
sudo networksetup -setdnsservers "Wi-Fi" Empty  # 清除 DNS

# 重新整理 DNS 快取
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder

# 查看 Wi-Fi 密碼 (需要管理員密碼)
security find-generic-password -wa "WiFi名稱"

# 掃描 Wi-Fi 網路
/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s

# 連接 Wi-Fi
networksetup -setairportnetwork en0 "WiFi名稱" "密碼"
```

{{< /note >}}

<!-- 電源管理 -->
{{< note title="電源管理" >}}

```bash
# 查看電池資訊
pmset -g batt
system_profiler SPPowerDataType

# 查看電源設定
pmset -g

# 設定睡眠時間 (分鐘)
sudo pmset -a displaysleep 10  # 螢幕睡眠
sudo pmset -a sleep 30         # 系統睡眠

# 防止系統睡眠
caffeinate -d  # 防止螢幕睡眠
caffeinate -i  # 防止系統睡眠
caffeinate -s  # 防止系統睡眠 (AC 電源時)

# 立即睡眠
pmset sleepnow

# 查看睡眠/喚醒歷史
pmset -g log | grep -E "(Sleep|Wake)"
```

{{< /note >}}

<!-- 應用程式管理 -->
{{< note title="應用程式管理" >}}

```bash
# 強制結束應用程式
killall "應用程式名稱"
pkill -f "應用程式名稱"

# 查看運行中的程序
ps aux | grep "應用程式名稱"
top -o cpu  # 按 CPU 使用率排序

# 開啟應用程式
open -a "應用程式名稱"
open /Applications/Safari.app

# 開啟檔案 (使用預設應用程式)
open file.txt
open .  # 在 Finder 中開啟當前目錄

# 查看應用程式資訊
mdls /Applications/Safari.app
```

{{< /note >}}

<!-- 檔案系統操作 -->
{{< note title="檔案系統操作" >}}

```bash
# 顯示檔案/目錄的詳細資訊
ls -la@  # 包含擴展屬性
stat filename

# 查看檔案類型
file filename

# 建立符號連結
ln -s /path/to/original /path/to/link

# 查看目錄大小
du -sh /path/to/directory
du -h -d 1  # 只顯示一層深度

# 尋找檔案
find /path -name "*.txt"
mdfind "檔案名稱"  # 使用 Spotlight 搜尋

# 壓縮/解壓縮
zip -r archive.zip folder/
unzip archive.zip
tar -czf archive.tar.gz folder/
tar -xzf archive.tar.gz

# 計算檔案雜湊值
md5 filename
shasum -a 256 filename
```

{{< /note >}}

<!-- 系統維護 -->
{{< note title="系統維護" >}}

```bash
# 清理系統快取
sudo rm -rf ~/Library/Caches/*
sudo rm -rf /Library/Caches/*
sudo rm -rf /System/Library/Caches/*

# 重建 Spotlight 索引
sudo mdutil -E /

# 修復磁碟權限 (macOS 10.11 之前)
sudo diskutil repairPermissions /

# 驗證/修復磁碟
diskutil verifyVolume /
sudo diskutil repairVolume /

# 查看系統日誌
log show --predicate 'process == "kernel"' --last 1h
console  # 開啟 Console 應用程式

# 重置 NVRAM/PRAM
# 開機時按住 Option+Command+P+R

# 重置 SMC (系統管理控制器)
# MacBook: 關機後按住 Shift+Control+Option+電源鍵 10 秒
```

{{< /note >}}
