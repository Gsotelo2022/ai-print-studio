require('dotenv').config()
const Replicate = require("replicate");
const fs = require("fs");
const path = require("path");

const replicate = new Replicate({
  auth: process.env.REPLICATE_API_TOKEN
});

const carpetaImagenes = path.join(__dirname, "uploads", "imagenes");

if (!fs.existsSync(carpetaImagenes)) {
  fs.mkdirSync(carpetaImagenes, { recursive: true });
}

async function streamToBuffer(stream) {
  const chunks = [];
  for await (const chunk of stream) {
    chunks.push(chunk);
  }
  return Buffer.concat(chunks);
}

async function generarImagen(prompt) {
  try {
    const promptMejorado =
      "high quality t-shirt design, centered, no background, vector style, clean lines, print ready, " +
      prompt;

    const output = await replicate.run(
      "black-forest-labs/flux-schnell",
      {
        input: {
          prompt: promptMejorado
        }
      }
    );

    console.log("OUTPUT:", output);

    let buffer = null;

    if (Array.isArray(output)) {
      const first = output[0];
      if (first && typeof first === "object" && typeof first.getReader === "function") {
        buffer = await streamToBuffer(first);
      } else if (typeof first === "string") {
        const response = await fetch(first);
        buffer = Buffer.from(await response.arrayBuffer());
      }
    } else if (typeof output === "string") {
      const response = await fetch(output);
      buffer = Buffer.from(await response.arrayBuffer());
    }

    if (!buffer) {
      throw new Error("No se pudo obtener la imagen");
    }

    const nombreArchivo = `imagen_${Date.now()}.png`;
    const rutaCompleta = path.join(carpetaImagenes, nombreArchivo);
    fs.writeFileSync(rutaCompleta, buffer);

    console.log("Imagen guardada en:", rutaCompleta);

    return `http://localhost:3000/api/imagenes-generadas-con-IA/${nombreArchivo}`;

  } catch (error) {
    console.error("Error en Replicate:", error);
    throw error;
  }
}

module.exports = { generarImagen };