<script setup>
import { onMounted, ref } from "vue";

const paymentId = ref(null);
const status = ref(null);

onMounted(async () => {
  const params = new URLSearchParams(window.location.search);

  paymentId.value = params.get("payment_id");
  status.value = params.get("status");

  if (status.value === "approved") {
    await fetch("http://localhost/ai-print-studio/backend/api/save-payment.php", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        payment_id: paymentId.value,
        status: status.value
      })
    });
  }
});
</script>

<template>
  <div>
    <h1 v-if="status === 'approved'">✅ Pago exitoso</h1>
    <h1 v-else>❌ Pago no completado</h1>

    <p>ID de pago: {{ paymentId }}</p>
  </div>
</template>