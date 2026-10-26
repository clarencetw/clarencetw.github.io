---
title: "Proxmox VE and PBS: Planning and Backup Strategy for Small and Mid-sized On-prem Infrastructure"
url: "https://clarence.tw/en/posts/proxmox-ve-pbs-infrastructure/"
language: "en"
---

# Proxmox VE and PBS: Planning and Backup Strategy for Small and Mid-sized On-prem Infrastructure

How I plan and operate Proxmox VE, Proxmox Backup Server, and GPU servers, covering cluster, storage, and network principles, backup strategy, and lessons from real operational issues.

Since 2023, I have planned and operated Proxmox VE, Proxmox Backup Server (PBS), GPU servers, and On-prem infrastructure as an operator. The environment runs internal services and AI runtime workloads, and I am responsible for the overall backup strategy.

This is not an installation guide. It summarizes the planning principles I care about in small and mid-sized on-prem environments, plus problems I actually ran into and documented on my [blog](https://blog.clarence.tw/) (the linked posts are written in Traditional Chinese). It does not include hostnames, IP addresses, network layouts, or security details. Configuration advice here is general guidance, and the official Proxmox documentation remains the reference.

## Background and Requirements

On-prem requirements are usually practical: a set of internal services has to run reliably for a long time, AI workloads need GPUs, and data has to be backed up and restorable. Budget and headcount are limited, so the platform has to be maintainable by a small team.

Proxmox VE fits this situation well. VMs and LXC containers are managed in the same interface, clustering, storage, and backup have built-in approaches, and PBS adds incremental, deduplicated backups. For me, the point is not having the most features. It is whether we can investigate and recover quickly when something breaks.

My responsibilities in this area include:

- Designing and operating Proxmox VE clusters, virtualization, storage, and the VM lifecycle.
- Building Proxmox Backup Server and planning backup, restore, and disaster recovery processes.
- Managing NVIDIA GPU servers, drivers and runtimes, inference environments, and system tuning.
- Evaluating Dell, HP, and Supermicro server hardware and GPU server specifications, and turning them into specs that can be purchased and operated.
- Planning internal and external data center paths, site-to-site backup, and high availability, and using LibreNMS for network and server monitoring.

## Planning: Cluster, Storage, and Network

### Cluster

A cluster gives you central management and VM mobility, but it also brings quorum into the picture. According to the [Proxmox VE documentation](https://pve.proxmox.com/pve-docs/chapter-pvecm.html), High Availability needs at least three nodes for reliable quorum. A two-node cluster can use a QDevice as the third vote.

A few other things I check early:

- **Consistent node versions**: the documentation recommends keeping all nodes on the same version, so upgrades should be planned and rolled out node by node.
- **CPU compatibility**: online migration is only guaranteed between CPUs from the same vendor. With mixed hardware, choose a conservative CPU model for VMs, or live migration may fail.
- **Node lifecycle**: adding, replacing, and removing nodes should follow a fixed procedure, not improvisation.

### Storage

The principle is to separate things that grow from the system itself. VM disks, ISOs and templates, and backup data each have a suitable place. Backup data in particular should not share space with the hypervisor's system disk, or a spike on one side will take down the other.

VM disks should also be expected to grow. Expanding a disk in Proxmox is easy, but after resizing on the hypervisor side, the partition, LVM, and filesystem inside the guest OS also need to be adjusted. I documented the [full steps for an Ubuntu 22.04 VM](https://blog.clarence.tw/2024/08/04/%e5%9c%a8-proxmox-ve-%e4%b8%ad%e6%93%b4%e5%b1%95-ubuntu-22-04-%e8%99%9b%e6%93%ac%e6%a9%9f%e7%9a%84%e7%a3%81%e7%a2%9f%e7%a9%ba%e9%96%93/) on my blog.

### Network

Cluster communication uses Corosync, which is sensitive to latency but does not need much bandwidth. The documentation recommends a dedicated physical NIC for cluster traffic and a second link on a different physical network for redundancy, so VM or backup traffic cannot crowd out Corosync.

As a general principle, plan management, cluster, VM, and backup traffic separately, and settle the addressing plan at the start. Changing a cluster's communication addresses later costs more than you might expect (see the operational issues below).

## GPU Servers and AI Workloads

AI runtimes are sensitive to GPU, driver, CUDA, and kernel versions. The operational goal for GPU servers is an environment that can be rebuilt, not a machine that happens to work.

A common way to use GPUs on Proxmox is PCI(e) passthrough. The [documentation](https://pve.proxmox.com/pve-docs/chapter-qm.html) points out several trade-offs to think through first:

- The hardware and BIOS / UEFI must support IOMMU, and it must be enabled.
- Once a GPU is passed through to a VM, the host and other VMs can no longer use that card.
- VMs with passed-through PCI devices currently cannot be live-migrated, so node maintenance needs planned downtime.

Because of these limits, it helps to plan GPU workloads per machine: which services need exclusive GPU access, how drivers and runtimes are versioned, and how services are stopped and brought back during host maintenance.

Driver problems are the most common issue in GPU operations. I documented how I handled [`nvidia-smi` reporting "No devices were found"](https://blog.clarence.tw/2024/02/19/%e8%a7%a3%e6%b1%ba-nvidia-linux-%e4%bd%bf%e7%94%a8-nvidia-smi-%e5%87%ba%e7%8f%be-no-devices-were-found-%e5%95%8f%e9%a1%8c/) and [NVIDIA drivers failing to load under Secure Boot on Ubuntu 24.04](https://blog.clarence.tw/2026/01/31/%e8%a7%a3%e6%b1%ba-ubuntu-24-04-secure-boot-%e7%92%b0%e5%a2%83%e4%b8%8b-nvidia-%e9%a9%85%e5%8b%95%e7%84%a1%e6%b3%95%e8%bc%89%e5%85%a5%e5%95%8f%e9%a1%8c/). The common lesson: first understand how the kernel, driver, Secure Boot, and build environment relate to each other, then decide on a fix, instead of reinstalling repeatedly.

## Proxmox Backup Server Backup Strategy

I look at backup strategy as four parts: backup, retention, cleanup, and verification, plus restore drills on top.

### Prune and Garbage Collection Are Different Things

This is the most commonly misunderstood part of PBS. According to the [PBS documentation](https://pbs.proxmox.com/docs/maintenance.html):

- **Prune** only removes snapshot metadata (manifests, indexes, and so on). The chunks that hold the actual data are not removed immediately.
- **Garbage Collection (GC)** is what actually deletes chunks no longer referenced by any snapshot. GC runs in two phases, mark and sweep, with a grace period (about 24 hours and 5 minutes by default), so running GC right after a prune does not necessarily free space immediately.

Retention settings (`keep-last`, `keep-daily`, `keep-weekly`, and so on) and the GC schedule should be designed together. Pruning without scheduled GC lets usage keep growing. Scheduling GC with an overly generous retention policy runs out of space just the same.

### Keep Headroom; Do Not Wait for 100%

I documented how I handled a [PBS disk that reached 100% usage](https://blog.clarence.tw/2024/05/29/%e5%a6%82%e4%bd%95%e8%99%95%e7%90%86-proxmox-backup-server-%e7%a1%ac%e7%a2%9f%e7%a9%ba%e9%96%93%e6%bb%bf-100-%e7%9a%84%e5%95%8f%e9%a1%8c/). The trap was that GC needs some free space to run, but there was none left. The fix was to delete task logs older than 90 days to free a little space, then run GC manually.

That experience made me care more about a few things:

- Monitor datastore usage and act while there is still headroom, not when writes start failing.
- Keep the datastore and the PBS system space as separate as possible so backup data cannot fill up the system.
- Regularly check that prune and GC jobs are actually running and not failing.

### Verification and Restore Drills

A successful backup is not the same as a restorable one. The PBS documentation recommends verify jobs and re-verifying all backups at least monthly, because aging disks can slowly corrupt previously good backups (bit rot). A good pattern is a frequent verify job for new backups, plus a weekly or monthly full re-verification.

Beyond verification, real restore drills matter: periodically restore a few VMs or containers to a test environment and confirm they boot, services run, and the data is the expected version. Proxmox VE also offers live-restore and single file restore, which are worth exercising during drills.

### Off-site Copies and Disaster Recovery

A single backup copy in the same data center is not enough if the whole site has a problem. PBS can use remotes and sync jobs to replicate backups to another PBS, which forms the basis of site-to-site backup. The key is to also document how and where backups at the other site would be restored, as part of the disaster recovery process, rather than just having the data sitting there.

## Operational Issues I Ran Into

Each item below is a problem I documented publicly on my blog. Here I only summarize the key points and what I learned.

### Changing the Cluster Communication IP

I documented the process of [updating Proxmox VE cluster IPs and syncing the configuration](https://blog.clarence.tw/2025/03/19/proxmox-ve-cluster-ip-%e6%9b%b4%e6%96%b0%e8%88%87%e9%85%8d%e7%bd%ae%e5%90%8c%e6%ad%a5%e7%b6%93%e9%a9%97%e8%ab%87/). The key is to edit the cluster-shared `/etc/pve/corosync.conf`, not `/etc/corosync/corosync.conf` on a single node. Back it up first, increment `config_version` when editing, update each node's network settings and `/etc/hosts`, and confirm with `pvecm status` that the change has been applied. This affects quorum, so it is a high-risk change that belongs in a maintenance window.

### Removing a Node from the Cluster

For node replacement, I wrote up [how to safely remove a node from a Proxmox VE cluster](https://blog.clarence.tw/2025/04/12/%e5%a6%82%e4%bd%95%e5%be%9e-proxmox-ve-%e5%8f%a2%e9%9b%86%e4%b8%ad%e5%ae%89%e5%85%a8%e7%a7%bb%e9%99%a4%e7%af%80%e9%bb%9e/): back up or migrate the node's VMs and containers, shut it down and make sure it will not power back on, remove it with `pvecm delnode`, and then clean up the leftover node directory and SSH key entries. The official documentation also stresses that a removed node must not rejoin the same cluster network with its old configuration, or the cluster may break.

### NIC Firmware Errors

I documented a Proxmox VE host where an [Intel X550 kept logging ixgbe FWSM firmware errors](https://blog.clarence.tw/2026/06/25/%e8%a7%a3%e6%b1%ba-proxmox-debian-%e4%b8%8a-intel-x550-ixgbe-fwsm-firmware-error-%e5%95%8f%e9%a1%8c/). Packet counters looked normal and a kernel update did not help. The errors only went away after updating the NIC's NVM and doing a real power cycle. The lesson: do not handle firmware warnings read from the hardware by filtering logs. Before flashing firmware, take an inventory, confirm version compatibility, and have BMC / IPMI or a physical console ready.

### Repairing VMs and Containers

- **A Windows VM that will not boot**: I documented [repairing a Windows VM on PVE with WinPE](https://blog.clarence.tw/2025/10/01/%e5%9c%a8-proxmox-ve%ef%bc%88pve%ef%bc%89windows-vm-%e4%bf%ae%e5%be%a9%e6%95%99%e5%ad%b8%ef%bc%9awinpe-%e4%b8%8b-sfc-scannow%e3%80%81dism-online-%e5%a4%b1%e6%95%88%ef%bc%9f%e7%94%a8-drvload/). WinPE may not include VirtIO drivers, so you need to load them with `drvload` before the system disk is visible, then repair with offline DISM.
- **IPv6 in LXC**: I documented that [enabling IPv6 for LXC containers on PVE](https://blog.clarence.tw/2023/02/24/proxmox-ve-pve-%e4%bd%bf%e7%94%a8-linux-container-lxc-%e5%ae%b9%e5%99%a8%e4%bd%bf%e7%94%a8-ipv6/) required adjusting the host's `accept_ra` setting.
- **Wrong Web UI certificate**: I documented [PVE showing Connection error 596](https://blog.clarence.tw/2023/01/15/pve-%e5%87%ba%e7%8f%be-connection-error-596-broken-pipe-%e7%9a%84%e8%a7%a3%e6%b1%ba%e6%96%b9%e6%b3%95/) after an incorrect certificate was installed. The fix was to SSH in and replace the pveproxy certificate files with the correct ones.

### Older Hardware and Hardware Monitoring

I documented a fix for [striped display output when installing PVE or PBS on an HP ProLiant DL380 G6](https://blog.clarence.tw/2023/04/30/hp-proliant-dl380-g6-%e5%9c%a8%e5%ae%89%e8%a3%9d-proxmox-ve-pve-%e6%88%96-proxmox-backup-server-pbs-%e6%99%82%e5%87%ba%e7%8f%be%e9%bb%91%e7%99%bd%e6%a2%9d%e7%b4%8b%e5%a6%82%e4%bd%95%e8%a7%a3/), and [installing HPE Agentless Management on Proxmox](https://blog.clarence.tw/2023/01/22/%e5%9c%a8-proxmox-%e5%ae%89%e8%a3%9d-hpe-agentless-management-ams/) so iLO can read the host status. Older hardware can stay in service longer, but expect installer and monitoring tool support to shrink over time, and plan replacements early.

### Checks Before Upgrading

I wrote about [several important new features in Proxmox VE 9.2](https://blog.clarence.tw/2026/05/21/proxmox-ve-9-2-%e5%b9%be%e5%80%8b%e6%88%91%e8%a6%ba%e5%be%97%e6%af%94%e8%bc%83%e9%87%8d%e8%a6%81%e7%9a%84%e6%96%b0%e5%8a%9f%e8%83%bd/), such as HA disarm / arm, dynamic load balancing in CRS, and the Custom CPU Models GUI. Whatever the version, before upgrading production I confirm that backups are complete, kernel and driver compatibility is fine, HA and migration behave as expected, and network configuration is unaffected, and I validate on a test environment or non-critical node first.

## What I Learned

- **Backups should be judged by whether they restore**: prune, GC, verification, and restore drills are all required. A successful backup job alone is not enough.
- **Monitor space and capacity early**: once PBS reaches 100%, even the cleanup tools struggle to run. Keeping headroom is far cheaper than firefighting.
- **Cluster changes are high-risk operations**: changing IPs, removing nodes, and upgrading all call for backing up configuration first, following the documented procedure, and scheduling a maintenance window.
- **Write down the problems you hit**: every issue above can be looked up in my own notes next time, which is why I keep writing on my [blog](https://blog.clarence.tw/).
