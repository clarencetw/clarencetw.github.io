const improveThemeAccessibility = () => {
  const sidebarToggler = document.getElementById('sidebar-toggler')
  if (sidebarToggler) {
    const navigation = document.querySelector('[data-notes-navigation]')
    const label = navigation?.dataset.navigationLabel || 'Toggle sidebar'

    if (!sidebarToggler.getAttribute('aria-label')) {
      sidebarToggler.setAttribute('aria-label', label)
    }
    sidebarToggler.setAttribute('aria-controls', 'sidebar-section')
    sidebarToggler.setAttribute('aria-expanded', 'false')
  }

  document.querySelectorAll('#footer h5').forEach((heading) => {
    const label = document.createElement('p')
    label.className = `${heading.className} footer-heading`.trim()
    label.innerHTML = heading.innerHTML
    heading.replaceWith(label)
  })
}

const setupNotesNavigation = () => {
  if (!document.body.classList.contains('type-notes')) return

  const sidebar = document.getElementById('sidebar-section')
  const navigation = document.querySelector('[data-notes-navigation]')
  const toggle = document.getElementById('sidebar-toggler')
  const closeButton = document.querySelector('[data-notes-close]')
  const backdrop = document.querySelector('[data-notes-backdrop]')
  const content = document.getElementById('content-section')
  const desktop = window.matchMedia('(min-width: 1200px)')
  let restoreFocus = false
  let focusTimer = 0

  if (!sidebar || !navigation || !toggle) return

  const setOpen = (isOpen, options = {}) => {
    window.clearTimeout(focusTimer)
    sidebar.classList.toggle('expanded', isOpen)
    document.body.classList.toggle('notes-sidebar-open', isOpen)
    toggle.setAttribute('aria-expanded', String(isOpen))
    content?.classList.remove('hide')

    if (backdrop) backdrop.hidden = !isOpen

    if (isOpen && options.focus !== false) {
      restoreFocus = true
      focusTimer = window.setTimeout(() => {
        const search = document.getElementById('notes-filter')
        const focusTarget = search || closeButton
        focusTarget?.focus()
      }, 200)
    } else if (!isOpen && options.restore !== false && restoreFocus) {
      restoreFocus = false
      toggle.focus()
    }
  }

  toggle.addEventListener('click', (event) => {
    event.preventDefault()
    event.stopImmediatePropagation()
    setOpen(!sidebar.classList.contains('expanded'))
  }, true)

  closeButton?.addEventListener('click', () => setOpen(false))
  backdrop?.addEventListener('click', () => setOpen(false))

  document.addEventListener('keydown', (event) => {
    if (!sidebar.classList.contains('expanded')) return

    if (event.key === 'Escape') {
      event.preventDefault()
      setOpen(false)
      return
    }

    if (event.key !== 'Tab' || desktop.matches) return

    const focusable = [...navigation.querySelectorAll(
      'a[href], button:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )].filter((element) => !element.hidden && element.offsetParent !== null)

    if (!focusable.length) return
    const first = focusable[0]
    const last = focusable[focusable.length - 1]

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault()
      last.focus()
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault()
      first.focus()
    }
  })

  desktop.addEventListener('change', (event) => {
    if (event.matches) setOpen(false, { restore: false })
  })

  setOpen(false, { restore: false })
}

const setupNotesFilter = () => {
  const input = document.getElementById('notes-filter')
  const status = document.getElementById('notes-filter-status')
  const groups = [...document.querySelectorAll('.notes-nav-group')]

  if (!input || !groups.length) return

  const normalise = (value) => value.normalize('NFKC').toLocaleLowerCase().trim()

  const filterNotes = () => {
    const query = normalise(input.value)
    let visibleCount = 0

    groups.forEach((group) => {
      const groupLabel = normalise(
        group.querySelector('[data-notes-group-label]')?.textContent || ''
      )
      const groupMatches = query && groupLabel.includes(query)
      const leaves = [...group.querySelectorAll('.notes-nav-leaf')]
      let groupCount = 0

      leaves.forEach((leaf) => {
        const matches = !query || groupMatches || normalise(leaf.textContent).includes(query)
        leaf.hidden = !matches
        if (matches) groupCount += 1
      })

      group.hidden = groupCount === 0
      visibleCount += groupCount
    })

    if (status) {
      const resultLabel = status.dataset.resultLabel || ''
      status.textContent = query ? `${visibleCount} ${resultLabel}`.trim() : ''
    }
  }

  input.addEventListener('input', filterNotes)
}

const setupNotesOutline = () => {
  const links = [...document.querySelectorAll('.notes-page-outline a[href^="#"]')]
  if (!links.length || !('IntersectionObserver' in window)) return

  const sections = links
    .map((link) => ({ link, section: document.getElementById(decodeURIComponent(link.hash.slice(1))) }))
    .filter(({ section }) => section)
  const visible = new Map()

  const setActive = (activeLink) => {
    links.forEach((link) => {
      const isActive = link === activeLink
      link.classList.toggle('is-active', isActive)
      if (isActive) link.setAttribute('aria-current', 'location')
      else link.removeAttribute('aria-current')
    })
  }

  const observer = new window.IntersectionObserver((entries) => {
    entries.forEach((entry) => visible.set(entry.target, entry.isIntersecting))
    const active = sections.find(({ section }) => visible.get(section))
    if (active) setActive(active.link)
  }, {
    rootMargin: '-18% 0px -68% 0px',
    threshold: 0
  })

  sections.forEach(({ section }) => observer.observe(section))
  setActive(sections[0]?.link)
}

const fallbackCopyText = (value) => {
  const textarea = document.createElement('textarea')
  textarea.value = value
  textarea.setAttribute('readonly', '')
  textarea.style.position = 'fixed'
  textarea.style.opacity = '0'
  document.body.appendChild(textarea)
  textarea.select()
  const copied = document.execCommand('copy')
  textarea.remove()
  if (!copied) throw new Error('Copy command failed')
}

const setupCodeCopyButtons = () => {
  const resetTimers = new WeakMap()

  document.querySelectorAll('[data-copy-code]').forEach((button) => {
    button.addEventListener('click', async () => {
      const shell = button.closest('[data-code-shell]')
      const code = shell?.querySelector('pre code')
      const label = button.querySelector('[data-copy-button-label]')
      const status = shell?.querySelector('[data-copy-status]')
      const defaultLabel = button.dataset.copyLabel || 'Copy'

      if (!code || !label) return

      const showState = (message, className) => {
        label.textContent = message
        button.setAttribute('aria-label', message)
        button.classList.remove('is-copied', 'is-error')
        button.classList.add(className)
        if (status) status.textContent = message

        window.clearTimeout(resetTimers.get(button))
        resetTimers.set(button, window.setTimeout(() => {
          label.textContent = defaultLabel
          button.setAttribute('aria-label', defaultLabel)
          button.classList.remove('is-copied', 'is-error')
          if (status) status.textContent = ''
        }, 1800))
      }

      try {
        if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(code.textContent)
        else fallbackCopyText(code.textContent)
        showState(button.dataset.copiedLabel || 'Copied', 'is-copied')
      } catch {
        showState(button.dataset.copyErrorLabel || 'Copy failed', 'is-error')
      }
    })
  })
}

const setupCredentialBadgeImages = () => {
  document.querySelectorAll('[data-credential-badge-image]').forEach((image) => {
    const media = image.closest('[data-credential-media]')
    if (!media) return

    const hideUnavailableImage = () => {
      media.hidden = true
      media.closest('li')?.classList.add('about-credential-item--text')
    }

    image.addEventListener('error', hideUnavailableImage, { once: true })
    if (image.complete && image.naturalWidth === 0) hideUnavailableImage()
  })
}

const initialiseSiteEnhancements = () => {
  improveThemeAccessibility()
  setupNotesNavigation()
  setupNotesFilter()
  setupNotesOutline()
  setupCodeCopyButtons()
  setupCredentialBadgeImages()
}

if (document.readyState === 'loading') {
  window.addEventListener('DOMContentLoaded', initialiseSiteEnhancements)
} else {
  initialiseSiteEnhancements()
}
