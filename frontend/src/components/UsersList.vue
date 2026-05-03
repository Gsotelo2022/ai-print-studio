<template>
  <section class="users-section">
    <div class="panel">
      <h3>Usuarios</h3>
      <div v-if="loading">Cargando usuarios...</div>
      <div v-else-if="error" class="error">Error: {{ error }}</div>
      <table v-else class="users-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Email</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.Id">
            <td>{{ u.Id }}</td>
            <td>{{ u.Nombre }}</td>
            <td>{{ u.Email }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useApi } from '../composables/useApi'

const { loading, error, get } = useApi()

const users = ref([])

async function loadUsers() {
  try {
    users.value = await get('/admin/clientes')
  } catch (err) {
    // error ya queda en el composable
    console.error(err)
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.users-section { padding: 16px; }
.panel { background: rgba(15,23,36,0.7); padding: 16px; border-radius: 8px; }
.users-table { width: 100%; border-collapse: collapse; }
.users-table th, .users-table td { padding: 8px 12px; border-bottom: 1px solid rgba(255,255,255,0.04); text-align: left; }
.error { color: #ffd54f; }
</style>
