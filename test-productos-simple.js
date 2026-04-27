const http = require('http');

console.log('✅ Probando /productos-ia...\n');

const options = {
  hostname: 'localhost',
  port: 5001,
  path: '/productos-ia',
  method: 'GET',
  timeout: 70000
};

const req = http.request(options, (res) => {
  let data = '';

  res.on('data', (chunk) => {
    data += chunk;
  });

  res.on('end', () => {
    try {
      const json = JSON.parse(data);
      console.log(`✅ Response: 200 OK`);
      console.log(`✅ Total productos: ${json.length || 0}\n`);
      
      if (json.length > 0) {
        const producto = json[0];
        console.log('📦 Primer producto:');
        console.log(`   ID: ${producto.id_producto}`);
        console.log(`   Nombre: ${producto.producto}`);
        console.log(`   Precio: $${producto.precio}`);
        console.log(`   Variantes: ${producto.variantes?.length || 0}`);
        
        if (producto.variantes && producto.variantes.length > 0) {
          console.log('\n🔍 Primera variante:');
          const variante = producto.variantes[0];
          console.log(`   ID: ${variante.id_variante}`);
          console.log(`   Talle: ${variante.talle || 'N/A'}`);
          console.log(`   Color: ${variante.color || 'N/A'}`);
          console.log(`   Precio: $${variante.precio}`);
        }
      }
    } catch (e) {
      console.error('❌ Error parseando JSON:', e.message);
      console.log('Respuesta raw (primeros 500 chars):\n', data.substring(0, 500));
    }
  });
});

req.on('error', (e) => {
  console.error('❌ Error de conexión:', e.message);
  console.error('   El agente puede no estar corriendo en el puerto 5001');
});

req.on('timeout', () => {
  console.error('❌ Timeout después de 70 segundos');
  req.destroy();
});

req.end();
