---
title: "GitLab Runner config.toml Configuration and Common CI/CD Variables"
description: GitLab Runner configuration reference covering glrt- token registration, config.toml location, concurrent, executor, [runners.docker], cache, Docker-in-Docker, Harbor private registries, and predefined variables such as CI_COMMIT_SHA.
lastmod: 2026-10-26T00:00:00+08:00
weight: 510
menu:
  notes:
    name: Runner config.toml
    identifier: notes-gitlab-runner-config
    parent: notes-gitlab
    weight: 10
---

{{< note title="Version and safety scope" >}}

**Last reviewed: October 26, 2026**

Checked against the official GitLab documentation on October 26, 2026, when the latest GitLab Runner release was v19.5.1. Settings and defaults change between versions; before production use, check [Runner advanced configuration](https://docs.gitlab.com/runner/configuration/advanced-configuration/), [Registering runners](https://docs.gitlab.com/runner/register/), and [Predefined CI/CD variables](https://docs.gitlab.com/ci/variables/predefined_variables/).

`privileged = true`, mounting `/var/run/docker.sock`, `gitlab-runner unregister`, and `gitlab-runner verify --delete` carry security or irreversible risks and are flagged below. Back up `config.toml` before changing it. Runner tokens and registry passwords are secrets; keep them out of repositories and CI logs.

{{< /note >}}

{{< note title="Register a runner (authentication token workflow)" >}}

The current workflow creates the runner in GitLab first, then registers it with a runner authentication token:

1. For a project runner, go to **Settings** > **CI/CD** > **Runners** and select **Create project runner** (Maintainer role required). Group and instance runners are created from group settings or the Admin Area.
2. Set tags and a description, then create the runner. GitLab shows an authentication token starting with `glrt-` only briefly.
3. Register on the runner host:

```bash
sudo gitlab-runner register \
  --non-interactive \
  --url "https://gitlab.example.com/" \
  --token "$RUNNER_TOKEN" \
  --executor "docker" \
  --docker-image alpine:latest \
  --docker-pull-policy "if-not-present" \
  --description "docker-runner"
```

- Legacy registration tokens (`--registration-token`) are deprecated and, according to the docs, scheduled for removal in GitLab 20.0. Use authentication tokens for every new runner.
- Tags, protected status, and run-untagged are set when the runner is created in the GitLab UI or API, not through `register` arguments.
- To automate runner creation, call `POST /api/v4/user/runners` with an access token that has the `create_runner` scope, then pass the returned token to `register`:

```bash
curl --silent --request POST --url "https://gitlab.example.com/api/v4/user/runners" \
  --data "runner_type=project_type" \
  --data "project_id=<project_id>" \
  --data "description=docker-runner" \
  --data "tag_list=docker,linux" \
  --header "PRIVATE-TOKEN: <project_access_token>"
```

**About `gitlab_pat`:** `config.toml` has no `gitlab_pat` setting. The runner authenticates with the `token` under `[[runners]]` (the `glrt-` runner authentication token). A personal access token (`glpat-` prefix) is only for API automation such as creating runners; it does not belong in `config.toml`.

{{< /note >}}

{{< note title="config.toml location" >}}

| Install type | `config.toml` path |
| :-- | :-- |
| Linux/macOS run as root (`sudo`) | `/etc/gitlab-runner/config.toml` |
| Linux/macOS run as a regular user | `~/.gitlab-runner/config.toml` |
| Windows | The install folder, for example `C:\GitLab-Runner\config.toml` |
| Other systems | `./config.toml` in the current directory |
| Docker container | `/etc/gitlab-runner/` inside the container, usually mounted from `/srv/gitlab-runner/config` on the host or a Docker volume |

Docker container install, as shown in the official docs:

```bash
docker run -d --name gitlab-runner --restart always \
  -v /srv/gitlab-runner/config:/etc/gitlab-runner \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gitlab/gitlab-runner:latest
```

This hands the host Docker socket to the runner container; see the risks under "Docker-in-Docker vs socket binding".

**Reloading:** the runner checks `config.toml` every 3 seconds and reloads changes automatically, or on `SIGHUP`. Most settings need no restart; `listen_address` is the exception.

{{< /note >}}

{{< note title="Common config.toml settings" >}}

```toml
concurrent = 4          # max concurrent jobs across all runners; 0 is not allowed
check_interval = 3      # seconds between job requests to GitLab; default 3
log_level = "info"      # debug / info / warn / error / fatal / panic
shutdown_timeout = 30   # seconds before forced shutdown; default 30

[[runners]]
  name = "docker-runner"                 # informational only
  url = "https://gitlab.example.com/"
  token = "glrt-REDACTED"                # authentication token, not the registration token
  executor = "docker"                    # shell, docker, kubernetes, ...
  limit = 0                              # max concurrent jobs for this runner; 0 means no limit
  request_concurrency = 1                # concurrent job requests to GitLab; default 1
  environment = ["TZ=Asia/Taipei"]       # append or override job environment variables

  [runners.docker]
    image = "alpine:latest"              # used when a job does not set an image
    privileged = false                   # disables container isolation when true; see below
    volumes = ["/cache"]                 # extra mounts, docker -v syntax
    pull_policy = "if-not-present"       # never / if-not-present / always; default always
    allowed_images = ["registry.example.com/*"]  # restrict job images; unset allows all
    shm_size = 0

  [runners.cache]
    Type = "s3"                          # s3 / gcs / azure
    Path = "runner-cache"                # prepended to the cache URL
    Shared = true                        # share cache between runners; default false
    [runners.cache.s3]
      ServerAddress = "s3.example.com"
      BucketName = "gitlab-runner-cache"
      BucketLocation = "ap-northeast-1"
      AuthenticationType = "iam"         # iam or access-key
```

- `concurrent` caps the whole runner process; `limit` caps one `[[runners]]` entry. Both apply.
- `pull_policy = "if-not-present"` speeds up job start, but stale images already on the host are not refreshed; pin tags or digests.
- In `[runners.cache.s3]`, `AuthenticationType` defaults to `access-key` when `ServerAddress`, `AccessKey`, and `SecretKey` are all set, otherwise `iam`. `AccessKey` and `SecretKey` are secrets; prefer an IAM role.
- `listen_address = ":9252"` enables Prometheus metrics; without it, metrics are off. Changing it requires a restart.

{{< /note >}}

{{< note title="Docker-in-Docker vs socket binding" >}}

There are two common ways to run `docker build` inside a job:

| Approach | Settings | Benefit | Risk |
| :-- | :-- | :-- | :-- |
| Docker-in-Docker (DinD) | `privileged = true`, `volumes = ["/certs/client", "/cache"]` | Each job gets its own Docker daemon, so jobs do not conflict | Privileged mode effectively disables container security mechanisms and can allow escape to the host |
| Docker socket binding | `volumes = ["/var/run/docker.sock:/var/run/docker.sock", "/cache"]`, `privileged = false` | No privileged mode; shares the host image cache | Hands the host Docker daemon to jobs: container breakout, privilege escalation, or deleting the runner's own containers |

**Security warning:** both `privileged = true` and a mounted `docker.sock` give jobs close to root access on the host. Enable them only on dedicated runners for trusted projects, never on shared runners that run forks or untrusted code.

`.gitlab-ci.yml` for DinD with TLS:

```yaml
build-image:
  image: docker:<version>-cli          # use a version your team has validated
  services:
    - docker:<version>-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  script:
    - docker build -t "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA" .
```

Socket binding limitations: it cannot be combined with the `docker:dind` service, volume paths in jobs resolve against the host, and containers with fixed names conflict between concurrent jobs.

{{< /note >}}

{{< note title="Private registries such as Harbor" >}}

When the runner pulls job or service images from a private registry such as Harbor, provide credentials with `DOCKER_AUTH_CONFIG`:

```bash
# Build the auth value; printf avoids encoding a trailing newline
printf "my_username:my_password" | openssl base64 -A
```

```json
{
  "auths": {
    "harbor.example.com": {
      "auth": "<base64 of username:password>"
    }
  }
}
```

- Set it as a project or group CI/CD variable named `DOCKER_AUTH_CONFIG` (masked is recommended), in `[[runners]]` `environment` (escape the double quotes), or in `.docker/config.json` on the runner host.
- Lookup order: `/root/.docker/config.json` → CI/CD variable → `environment` in `config.toml` → `$HOME/.docker/config.json` of the user running the runner.
- The `auths` key must match the image reference exactly; for `harbor.example.com:5000/...`, the key must be `harbor.example.com:5000`.
- Prefer a Harbor robot account scoped to the projects it needs.

To push to the built-in GitLab Container Registry, use the predefined variables:

```yaml
script:
  - echo "$CI_REGISTRY_PASSWORD" | docker login "$CI_REGISTRY" -u "$CI_REGISTRY_USER" --password-stdin
  - docker push "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA"
```

`CI_REGISTRY_PASSWORD` equals `CI_JOB_TOKEN` and expires when the job ends; use a deploy token for long-lived access. Pushing to Harbor requires your own masked CI/CD variables holding robot account credentials.

{{< /note >}}

{{< note title="Useful gitlab-runner commands" >}}

```bash
sudo gitlab-runner list        # list runners in config.toml
sudo gitlab-runner verify      # check registered runners can reach GitLab
sudo gitlab-runner status      # service status; exit code 0 when running
sudo gitlab-runner restart     # stop, then start the service
sudo gitlab-runner start
sudo gitlab-runner stop

# Reload config.toml without a restart
sudo kill -SIGHUP <main_runner_pid>
```

**Irreversible commands (back up `config.toml` first):**

```bash
# Remove runners that no longer exist in GitLab; rewrites config.toml
sudo gitlab-runner verify --delete

# Unregister by name; with duplicate names only the first is removed
sudo gitlab-runner unregister --name docker-runner

# Unregister by URL and token
sudo gitlab-runner unregister --url "https://gitlab.example.com/" --token "$RUNNER_TOKEN"

# Unregister every runner
sudo gitlab-runner unregister --all-runners
```

- For runners created in the GitLab UI or API, `unregister` removes only the runner manager; delete the runner in the UI or through the API to remove it completely.
- Without `sudo`, the runner runs in user mode and uses `~/.gitlab-runner/config.toml`, a common cause of "runner not found".
- Do not use `killall` or `pkill` on runners with the shell or docker executor; it can break signal handling. Send `SIGQUIT` for a graceful stop.

{{< /note >}}

{{< note title="Common predefined CI/CD variables" >}}

| Variable | Value | Notes |
| :-- | :-- | :-- |
| `CI_COMMIT_SHA` | Full commit hash the pipeline builds | |
| `CI_COMMIT_SHORT_SHA` | First 8 characters of `CI_COMMIT_SHA` | Common image tag |
| `CI_COMMIT_REF_NAME` | Branch or tag name being built | |
| `CI_COMMIT_REF_SLUG` | `CI_COMMIT_REF_NAME` lowercased, non-alphanumerics replaced with `-`, max 63 bytes | Safe for URLs, hostnames, image tags |
| `CI_COMMIT_BRANCH` | Branch name | Not available in merge request or tag pipelines |
| `CI_COMMIT_TAG` | Tag name | Only in tag pipelines |
| `CI_DEFAULT_BRANCH` | Project default branch name | |
| `CI_PIPELINE_SOURCE` | How the pipeline was triggered | For example `push`, `merge_request_event`, `schedule`, `web`, `api`, `trigger`, `parent_pipeline` |
| `CI_PIPELINE_ID` | Pipeline ID, unique across the instance | Job-only |
| `CI_JOB_ID` | Job ID, unique across the instance | Job-only |
| `CI_REGISTRY` | Container Registry address (`<host>[:<port>]`) | Only when the registry is enabled for the instance |
| `CI_REGISTRY_IMAGE` | Base image path for the project (`<host>[:<port>]/<project_full_path>`) | Only when the registry is enabled for the project |
| `CI_REGISTRY_USER` / `CI_REGISTRY_PASSWORD` | Credentials for pushing to the project registry | Password equals `CI_JOB_TOKEN` and expires with the job |
| `CI_PROJECT_DIR` | Full path where the repository is cloned and the job runs | Follows `builds_dir` when set |
| `CI_PROJECT_NAME` / `CI_PROJECT_PATH` | Project directory name / namespace plus project name | |
| `CI_JOB_TOKEN` | Token for certain API endpoints | Valid only while the job runs; never print it |
| `CI_ENVIRONMENT_NAME` | Job environment name | Only when `environment:name` is set |
| `CI_MERGE_REQUEST_IID` | Merge request ID within the project | Only in merge request pipelines |
| `CI_SERVER_URL` | Base GitLab instance URL, including protocol and port | |
| `GITLAB_USER_LOGIN` | Username of the user who started the pipeline | For manual jobs, the user who started the job |

A common pattern for pipeline-type rules:

```yaml
deploy:
  script:
    - echo "Deploy $CI_COMMIT_SHORT_SHA to $CI_ENVIRONMENT_NAME"
  environment:
    name: production
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"   # skip scheduled pipelines
      when: never
    - if: $CI_COMMIT_TAG                       # deploy only from tag pipelines
```

{{< /note >}}

Further reading: for full `.gitlab-ci.yml`, Harbor, and multi-environment deployment examples, see the [GitLab CI/CD guide]({{< ref "/posts/gitlab-cicd-complete-guide" >}}).
