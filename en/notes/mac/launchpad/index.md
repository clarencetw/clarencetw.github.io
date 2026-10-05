---
title: "macOS Administration Commands"
url: "https://clarence.tw/en/notes/mac/launchpad/"
language: "en"
---

# macOS Administration Commands

macOS Launchpad, Dock, Finder, screenshot, and system inspection commands.

## Version and safety scope

**Last reviewed: July 11, 2026**

This is a general command reference, not a version-pinned runbook. Check the installed version, current official documentation, and the target account, host, and path before use. Commands that deploy, destroy, delete, prune, sync, upgrade, or change system settings can cause cost, downtime, or data loss; preview changes and back up where appropriate.

## Launchpad and Dock

```bash
defaults write com.apple.dock ResetLaunchPad -bool true
killall Dock

defaults write com.apple.dock autohide -bool true
defaults write com.apple.dock tilesize -int 50
killall Dock
```

Dock changes usually need `killall Dock` before they appear.

## Finder and screenshots

```bash
defaults write com.apple.finder AppleShowAllFiles -bool true
defaults write NSGlobalDomain AppleShowAllExtensions -bool true
killall Finder

defaults write com.apple.screencapture location ~/Desktop/Screenshots
defaults write com.apple.screencapture type -string "png"
killall SystemUIServer
```

Create the screenshot target folder before changing the screenshot location.

## System and network checks

```bash
sw_vers
system_profiler SPHardwareDataType
sysctl -n machdep.cpu.brand_string
df -h
networksetup -listallhardwareports
networksetup -getinfo "Wi-Fi"
```

These commands are useful when documenting a Mac before troubleshooting or migration.
