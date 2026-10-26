---
title: "Self-hosted GitLab, Runner, and Harbor: A CI/CD Flow from Source Code to Deployment"
url: "https://clarence.tw/en/posts/self-hosted-gitlab-runner-harbor/"
language: "en"
---

# Self-hosted GitLab, Runner, and Harbor: A CI/CD Flow from Source Code to Deployment

An operator's view of self-hosted GitLab, GitLab Runner, and Harbor registry, covering why to self-host, how the pieces connect, and the upgrades, backups, signing keys, and log limits that come with running it for years.

Since 2022, I have built and maintained self-hosted GitLab, GitLab Runner, Harbor registry, and CI/CD workflows as an Operator, connecting source code, container images, and deployment into one flow.

This is not a setup tutorial. Examples for `.gitlab-ci.yml`, Runner deployment, and multi-environment deployment are in the [GitLab CI/CD Guide: Runner Setup, .gitlab-ci.yml, Harbor, and Deployments](https://clarence.tw/en/posts/gitlab-cicd-complete-guide/), and `config.toml` options and common variables are in [GitLab Runner config.toml Configuration and Common CI/CD Variables](https://clarence.tw/en/notes/gitlab/runner-config/). This post covers the other side: why you would run this stack yourself, how the components fit together, and where the time actually goes after a few years. Each problem mentioned below links to the record I wrote at the time on [blog.clarence.tw](https://blog.clarence.tw/).

## Why Consider Self-hosting

GitLab.com and the cloud registries are mature, so self-hosting is not the default answer. It usually comes from several considerations stacking up:

- **Where code and data live**: some teams need source code, images, and build logs to stay in an environment they control.
- **Network environment**: when deployment targets are on-premises or on an internal network, keeping Runners and the registry on the same side shortens build and image pull paths and makes outbound traffic easier to control.
- **Runner resources**: jobs that need specific hardware, operating systems, or larger build capacity are easier to schedule on your own Runners.
- **Integration**: the platform has to connect with existing identity, monitoring, and backup processes.

The cost is equally clear: upgrades, backups, certificates, signing keys, disk space, and troubleshooting all become your responsibility. Before self-hosting, make sure someone is willing to own that work for the long term.

## The Overall Flow

The flow fits in one sentence: code goes into GitLab, Runners build and test it according to the pipeline, the resulting container image is pushed to Harbor, and the deployment environment pulls the image from Harbor.

1. **Source**: a developer pushes a commit or tag to GitLab, which triggers a pipeline.
2. **CI**: GitLab assigns jobs to Runners with matching tags, which run tests and build the image.
3. **Image**: the built image is pushed to the matching Harbor project according to the tagging rules.
4. **Deploy**: the deployment environment pulls a specific image version from Harbor with a pull-only account.

Splitting it this way gives each stage a clear responsibility. When a pipeline fails, you can first decide whether the problem is in source, build, push, or deploy instead of guessing across the whole chain.

There is not always just one registry. In 2021 I wrote about [using Jib and Gradle in GitLab CI to push images to GitLab Container Registry, Azure Container Registry, and Amazon ECR](https://blog.clarence.tw/2021/07/25/java-jib-gradle-uses-gitlab-ci-cd-to-automatically-upload-docker-to-gitlab-container-registry-azure-container-registry-and-amazon-elastic-container-registry/). The ECR login flow required me to build a separate image with the AWS CLI and a credential helper. Every additional registry adds another authentication method and another way for things to break.

## Runner Strategy

Runners are the part of CI/CD that gets adjusted most often. A few general principles help:

- **Route with tags**: send different kinds of jobs (regular builds, jobs that need Docker, special environments) to different Runners so they do not compete for resources.
- **Minimize privileges**: `privileged` mode and mounting the Docker socket effectively hand host access to the job. Enable them only for projects that need them and can be trusted.
- **Treat the config as an asset**: `config.toml` contains runner tokens. Back it up before editing and never commit it to a repository.

Runner versions and helper images can break too. In 2020, on the `docker-windows` executor, I ran into [Missing gitlab-runner-helper errors that disabled artifact uploads](https://blog.clarence.tw/2020/02/09/windows-gitlab-runner-in-docker-windows-missing-error-uploading-artifacts-is-disabled-or-missing-gitlab-runner-helper-uploading-artifacts-is-disabled-who-to-fix/), and fixed it by setting `helper_image` in `config.toml`. See the Runner note linked above for specific options and their risks.

## Harbor and Image Management

### Robot Accounts and CI Authentication

When CI pushes images to Harbor, I use a Harbor robot account rather than a personal account. According to the [Harbor documentation](https://goharbor.io/docs/2.13.0/working-with-projects/project-configuration/create-robot-accounts/), a project robot account can act only within its own project, its permissions are chosen at creation, and it can have an expiration time. Giving CI push access and deployment targets pull-only access is an easy split to manage.

Robot account names carry a `robot$` prefix by default, and that `$` cost me some time. In 2023 I documented [docker login returning unauthorized when integrating GitLab CI with Harbor](https://blog.clarence.tw/2023/11/26/%e8%a7%a3%e6%b1%ba%e4%bd%bf%e7%94%a8-gitlab-ci-%e6%95%b4%e5%90%88-harbor-%e5%87%ba%e7%8f%be%e7%9a%84%e5%a5%87%e6%80%aa%e5%95%8f%e9%a1%8c%ef%bc%9a%e5%b8%b3%e8%99%9f%e4%b8%ad%e7%9a%84-%e7%ac%a6/). Interactive login worked, but inside the pipeline the `$` was expanded as a variable. The fix at the time was to write `$$` in `.gitlab-ci.yml` and pass the password with `--password-stdin`. According to the [GitLab CI/CD variables documentation](https://docs.gitlab.com/ci/variables/), variables defined in the UI do not expand `$` references by default, so storing the account name as a CI/CD variable is another option worth considering.

### Tagging Rules and Storage

An image tag should trace back to source code. A common approach is to use version numbers for releases and the commit SHA for other builds. In 2020 I documented a small requirement: [turning the Git tag `v1.0.0` into the image tag `1.0.0`](https://blog.clarence.tw/2020/11/10/gitlab-ci-docker-tag-removal-version-v/) by dropping the first character with `${CI_COMMIT_TAG:1}`. The rule is simple, but it should be decided early so every project follows the same convention.

Images only accumulate. Harbor offers several tools to manage them:

- **Tag retention**: keep the tags you need by repository, count, or age, and remove the rest. The documentation recommends a dry run first because a run cannot be undone.
- **Tag immutability**: prevent release tags from being overwritten so a version number always points to the same image.
- **Garbage collection**: deleting tags or artifacts does not free space immediately. You need to run [garbage collection](https://goharbor.io/docs/2.13.0/administration/garbage-collection/) to remove blobs that are no longer referenced.

## Long-term Operations: Upgrades, Backups, Signing Keys, and Log Limits

Standing the system up is only the beginning. Most of the time goes into the years of maintenance that follow. These are the kinds of problems I recorded on my blog.

### Upgrades: Required Stops Cannot Be Skipped

In 2023 I documented [upgrading GitLab from 14.9.3](https://blog.clarence.tw/2023/12/24/gitlab-%e4%bc%ba%e6%9c%8d%e5%99%a8%e5%8d%87%e7%b4%9a%e6%8c%87%e5%8d%97%ef%bc%9a%e5%be%9e%e7%89%88%e6%9c%ac-14-9-3-%e5%8d%87%e7%b4%9a/). A direct apt upgrade was blocked by the package's preinstall check, which required moving to 14.10.x first. The fix was to step through versions with `apt install gitlab-ce=<version>`, restarting and checking services at each stop.

The lesson: the longer GitLab goes without an upgrade, the longer the path becomes. According to the [GitLab upgrade paths documentation](https://docs.gitlab.com/update/upgrade_paths/), required upgrade stops cannot be skipped; at each stop, upgrade to the latest patch release and let background migrations finish before continuing. GitLab also provides an Upgrade Path tool that calculates which stops apply. Small, regular upgrades are much safer than one large upgrade every few years.

### Backups: Know What You Are Backing Up

In 2023 I wrote a [Bash script that uses the GitLab API to clone every project under an account](https://blog.clarence.tw/2023/11/12/%e5%a6%82%e4%bd%95%e5%82%99%e4%bb%bd%e6%95%b4%e5%80%8b-gitlab-%e6%89%80%e6%9c%89%e5%b0%88%e6%a1%88/), because a colleague needed all the repositories at once. A script like this is useful for migration or keeping a copy of the code, but it covers Git repositories only, not issues, merge requests, or CI/CD settings.

A complete GitLab backup still relies on the official backup process. According to the [GitLab backup documentation](https://docs.gitlab.com/administration/backup_restore/backup_gitlab/), the backup task does not include configuration files. For Linux package installations, at minimum back up `/etc/gitlab/gitlab-secrets.json` and `/etc/gitlab/gitlab.rb` separately, and do not store them with the data backup. Without the secrets file, encrypted data in the database cannot be restored.

### Package Signing Keys: They Will Expire

Installing GitLab and Runner through apt means dealing with repository signing key rotation. I hit it twice:

- In 2020, [`apt update` reported `NO_PUBKEY`](https://blog.clarence.tw/2020/04/21/gitlab-gpg-key-update/) and the new GitLab GPG key had to be imported.
- In 2022, updating Runner on Ubuntu 18.04 [failed with `EXPKEYSIG` because the key had expired](https://blog.clarence.tw/2022/09/11/ubuntu-18-04-lts-gitlab-%e9%87%91%e9%91%b0%e9%81%8e%e6%9c%9f%e8%99%95%e7%90%86%e6%96%b9%e6%b3%95/), so it had to be downloaded and imported again.

These issues do not take the service down immediately, but they make upgrades fail quietly. The `apt-key` command used in those posts is no longer recommended on newer Debian and Ubuntu releases, so follow GitLab's current official instructions when handling this today.

### Log Limits: 4 MB by Default

In 2022 I ran into [Runner reporting `Job's log exceeded limit of 4194304 bytes`](https://blog.clarence.tw/2022/11/27/gitlab-runner-%e5%87%ba%e7%8f%be-jobs-log-exceeded-limit-of-4194304-bytes-%e7%9a%84%e8%a7%a3%e6%b3%95/). According to the [Runner advanced configuration](https://docs.gitlab.com/runner/configuration/advanced-configuration/), `output_limit` under `[[runners]]` defaults to 4096 KB. Raising it keeps the job running, but the better fix is to find out why the log is so large, for example by turning off unnecessary verbose output.

## What I Learned

- **The cost of self-hosting comes later**: installation happens once, while upgrades, backups, signing keys, and storage management recur every year and belong in a regular operations rhythm.
- **Draw clear boundaries between stages**: source, CI, image, and deploy each have their own components and permissions, which makes problems quick to locate.
- **Design accounts and permissions for automation**: robot accounts for CI and pull-only access for deployment are easier to manage and rotate than shared personal accounts.
- **Write down the problems you hit**: for every issue above, the fastest fix the next time was the record I left myself.
