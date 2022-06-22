---
title: Mac Launchpad
weight: 210
menu:
  notes:
    name: Launchpad
    identifier: notes-mac-launchpad
    parent: notes-mac
    weight: 10
---

<!-- Launchpad reset -->
{{< note title="Launchpad reset" >}}

```bash
defaults write com.apple.dock ResetLaunchPad -bool true;
killall Dock
```

{{< /note >}}
