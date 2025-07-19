---
title: AWS CLI 基礎指令
weight: 120
menu:
  notes:
    name: AWS CLI
    identifier: notes-aws-cli
    parent: notes-aws
    weight: 20
---

<!-- AWS CLI 安裝與設定 -->
{{< note title="AWS CLI 安裝與設定" >}}

**安裝 AWS CLI：**
```bash
# macOS (使用 Homebrew)
brew install awscli

# Ubuntu/Debian
sudo apt update
sudo apt install awscli

# 使用 pip 安裝
pip install awscli

# 安裝 AWS CLI v2 (推薦)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# 驗證安裝
aws --version
```

**設定 AWS CLI：**
```bash
# 基本設定
aws configure
# 會提示輸入：
# AWS Access Key ID
# AWS Secret Access Key  
# Default region name (例如: us-east-1)
# Default output format (json/text/table)

# 設定特定 profile
aws configure --profile myprofile

# 查看設定
aws configure list
aws configure list --profile myprofile

# 設定單一參數
aws configure set region ap-northeast-1
aws configure set output json --profile myprofile
```

**環境變數設定：**
```bash
# 設定環境變數
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
export AWS_PROFILE=myprofile

# 查看當前設定
aws sts get-caller-identity
```

{{< /note >}}

<!-- S3 基本操作 -->
{{< note title="S3 基本操作" >}}

**Bucket 管理：**
```bash
# 列出所有 buckets
aws s3 ls

# 建立 bucket
aws s3 mb s3://my-bucket-name
aws s3 mb s3://my-bucket-name --region ap-northeast-1

# 刪除空的 bucket
aws s3 rb s3://my-bucket-name

# 刪除 bucket 及所有內容
aws s3 rb s3://my-bucket-name --force

# 查看 bucket 內容
aws s3 ls s3://my-bucket-name
aws s3 ls s3://my-bucket-name/folder/ --recursive
```

**檔案上傳與下載：**
```bash
# 上傳單一檔案
aws s3 cp file.txt s3://my-bucket-name/
aws s3 cp file.txt s3://my-bucket-name/folder/

# 下載單一檔案
aws s3 cp s3://my-bucket-name/file.txt ./
aws s3 cp s3://my-bucket-name/folder/file.txt ./downloads/

# 上傳整個目錄
aws s3 cp ./local-folder s3://my-bucket-name/remote-folder --recursive

# 下載整個目錄
aws s3 cp s3://my-bucket-name/remote-folder ./local-folder --recursive

# 同步目錄 (只上傳變更的檔案)
aws s3 sync ./local-folder s3://my-bucket-name/remote-folder
aws s3 sync s3://my-bucket-name/remote-folder ./local-folder

# 移動檔案
aws s3 mv file.txt s3://my-bucket-name/
aws s3 mv s3://my-bucket-name/old-file.txt s3://my-bucket-name/new-file.txt
```

{{< /note >}}

<!-- S3 進階操作 -->
{{< note title="S3 進階操作" >}}

**檔案管理：**
```bash
# 刪除檔案
aws s3 rm s3://my-bucket-name/file.txt

# 刪除目錄及所有內容
aws s3 rm s3://my-bucket-name/folder --recursive

# 設定檔案權限 (ACL)
aws s3 cp file.txt s3://my-bucket-name/ --acl public-read
aws s3 cp file.txt s3://my-bucket-name/ --acl private

# 設定 Content-Type
aws s3 cp index.html s3://my-bucket-name/ --content-type "text/html"

# 設定快取控制
aws s3 cp image.jpg s3://my-bucket-name/ --cache-control "max-age=3600"

# 設定 metadata
aws s3 cp file.txt s3://my-bucket-name/ --metadata "key1=value1,key2=value2"
```

**過濾與排除：**
```bash
# 只同步特定檔案類型
aws s3 sync ./folder s3://my-bucket-name/ --include "*.jpg"

# 排除特定檔案
aws s3 sync ./folder s3://my-bucket-name/ --exclude "*.tmp"

# 複合條件
aws s3 sync ./folder s3://my-bucket-name/ --exclude "*" --include "*.jpg" --include "*.png"

# 刪除本地不存在的檔案
aws s3 sync ./folder s3://my-bucket-name/ --delete
```

**檔案資訊查詢：**
```bash
# 查看檔案詳細資訊
aws s3api head-object --bucket my-bucket-name --key file.txt

# 查看檔案大小和數量
aws s3 ls s3://my-bucket-name --recursive --human-readable --summarize

# 查看特定前綴的檔案
aws s3 ls s3://my-bucket-name/logs/ --recursive
```

{{< /note >}}

<!-- S3 網站託管 -->
{{< note title="S3 靜態網站託管" >}}

```bash
# 啟用靜態網站託管
aws s3 website s3://my-bucket-name --index-document index.html --error-document error.html

# 上傳網站檔案並設定公開讀取
aws s3 sync ./website s3://my-bucket-name --acl public-read

# 設定 bucket policy (允許公開讀取)
cat > bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::my-bucket-name/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy --bucket my-bucket-name --policy file://bucket-policy.json

# 查看網站設定
aws s3api get-bucket-website --bucket my-bucket-name

# 停用網站託管
aws s3api delete-bucket-website --bucket my-bucket-name
```

{{< /note >}}

<!-- S3 生命週期管理 -->
{{< note title="S3 生命週期管理" >}}

```bash
# 建立生命週期規則
cat > lifecycle.json << EOF
{
    "Rules": [
        {
            "ID": "DeleteOldFiles",
            "Status": "Enabled",
            "Filter": {
                "Prefix": "logs/"
            },
            "Expiration": {
                "Days": 30
            }
        },
        {
            "ID": "TransitionToIA",
            "Status": "Enabled",
            "Transitions": [
                {
                    "Days": 30,
                    "StorageClass": "STANDARD_IA"
                },
                {
                    "Days": 90,
                    "StorageClass": "GLACIER"
                }
            ]
        }
    ]
}
EOF

# 套用生命週期規則
aws s3api put-bucket-lifecycle-configuration --bucket my-bucket-name --lifecycle-configuration file://lifecycle.json

# 查看生命週期規則
aws s3api get-bucket-lifecycle-configuration --bucket my-bucket-name

# 刪除生命週期規則
aws s3api delete-bucket-lifecycle --bucket my-bucket-name
```

{{< /note >}}

<!-- S3 版本控制 -->
{{< note title="S3 版本控制" >}}

```bash
# 啟用版本控制
aws s3api put-bucket-versioning --bucket my-bucket-name --versioning-configuration Status=Enabled

# 查看版本控制狀態
aws s3api get-bucket-versioning --bucket my-bucket-name

# 列出檔案的所有版本
aws s3api list-object-versions --bucket my-bucket-name --prefix file.txt

# 下載特定版本的檔案
aws s3api get-object --bucket my-bucket-name --key file.txt --version-id VERSION_ID output.txt

# 刪除特定版本
aws s3api delete-object --bucket my-bucket-name --key file.txt --version-id VERSION_ID

# 暫停版本控制
aws s3api put-bucket-versioning --bucket my-bucket-name --versioning-configuration Status=Suspended
```

{{< /note >}}

<!-- S3 跨區域複製 -->
{{< note title="S3 跨區域複製" >}}

```bash
# 建立複製規則
cat > replication.json << EOF
{
    "Role": "arn:aws:iam::ACCOUNT_ID:role/replication-role",
    "Rules": [
        {
            "ID": "ReplicateToBackup",
            "Status": "Enabled",
            "Filter": {
                "Prefix": "important/"
            },
            "Destination": {
                "Bucket": "arn:aws:s3:::backup-bucket-name",
                "StorageClass": "STANDARD_IA"
            }
        }
    ]
}
EOF

# 套用複製規則
aws s3api put-bucket-replication --bucket my-bucket-name --replication-configuration file://replication.json

# 查看複製規則
aws s3api get-bucket-replication --bucket my-bucket-name

# 刪除複製規則
aws s3api delete-bucket-replication --bucket my-bucket-name
```

{{< /note >}}

<!-- 常用 S3 技巧 -->
{{< note title="常用 S3 技巧" >}}

```bash
# 產生預簽名 URL (臨時存取連結)
aws s3 presign s3://my-bucket-name/file.txt --expires-in 3600

# 計算檔案 MD5 雜湊值
aws s3api head-object --bucket my-bucket-name --key file.txt --query 'ETag' --output text

# 批次操作 (使用 xargs)
aws s3 ls s3://my-bucket-name --recursive | grep ".log" | awk '{print $4}' | xargs -I {} aws s3 rm s3://my-bucket-name/{}

# 監控傳輸進度
aws s3 cp large-file.zip s3://my-bucket-name/ --cli-read-timeout 0 --cli-write-timeout 0

# 設定多部分上傳閾值
aws configure set default.s3.multipart_threshold 64MB
aws configure set default.s3.max_concurrent_requests 10

# 使用不同的 storage class
aws s3 cp file.txt s3://my-bucket-name/ --storage-class STANDARD_IA
aws s3 cp file.txt s3://my-bucket-name/ --storage-class GLACIER

# 加密上傳
aws s3 cp file.txt s3://my-bucket-name/ --sse AES256
aws s3 cp file.txt s3://my-bucket-name/ --sse aws:kms --sse-kms-key-id alias/my-key
```

{{< /note >}}