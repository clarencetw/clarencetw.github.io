document.addEventListener('DOMContentLoaded', () => {
  const target = document.getElementById('typed')
  const list = document.getElementById('typing-carousel-data')?.children

  if (!target || !list || list.length === 0) return

  const strings = Array.from(list)
    .map(item => item.textContent.trim())
    .filter(Boolean)

  if (strings.length === 0) return

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    target.textContent = strings[0]
    return
  }

  let stringIndex = 0
  let charIndex = 0
  let deleting = false

  const tick = () => {
    const chars = Array.from(strings[stringIndex])
    target.textContent = chars.slice(0, charIndex).join('')

    if (!deleting && charIndex < chars.length) {
      charIndex += 1
      window.setTimeout(tick, 82)
      return
    }

    if (!deleting) {
      deleting = true
      window.setTimeout(tick, 1350)
      return
    }

    if (charIndex > 0) {
      charIndex -= 1
      window.setTimeout(tick, 36)
      return
    }

    deleting = false
    stringIndex = (stringIndex + 1) % strings.length
    window.setTimeout(tick, 260)
  }

  tick()
})
