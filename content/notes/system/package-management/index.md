---
title: 套件管理指令
weight: 310
menu:
  notes:
    name: Package Management
    identifier: notes-system-package
    parent: notes-system
    weight: 10
---

<!-- Homebrew 安裝與使用 -->
{{< note title="Homebrew (macOS)" >}}

**安裝 Homebrew：**
```bash
# 安裝 Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 設定環境變數 (Apple Silicon Mac)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc

# 設定環境變數 (Intel Mac)
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc
```

**常用指令：**
```bash
# 安裝套件
brew install git
brew install node
brew install docker
brew install hugo

# 安裝 GUI 應用程式
brew install --cask visual-studio-code
brew install --cask docker
brew install --cask google-chrome

# 更新套件
brew update          # 更新 Homebrew 本身
brew upgrade         # 更新所有套件
brew upgrade git     # 更新特定套件

# 搜尋套件
brew search nginx
brew search --cask chrome

# 查看已安裝套件
brew list
brew list --cask

# 移除套件
brew uninstall git
brew uninstall --cask docker

# 清理舊版本
brew cleanup
brew cleanup git

# 查看套件資訊
brew info git
brew deps git        # 查看相依性
```

{{< /note >}}

<!-- APT 套件管理 (Ubuntu/Debian) -->
{{< note title="APT (Ubuntu/Debian)" >}}

**更新套件清單：**
```bash
# 更新套件清單
sudo apt update

# 升級所有套件
sudo apt upgrade

# 升級系統 (包含核心)
sudo apt full-upgrade

# 更新並升級 (一次完成)
sudo apt update && sudo apt upgrade -y
```

**安裝套件：**
```bash
# 安裝單一套件
sudo apt install git
sudo apt install nginx
sudo apt install docker.io

# 安裝多個套件
sudo apt install git curl wget vim

# 安裝特定版本
sudo apt install nginx=1.18.0-0ubuntu1

# 從 .deb 檔案安裝
sudo dpkg -i package.deb
sudo apt install -f  # 修復相依性問題
```

**移除套件：**
```bash
# 移除套件 (保留設定檔)
sudo apt remove nginx

# 完全移除套件 (包含設定檔)
sudo apt purge nginx

# 移除不需要的相依套件
sudo apt autoremove

# 移除並清理
sudo apt remove nginx && sudo apt autoremove
```

**搜尋與查詢：**
```bash
# 搜尋套件
apt search nginx
apt search "web server"

# 查看套件資訊
apt show nginx
apt info docker.io

# 查看已安裝套件
apt list --installed
apt list --installed | grep nginx

# 查看可升級套件
apt list --upgradable

# 查看套件相依性
apt depends nginx
apt rdepends nginx  # 反向相依性
```

**清理系統：**
```bash
# 清理下載的套件檔案
sudo apt clean

# 清理部分快取
sudo apt autoclean

# 修復損壞的套件
sudo apt install -f

# 重新設定套件
sudo dpkg-reconfigure package-name
```

{{< /note >}}

<!-- YUM/DNF (CentOS/RHEL/Fedora) -->
{{< note title="YUM/DNF (CentOS/RHEL/Fedora)" >}}

**DNF (Fedora)：**
```bash
# 更新套件清單
sudo dnf check-update

# 升級所有套件
sudo dnf upgrade

# 安裝套件
sudo dnf install git
sudo dnf install nginx

# 移除套件
sudo dnf remove nginx

# 搜尋套件
dnf search nginx

# 查看套件資訊
dnf info nginx

# 查看已安裝套件
dnf list installed

# 清理快取
sudo dnf clean all
```

**YUM (CentOS 7)：**
```bash
# 更新套件
sudo yum update

# 安裝套件
sudo yum install git
sudo yum install epel-release  # EPEL 倉庫

# 移除套件
sudo yum remove nginx

# 搜尋套件
yum search nginx

# 查看套件資訊
yum info nginx

# 查看已安裝套件
yum list installed

# 清理快取
sudo yum clean all
```

{{< /note >}}

<!-- Snap 套件管理 -->
{{< note title="Snap (Universal Packages)" >}}

```bash
# 安裝 snapd (如果尚未安裝)
sudo apt install snapd

# 安裝 snap 套件
sudo snap install code --classic
sudo snap install docker
sudo snap install hugo

# 查看已安裝的 snap
snap list

# 更新 snap 套件
sudo snap refresh
sudo snap refresh code

# 移除 snap 套件
sudo snap remove code

# 搜尋 snap 套件
snap find "text editor"

# 查看 snap 資訊
snap info code

# 查看 snap 版本
snap version
```

{{< /note >}}

<!-- 常用開發工具安裝 -->
{{< note title="常用開發工具快速安裝" >}}

**Node.js 與 npm：**
```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS
brew install node

# 驗證安裝
node --version
npm --version
```

**Docker：**
```bash
# Ubuntu
sudo apt update
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt update
sudo apt install docker-ce

# macOS
brew install --cask docker

# 啟動 Docker 服務
sudo systemctl start docker
sudo systemctl enable docker

# 將使用者加入 docker 群組
sudo usermod -aG docker $USER
```

**Git：**
```bash
# Ubuntu/Debian
sudo apt install git

# macOS
brew install git

# 設定 Git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

**Hugo：**
```bash
# Ubuntu (從 GitHub 下載)
wget https://github.com/gohugoio/hugo/releases/download/v0.148.1/hugo_extended_0.148.1_linux-amd64.deb
sudo dpkg -i hugo_extended_0.148.1_linux-amd64.deb

# macOS
brew install hugo

# 驗證安裝
hugo version
```

{{< /note >}}