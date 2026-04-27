require('dotenv').config()
const express = require('express')
const cors = require('cors')
const path = require('path');

const { generarImagen } = require('./generateImage')

const app = express()

app.use(cors())
app.use(express.json())

app.post('/generar-imagen', async (req, res) => {
  try {
    const { prompt } = req.body

    console.log('Prompt:', prompt)

    const imagen = await generarImagen(prompt)

    res.json({ imagen })

  } catch (error) {

    console.error('Error:', error.message)

    res.status(500).json({
      error: 'No se pudo generar la imagen'
    })
  }
})


// 👇 AGREGAR ESTO
app.use('/api/imagenes-generadas-con-IA', express.static(path.join(__dirname, 'api/imagenes-generadas-con-IA')));

app.listen(3000, () => {
  console.log('Servidor corriendo en http://localhost:3000')
})