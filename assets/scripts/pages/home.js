document.addEventListener('DOMContentLoaded', () => {
  const target = document.getElementById('typed')
  const list = document.getElementById('typing-carousel-data')?.children

  if (!target || !list || list.length === 0) return

  const strings = Array.from(list)
    .map(item => item.textContent.trim())
    .filter(Boolean)

  if (strings.length === 0) return

  const rail = target.closest('.typing-carousel')
  rail?.classList.add('delivery-rail')
  rail?.classList.toggle('delivery-rail--extended', strings.length > 4)
  rail?.querySelector('.ityped-cursor')?.setAttribute('hidden', '')

  target.replaceChildren(
    ...strings.map((label, index) => {
      const stage = document.createElement('span')
      stage.className = 'delivery-stage'
      const stageIndex = document.createElement('span')
      stageIndex.className = 'delivery-stage__index'
      stageIndex.setAttribute('aria-hidden', 'true')
      stageIndex.textContent = String(index + 1).padStart(2, '0')

      const stageLabel = document.createElement('span')
      stageLabel.className = 'delivery-stage__label'
      stageLabel.textContent = label

      stage.replaceChildren(stageIndex, stageLabel)
      return stage
    })
  )
})
