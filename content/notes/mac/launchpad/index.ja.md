---
title: macOS 管理コマンド
description: macOS Launchpad、Dock、Finder、screenshot、system inspection のコマンド。
weight: 210
menu:
  notes:
    name: macOS コマンド
    identifier: notes-mac-commands
    parent: notes-mac
    weight: 10
---

{{< note title="Launchpad と Dock" >}}

```bash
defaults write com.apple.dock ResetLaunchPad -bool true
killall Dock

defaults write com.apple.dock autohide -bool true
defaults write com.apple.dock tilesize -int 50
killall Dock
```

Dock の変更は、多くの場合 `killall Dock` 後に反映される。

{{< /note >}}

{{< note title="Finder と screenshots" >}}

```bash
defaults write com.apple.finder AppleShowAllFiles -bool true
defaults write NSGlobalDomain AppleShowAllExtensions -bool true
killall Finder

defaults write com.apple.screencapture location ~/Desktop/Screenshots
defaults write com.apple.screencapture type -string "png"
killall SystemUIServer
```

screenshot location を変更する前に target folder を作成する。

{{< /note >}}

{{< note title="System と network checks" >}}

```bash
sw_vers
system_profiler SPHardwareDataType
sysctl -n machdep.cpu.brand_string
df -h
networksetup -listallhardwareports
networksetup -getinfo "Wi-Fi"
```

troubleshooting や migration 前の Mac 記録に使える。

{{< /note >}}
