const Replicate = require("replicate");
const fs = require("fs");
const path = require("path");

const replicate = new Replicate({
  auth: process.env.REPLICATE_API_TOKEN
});

// 📁 Ruta donde se guardan las imágenes
const carpetaImagenes = path.join(__dirname, "api", "imagenes-generadas-con-IA");

// Crear carpeta si no existe
if (!fs.existsSync(carpetaImagenes)) {
  fs.mkdirSync(carpetaImagenes, { recursive: true });
}

// 🔥 Convierte stream a buffer
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

      // 🟣 Caso stream
      if (first && typeof first === "object" && typeof first.getReader === "function") {
        buffer = await streamToBuffer(first);
      }

      // 🟢 Caso URL
      else if (typeof first === "string") {
        const response = await fetch(first);
        buffer = Buffer.from(await response.arrayBuffer());
      }
    }

    // 🟡 Caso string directo
    else if (typeof output === "string") {
      const response = await fetch(output);
      buffer = Buffer.from(await response.arrayBuffer());
    }

    if (!buffer) {
      throw new Error("No se pudo obtener la imagen");
    }

    // 📸 Nombre único
    const nombreArchivo = `imagen_${Date.now()}.png`;
    const rutaCompleta = path.join(carpetaImagenes, nombreArchivo);

    // 💾 Guardar imagen
    fs.writeFileSync(rutaCompleta, buffer);

    console.log("Imagen guardada en:", rutaCompleta);

    // 🌐 URL que va a usar Vue
    const url = `http://localhost:3000/api/imagenes-generadas-con-IA/${nombreArchivo}`;

    return url;

  } catch (error) {
    console.error("Error en Replicate:", error);
    throw error;
  }
}

module.exports = { generarImagen };