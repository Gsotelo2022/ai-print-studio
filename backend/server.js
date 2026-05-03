require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') })
const express = require('express')
const cors = require('cors')
const path = require('path')
const { generarImagen } = require('./generateImage')

const app = express()
app.use(cors())
app.use(express.json())

app.post('/generar-imagen', async (req, res) => {
  if (!process.env.REPLICATE_API_TOKEN) {
    return res.status(500).json({ error: 'REPLICATE_API_TOKEN no configurada en el servidor' })
  }

  try {
    const { prompt } = req.body
    if (!prompt?.trim()) {
      return res.status(400).json({ error: 'El prompt es requerido' })
    }

    console.log('Prompt:', prompt)
    const imagen = await generarImagen(prompt)
    res.json({ imagen })

  } catch (error) {
    console.error('Error Replicate:', error.message)
    const msg = error.message?.includes('401') || error.message?.includes('auth')
      ? 'REPLICATE_API_TOKEN inválida o sin permisos'
      : (error.message || 'No se pudo generar la imagen')
    res.status(500).json({ error: msg })
  }
})

app.use('/api/imagenes-generadas-con-IA', express.static(path.join(__dirname, './uploads/imagenes')))

app.listen(3000, () => {
  console.log('Servidor Node corriendo en http://localhost:3000')
})