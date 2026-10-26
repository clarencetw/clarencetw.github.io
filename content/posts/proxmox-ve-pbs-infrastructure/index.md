---
title: Proxmox VE 與 PBS：中小型 On-prem 基礎設施的規劃與備份策略
date: 2026-10-26T00:00:00+08:00
description: 整理我規劃與維運 Proxmox VE、Proxmox Backup Server 與 GPU server 的思路，包含叢集、儲存、網路原則、備份策略，以及維運時踩過的坑。
menu:
  sidebar:
    name: Proxmox VE 與 PBS
    identifier: proxmox-ve-pbs-infrastructure
    weight: 50
tags: ["Proxmox", "Backup", "Infrastructure", "GPU", "On-prem"]
categories: ["Portfolio", "Engineering"]
---

自 2023 年起，我以 Operator 的角色規劃與維運 Proxmox VE、Proxmox Backup Server（PBS）、GPU server 與 On-prem infrastructure，承載 internal services、AI runtime workload，並負責整體的 backup strategy。

這篇不是安裝教學，而是整理我在這類中小型地端環境裡比較在意的規劃原則，以及維運時實際踩過、也在 [blog](https://blog.clarence.tw/) 記錄過的問題。文中不會提到任何主機名稱、IP、網段配置或資安細節；涉及設定建議的地方，都是一般性的做法，並以 Proxmox 官方文件為準。

## 背景與需求

地端環境的需求通常很實際：有一批 internal services 要長期穩定運作，有 AI workload 需要 GPU，還有資料必須能備份、能還原。預算與人力有限，所以選擇的平台要能讓少數人就維護得動。

Proxmox VE 適合這種情境：VM 與 LXC container 可以在同一個介面管理，cluster、storage、backup 都有內建的做法，搭配 PBS 就能有 incremental、deduplicated 的備份。對我來說，重點不是「功能最多」，而是「出事時能不能快速查、快速救」。

我在這個範圍內負責的工作包含：

- 設計與維運 Proxmox VE cluster、virtualization、storage 與 VM lifecycle。
- 建置 Proxmox Backup Server，規劃 backup、restore 與 disaster recovery 流程。
- 管理 NVIDIA GPU server、driver / runtime、inference environment 與系統調校。
- 評估 Dell、HP、Supermicro server hardware 與 GPU server 規格，整理成可採購、可維運的技術規格。
- 規劃內外部機房、site-to-site backup 與 high availability 路徑，並用 LibreNMS 做 network / server monitoring。

## 規劃重點：叢集、儲存與網路

### 叢集

Cluster 的價值在於集中管理與 VM 搬移，但它也帶來 quorum 的問題。依照 [Proxmox VE 官方文件](https://pve.proxmox.com/pve-docs/chapter-pvecm.html)，如果要用 High Availability，至少需要三個節點才能有可靠的 quorum；只有兩個節點時，可以用 QDevice 補第三票。

另外幾個我會先確認的事：

- **節點版本一致**：官方建議 cluster 內所有節點維持相同版本，升級要有計畫地一台一台做。
- **CPU 相容性**：官方文件提到 online migration 只在相同 CPU vendor 之間保證可行；硬體不一致時，VM 的 CPU model 要選得保守一點，否則 live migration 可能失敗。
- **節點生命週期**：加入、汰換、移除節點都要有固定流程，不要臨場發揮。

### 儲存

儲存規劃的原則是「把會長大的東西和系統分開」。VM disk、ISO / template、備份資料各自有適合放的位置，備份資料尤其不要和 hypervisor 的系統碟擠在同一個空間，否則某一邊爆量就會連帶影響另一邊。

VM 的 disk 也要預期會成長。在 Proxmox 上擴充磁碟本身不難，但要記得 hypervisor 端 resize 之後，guest OS 裡的 partition、LVM 與 filesystem 也要跟著調整。這個流程我在 blog 整理過 [Ubuntu 22.04 VM 的完整步驟](https://blog.clarence.tw/2024/08/04/%e5%9c%a8-proxmox-ve-%e4%b8%ad%e6%93%b4%e5%b1%95-ubuntu-22-04-%e8%99%9b%e6%93%ac%e6%a9%9f%e7%9a%84%e7%a3%81%e7%a2%9f%e7%a9%ba%e9%96%93/)。

### 網路

Cluster 通訊使用 Corosync，對延遲很敏感，但不太吃頻寬。官方建議給 cluster traffic 一張專用的實體網卡，並在另一個實體網路上準備第二條 link 作為備援，避免 VM 流量或備份流量把 Corosync 擠掉。

一般性的原則是把管理、cluster、VM 與備份流量分開規劃，並在一開始就決定好位址規劃，因為之後要改 cluster 的通訊位址，成本會比想像中高（後面「踩過的坑」會提到）。

## GPU Server 與 AI Workload

AI runtime 對 GPU、driver、CUDA 版本與 kernel 都很敏感，所以 GPU server 的維運重點是「環境可以被重建」，而不是某台機器剛好能跑。

在 Proxmox 上使用 GPU，常見做法是 PCI(e) passthrough。[官方文件](https://pve.proxmox.com/pve-docs/chapter-qm.html)提到幾個要先想清楚的取捨：

- 硬體與 BIOS / UEFI 要支援並啟用 IOMMU。
- GPU passthrough 給某台 VM 之後，host 和其他 VM 就不能再使用那張卡。
- 有 passthrough PCI 裝置的 VM 目前不能 live migration，因此維護節點時要預先安排停機時間。

因為這些限制，GPU workload 適合用「整台規劃」的角度思考：哪些服務要獨佔 GPU、driver 與 runtime 怎麼版本化、主機維護時服務要怎麼停與怎麼回來。

Driver 問題是 GPU 維運最常遇到的。我在 blog 記錄過 [`nvidia-smi` 出現 No devices were found](https://blog.clarence.tw/2024/02/19/%e8%a7%a3%e6%b1%ba-nvidia-linux-%e4%bd%bf%e7%94%a8-nvidia-smi-%e5%87%ba%e7%8f%be-no-devices-were-found-%e5%95%8f%e9%a1%8c/) 的處理方式，以及 [Ubuntu 24.04 在 Secure Boot 環境下 NVIDIA 驅動無法載入](https://blog.clarence.tw/2026/01/31/%e8%a7%a3%e6%b1%ba-ubuntu-24-04-secure-boot-%e7%92%b0%e5%a2%83%e4%b8%8b-nvidia-%e9%a9%85%e5%8b%95%e7%84%a1%e6%b3%95%e8%bc%89%e5%85%a5%e5%95%8f%e9%a1%8c/) 的解法。這類問題的共通點是：先確認 kernel、driver、Secure Boot 與編譯環境的關係，再決定怎麼修，而不是一直重裝。

## Proxmox Backup Server 備份策略

備份策略我會分成四件事看：備份、保留、清理、驗證，最後再加上還原演練。

### Prune 與 Garbage Collection 是兩件事

這是 PBS 最容易誤解的地方。依照 [PBS 官方文件](https://pbs.proxmox.com/docs/maintenance.html)：

- **Prune** 只會移除 snapshot 的 metadata（manifest、index 等），實際資料所在的 chunk 不會立刻消失。
- **Garbage Collection（GC）** 才會真正刪除不再被任何 snapshot 參考的 chunk。GC 分成 mark 與 sweep 兩個階段，而且有一段寬限時間（預設約 24 小時 5 分鐘），所以剛 prune 完、馬上跑 GC，空間不一定會立刻釋放。

所以保留政策（`keep-last`、`keep-daily`、`keep-weekly` 等）和 GC 排程要一起設計。只設定 prune、沒有排 GC，空間會一直長；只看 GC 而保留政策太寬，空間一樣會不夠。

### 空間要預留，不要等到 100%

我在 blog 記錄過 [PBS 硬碟空間滿到 100%](https://blog.clarence.tw/2024/05/29/%e5%a6%82%e4%bd%95%e8%99%95%e7%90%86-proxmox-backup-server-%e7%a1%ac%e7%a2%9f%e7%a9%ba%e9%96%93%e6%bb%bf-100-%e7%9a%84%e5%95%8f%e9%a1%8c/) 的處理過程。當時的困境是：GC 需要一點空間才能執行，但空間已經完全用完。最後是先清掉超過 90 天的舊 task log，釋放出一點空間，再手動執行 GC。

這次經驗讓我更重視幾件事：

- 用 monitoring 盯 datastore 使用率，在還有餘裕時就處理，而不是等到寫不進去。
- 讓 datastore 和 PBS 系統本身的空間盡量分開，避免備份資料把系統擠爆。
- 定期檢查 prune 與 GC job 是否真的有在跑、有沒有失敗。

### Verify 與還原演練

備份成功不等於可以還原。PBS 官方文件建議設定 verify job，並且至少每個月重新驗證一次所有備份，因為硬碟老化可能讓原本正常的備份慢慢損壞（bit rot）。比較好的做法是：頻繁的 verify job 檢查新的備份，再搭配每週或每月一次的完整 re-verify。

除了 verify，還需要真正的還原演練：定期挑幾台 VM 或 container 還原到測試環境，確認開得起來、服務能跑、資料是預期的版本。Proxmox VE 也提供 live-restore 與 single file restore，適合在演練時一起確認流程。

### Off-site 與 disaster recovery

只有一份備份放在同一個機房，遇到整個站點出問題時就不夠。PBS 可以透過 remote 與 sync job 把備份同步到另一台 PBS，作為 site-to-site backup 的基礎。重點是要把「另一個站點的備份怎麼還原、還原到哪裡」也寫進 disaster recovery 流程，而不是只有資料在那裡。

## 維運踩過的坑

以下每一項都是我在 blog 上公開記錄過的問題，這裡只摘要重點與學到的事。

### 變更 Cluster 通訊 IP

我在 blog 記錄過 [Proxmox VE Cluster IP 更新與配置同步](https://blog.clarence.tw/2025/03/19/proxmox-ve-cluster-ip-%e6%9b%b4%e6%96%b0%e8%88%87%e9%85%8d%e7%bd%ae%e5%90%8c%e6%ad%a5%e7%b6%93%e9%a9%97%e8%ab%87/) 的過程。重點是要修改 cluster 共享的 `/etc/pve/corosync.conf`，而不是單一節點上的 `/etc/corosync/corosync.conf`；改之前先備份，改的時候要遞增 `config_version`，各節點的網卡設定與 `/etc/hosts` 也要同步更新，最後用 `pvecm status` 確認設定已經套用。這類操作會影響 quorum，屬於高風險變更，要排在維護時段做。

### 從叢集移除節點

節點汰換時，我在 blog 整理過 [如何從 Proxmox VE 叢集中安全移除節點](https://blog.clarence.tw/2025/04/12/%e5%a6%82%e4%bd%95%e5%be%9e-proxmox-ve-%e5%8f%a2%e9%9b%86%e4%b8%ad%e5%ae%89%e5%85%a8%e7%a7%bb%e9%99%a4%e7%af%80%e9%bb%9e/)：先備份或遷移該節點上的 VM 與 container，關機並確認它不會自動開回來，再用 `pvecm delnode` 移除，最後清掉殘留的節點目錄與 SSH key 資訊。官方文件也特別強調，被移除的節點不能用原本的設定再接回同一個 cluster 網路，否則可能把 cluster 弄壞。

### 網卡 firmware 錯誤

我在 blog 記錄過一台 Proxmox VE 主機的 [Intel X550 一直出現 ixgbe FWSM firmware error](https://blog.clarence.tw/2026/06/25/%e8%a7%a3%e6%b1%ba-proxmox-debian-%e4%b8%8a-intel-x550-ixgbe-fwsm-firmware-error-%e5%95%8f%e9%a1%8c/)。封包 counters 看起來都正常，更新 kernel 也沒有解，最後是更新網卡 NVM 並做真正的 power cycle 才消失。學到的是：driver 從硬體讀到的 firmware 警告不要用過濾 log 的方式處理；刷 firmware 前要先做 inventory、確認版本對應，並準備好 BMC / IPMI 或實體 console。

### VM 與 container 的修復

- **Windows VM 開不了機**：我在 blog 記錄過 [在 PVE 上用 WinPE 修復 Windows VM](https://blog.clarence.tw/2025/10/01/%e5%9c%a8-proxmox-ve%ef%bc%88pve%ef%bc%89windows-vm-%e4%bf%ae%e5%be%a9%e6%95%99%e5%ad%b8%ef%bc%9awinpe-%e4%b8%8b-sfc-scannow%e3%80%81dism-online-%e5%a4%b1%e6%95%88%ef%bc%9f%e7%94%a8-drvload/)。關鍵是 WinPE 預設不一定有 VirtIO 驅動，要先用 `drvload` 載入，才看得到系統磁碟，再用離線 DISM 修復。
- **LXC 使用 IPv6**：我在 blog 記錄過 [讓 PVE 上的 LXC container 使用 IPv6](https://blog.clarence.tw/2023/02/24/proxmox-ve-pve-%e4%bd%bf%e7%94%a8-linux-container-lxc-%e5%ae%b9%e5%99%a8%e4%bd%bf%e7%94%a8-ipv6/) 時需要調整 host 的 `accept_ra` 設定。
- **Web UI 憑證換錯**：我在 blog 記錄過 [PVE 出現 Connection error 596](https://blog.clarence.tw/2023/01/15/pve-%e5%87%ba%e7%8f%be-connection-error-596-broken-pipe-%e7%9a%84%e8%a7%a3%e6%b1%ba%e6%96%b9%e6%b3%95/)，原因是換了不正確的憑證，要從 SSH 進去把 pveproxy 的憑證檔換回正確的。

### 舊硬體與硬體監控

我在 blog 記錄過 [在 HP ProLiant DL380 G6 安裝 PVE 或 PBS 時畫面出現條紋](https://blog.clarence.tw/2023/04/30/hp-proliant-dl380-g6-%e5%9c%a8%e5%ae%89%e8%a3%9d-proxmox-ve-pve-%e6%88%96-proxmox-backup-server-pbs-%e6%99%82%e5%87%ba%e7%8f%be%e9%bb%91%e7%99%bd%e6%a2%9d%e7%b4%8b%e5%a6%82%e4%bd%95%e8%a7%a3/) 的解法，也記錄過 [在 Proxmox 安裝 HPE Agentless Management](https://blog.clarence.tw/2023/01/22/%e5%9c%a8-proxmox-%e5%ae%89%e8%a3%9d-hpe-agentless-management-ams/)，讓 iLO 能讀到主機狀態。舊世代硬體可以延長使用，但要預期安裝與監控工具的支援會越來越少，汰換計畫要提早排。

### 升級前的檢查

我在 blog 整理過 [Proxmox VE 9.2 幾個比較重要的新功能](https://blog.clarence.tw/2026/05/21/proxmox-ve-9-2-%e5%b9%be%e5%80%8b%e6%88%91%e8%a6%ba%e5%be%97%e6%af%94%e8%bc%83%e9%87%8d%e8%a6%81%e7%9a%84%e6%96%b0%e5%8a%9f%e8%83%bd/)，例如 HA disarm / arm、CRS 動態負載平衡與 Custom CPU Models GUI。不論是哪一版，正式環境升級前我都會先確認：備份是否完整、kernel / driver 相容性、HA 與 migration 行為，以及網路設定有沒有受到影響，並優先在測試環境或非核心節點驗證。

## 學到的事

- **備份要以「能還原」為目標**：prune、GC、verify 與還原演練缺一不可，只看備份 job 成功是不夠的。
- **空間與容量要提前監控**：PBS 滿到 100% 時，連清理工具都很難執行，預留空間比事後救火便宜很多。
- **Cluster 的變更都是高風險操作**：改 IP、移除節點、升級，都要先備份設定、照文件流程走，並排在維護時段。
- **把踩過的坑寫下來**：上面每一個問題，下次再遇到時都能直接查自己的紀錄，這也是我持續寫 [blog](https://blog.clarence.tw/) 的原因。
