const HF_TOKEN = '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'

async function _getFetch() {
  if (typeof globalThis.fetch === 'function') return globalThis.fetch

  try {
    const mod = await import('node-fetch')
    return mod.default || mod
  } catch (e) {
    try {
      // eslint-disable-next-line global-require
      const { fetch: undiciFetch } = require('undici')
      if (typeof undiciFetch === 'function') return undiciFetch
    } catch (err) {
      // ignore
    }
  }

  throw new Error('No hay una implementación de fetch disponible. Usa Node 18+ o instala `undici`.')
}

async function generarImagen(prompt) {
  const fetch = await _getFetch()

  const response = await fetch(
    'https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0',
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${HF_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        inputs: prompt
      })
    }
  )

  const contentType = response.headers.get && response.headers.get('content-type')

  if (!contentType || !contentType.includes('image')) {
    const errorText = await response.text()
    throw new Error(errorText)
  }

  const buffer = await response.arrayBuffer()
  const base64 = Buffer.from(buffer).toString('base64')

  return `data:image/png;base64,${base64}`
}

module.exports = { generarImagen }