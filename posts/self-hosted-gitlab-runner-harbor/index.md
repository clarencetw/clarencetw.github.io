---
title: "自架 GitLab、Runner 與 Harbor：從原始碼到部署的 CI/CD 流程"
url: "https://clarence.tw/posts/self-hosted-gitlab-runner-harbor/"
language: "zh-tw"
---

# 自架 GitLab、Runner 與 Harbor：從原始碼到部署的 CI/CD 流程

以維運者的角度整理 Self-hosted GitLab、GitLab Runner 與 Harbor registry：為什麼自架、各元件怎麼串起來，以及長期維運中的升級、備份、金鑰與 log 限制問題。

自 2022 年起，我以 Operator 的角色建置與維護 Self-hosted GitLab、GitLab Runner、Harbor registry 與 CI/CD workflow，把 source code、container image 與 deployment 串在同一條流程上。

這篇不是設定教學。`.gitlab-ci.yml`、Runner 部署與多環境部署的範例整理在 [GitLab CI/CD 完整配置指南](https://clarence.tw/posts/gitlab-cicd-complete-guide/)，`config.toml` 的設定項目與常用變數整理在 [GitLab Runner config.toml 設定與常用 CI/CD 變數](https://clarence.tw/notes/gitlab/runner-config/)。這裡想談的是另一面：為什麼要自己養這套系統、各元件怎麼接，以及跑了幾年之後真正花時間的地方。文中提到的問題，都附上我當時寫在 [blog.clarence.tw](https://blog.clarence.tw/) 的紀錄。

## 為什麼考慮自架

GitLab.com 與各家雲端 registry 都很成熟，自架不是預設答案。會走向自架，通常是下面幾個考量疊在一起：

- **資料與程式碼放在哪裡**：有些團隊需要原始碼、image 與 build log 留在自己能控制的環境。
- **網路環境**：deployment target 在地端或內部網路時，Runner 與 registry 放在同一側，build 與 pull image 的路徑比較短，也比較好控管對外連線。
- **Runner 資源**：需要特定硬體、作業系統或較大的 build 資源時，自己的 Runner 比較好安排。
- **整合需求**：要和既有的帳號系統、監控與備份流程接在一起。

代價也很清楚：升級、備份、憑證、金鑰、磁碟空間與故障排除都變成自己的事。決定自架之前，要先確定有人願意長期承擔這些工作。

## 整體流向

整條流程可以用一句話描述：程式碼進 GitLab，Runner 依照 pipeline build 與測試，產出的 container image 推到 Harbor，部署環境再從 Harbor 拉 image。

1. **Source**：開發者 push commit 或 tag 到 GitLab，觸發 pipeline。
2. **CI**：GitLab 把 job 派給符合 tags 的 Runner，執行測試與 image build。
3. **Image**：build 完成的 image 依照 tag 規則推到 Harbor 對應的 project。
4. **Deploy**：部署環境用只有 pull 權限的帳號從 Harbor 拉指定版本的 image。

這樣切的好處是每一段的責任清楚。pipeline 失敗時，可以先判斷是 source、build、push 還是 deploy 出問題，而不是整條鏈一起猜。

Registry 也不一定只有一個。2021 年我寫過一篇用 [Jib 與 Gradle 在 GitLab CI 把 image 同時推到 GitLab Container Registry、Azure Container Registry 與 Amazon ECR](https://blog.clarence.tw/2021/07/25/java-jib-gradle-uses-gitlab-ci-cd-to-automatically-upload-docker-to-gitlab-container-registry-azure-container-registry-and-amazon-elastic-container-registry/) 的紀錄，當時為了 ECR 的登入流程，還另外做了一個帶 AWS CLI 與 credential helper 的 build image。每多一個 registry，就多一組認證方式與失效的可能。

## Runner 的配置策略

Runner 是 CI/CD 裡最常被調整的一塊。規劃時有幾個通用原則：

- **用 tags 分流**：不同類型的 job（一般 build、需要 Docker 的 job、特殊環境）交給不同 Runner，避免互相搶資源。
- **權限最小化**：`privileged` 與掛載 Docker socket 都等於把主機權限交給 job，只開給確實需要且可信任的 project。
- **設定檔視為重要資產**：`config.toml` 裡有 runner token，修改前先備份，不要寫進 repository。

Runner 的版本與 helper image 也會出問題。2020 年我在 `docker-windows` executor 上遇到 [Missing gitlab-runner-helper、artifacts 無法上傳的錯誤](https://blog.clarence.tw/2020/02/09/windows-gitlab-runner-in-docker-windows-missing-error-uploading-artifacts-is-disabled-or-missing-gitlab-runner-helper-uploading-artifacts-is-disabled-who-to-fix/)，最後是在 `config.toml` 指定 `helper_image` 才解決。具體的設定項目與風險說明請參考上面連結的 Runner 筆記。

## Harbor 與映像檔管理

### Robot account 與 CI 認證

CI 推 image 到 Harbor 時，我會用 Harbor 的 robot account，而不是個人帳號。依照 [Harbor 文件](https://goharbor.io/docs/2.13.0/working-with-projects/project-configuration/create-robot-accounts/)，project robot account 只能在所屬 project 內動作，權限在建立時選定，也可以設定到期時間。CI 用 push 權限、部署端只給 pull 權限，是比較好管理的切法。

Robot account 名稱預設帶有 `robot$` 前綴，這個 `$` 曾讓我卡了一段時間。2023 年我記錄過 [GitLab CI 整合 Harbor 時 docker login 一直回傳 unauthorized](https://blog.clarence.tw/2023/11/26/%e8%a7%a3%e6%b1%ba%e4%bd%bf%e7%94%a8-gitlab-ci-%e6%95%b4%e5%90%88-harbor-%e5%87%ba%e7%8f%be%e7%9a%84%e5%a5%87%e6%80%aa%e5%95%8f%e9%a1%8c%ef%bc%9a%e5%b8%b3%e8%99%9f%e4%b8%ad%e7%9a%84-%e7%ac%a6/) 的問題：手動互動登入沒事，但在 pipeline 裡，`$` 被當成變數展開。當時的解法是在 `.gitlab-ci.yml` 寫成 `$$`，並改用 `--password-stdin` 傳密碼。依照 [GitLab CI/CD variables 文件](https://docs.gitlab.com/ci/variables/)，在 UI 設定的變數預設不會展開 `$` 參照，把帳號名稱也放進 CI/CD variable 是另一個可以考慮的做法。

### Tag 規則與空間管理

Image tag 要能對回原始碼。常見做法是 release 用版本號、其他 build 用 commit SHA。2020 年我記錄過一個小需求：[把 Git tag 的 `v1.0.0` 轉成 image tag `1.0.0`](https://blog.clarence.tw/2020/11/10/gitlab-ci-docker-tag-removal-version-v/)，用 shell 的 `${CI_COMMIT_TAG:1}` 去掉第一個字元。規則不複雜，但要一開始就定好，之後所有 project 都照同一套走。

Image 只會越堆越多，Harbor 提供幾個工具可以管理：

- **Tag retention**：依 repository、數量或時間保留需要的 tag，其餘清掉。官方文件建議先 dry run，因為執行後無法復原。
- **Tag immutability**：讓 release tag 不能被覆寫，確保同一個版本號永遠指向同一個 image。
- **Garbage collection**：刪掉 tag 或 artifact 不會立刻釋放空間，要跑 [garbage collection](https://goharbor.io/docs/2.13.0/administration/garbage-collection/) 才會清掉沒有被引用的 blob。

## 長期維運：升級、備份、金鑰與 log 限制

系統架好只是開始，真正花時間的是之後幾年的維護。以下是我在部落格上留下紀錄的幾類問題。

### 升級：不能跳過必經版本

2023 年我記錄過 [GitLab 從 14.9.3 升級](https://blog.clarence.tw/2023/12/24/gitlab-%e4%bc%ba%e6%9c%8d%e5%99%a8%e5%8d%87%e7%b4%9a%e6%8c%87%e5%8d%97%ef%bc%9a%e5%be%9e%e7%89%88%e6%9c%ac-14-9-3-%e5%8d%87%e7%b4%9a/) 的過程。直接用 apt 升級時，套件的 preinstall 檢查會擋下來，要求先升到 14.10.x。解法是用 `apt install gitlab-ce=<版本>` 一站一站往上升，每站重啟並確認服務正常。

這件事的教訓是：GitLab 越久沒升，要走的路越長。依照 [GitLab upgrade paths 文件](https://docs.gitlab.com/update/upgrade_paths/)，required upgrade stops 不能跳過，每一站要升到最新 patch，並等 background migrations 跑完再繼續；官方也提供 Upgrade Path tool 計算需要經過的版本。定期小步升級，比幾年一次大升級安全得多。

### 備份：分清楚備份的是什麼

2023 年我寫過一個 [用 GitLab API 把帳號下所有 project clone 下來的 Bash 腳本](https://blog.clarence.tw/2023/11/12/%e5%a6%82%e4%bd%95%e5%82%99%e4%bb%bd%e6%95%b4%e5%80%8b-gitlab-%e6%89%80%e6%9c%89%e5%b0%88%e6%a1%88/)，起因是同事需要一次取得所有 repository。這類腳本適合拿來搬移或保留一份程式碼副本，但它只有 Git repository，不包含 issue、merge request、CI/CD 設定等資料。

完整的 GitLab 備份仍要靠官方的備份流程。另外，依照 [GitLab 備份文件](https://docs.gitlab.com/administration/backup_restore/backup_gitlab/)，備份任務不會包含設定檔，Linux package 安裝至少要另外備份 `/etc/gitlab/gitlab-secrets.json` 與 `/etc/gitlab/gitlab.rb`，而且不要和資料備份放在一起。少了 secrets 檔，資料庫裡加密的資料就無法還原。

### 套件金鑰：一定會過期

用 apt 安裝 GitLab 與 Runner，就要面對套件庫簽章金鑰的更替。我遇過兩次：

- 2020 年 [`apt update` 出現 `NO_PUBKEY`](https://blog.clarence.tw/2020/04/21/gitlab-gpg-key-update/)，需要匯入新的 GitLab GPG key。
- 2022 年在 Ubuntu 18.04 更新 Runner 時 [出現 `EXPKEYSIG`，金鑰已過期](https://blog.clarence.tw/2022/09/11/ubuntu-18-04-lts-gitlab-%e9%87%91%e9%91%b0%e9%81%8e%e6%9c%9f%e8%99%95%e7%90%86%e6%96%b9%e6%b3%95/)，需要重新下載並匯入。

這類問題不會讓服務立刻掛掉，但會讓升級默默失敗。當時文章用的 `apt-key` 在較新的 Debian / Ubuntu 已不建議使用，現在處理時應以 GitLab 官方文件當下的做法為準。

### Log 限制：預設 4 MB

2022 年我遇過 [Runner 出現 `Job's log exceeded limit of 4194304 bytes`](https://blog.clarence.tw/2022/11/27/gitlab-runner-%e5%87%ba%e7%8f%be-jobs-log-exceeded-limit-of-4194304-bytes-%e7%9a%84%e8%a7%a3%e6%b3%95/)。依照 [Runner advanced configuration](https://docs.gitlab.com/runner/configuration/advanced-configuration/)，`[[runners]]` 的 `output_limit` 預設是 4096 KB。調高這個值可以讓 job 繼續跑，但更根本的做法是檢查為什麼 log 這麼多，例如關掉不必要的 verbose 輸出。

## 學到的事

- **自架的成本在後面**：安裝只花一次時間，升級、備份、金鑰與空間管理是每年都要做的事，要排進固定的維運節奏。
- **把每一段的邊界切清楚**：source、CI、image、deploy 各自有負責的元件與權限，出問題時才能快速定位。
- **帳號與權限要為自動化設計**：CI 用 robot account、部署端只給 pull，比共用個人帳號好管理，也比較容易輪替。
- **把踩過的坑寫下來**：上面每一個問題，下次遇到時最快的解法都是自己當時留下的紀錄。
