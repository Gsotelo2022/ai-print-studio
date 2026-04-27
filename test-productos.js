const http = require('http');

console.log('Solicitando productos...');

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
      console.log('\n✅ Respuesta recibida:');
      console.log(`Total productos: ${json.value?.length || 0}`);
      if (json.value && json.value.length > 0) {
        console.log('\nPrimer producto:');
        console.log(JSON.stringify(json.value[0], null, 2));
      }
    } catch (e) {
      console.error('❌ Error parseando JSON:', e.message);
      console.log('Respuesta raw:', data.substring(0, 500));
    }
  });
});

req.on('error', (e) => {
  console.error('❌ Error de conexión:', e.message);
});

req.on('timeout', () => {
  console.error('❌ Timeout después de 70 segundos');
  req.destroy();
});

req.end();
