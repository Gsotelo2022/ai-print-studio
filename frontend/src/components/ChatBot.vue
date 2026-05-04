<template>
  <div class="chat-container">

    <!-- BOTÓN FLOTANTE -->
    <button class="chat-toggle" @click="toggleChat">
      💬
    </button>

    <!-- PANEL CHAT -->
    <div v-if="open" class="chat-box">

      <!-- HEADER -->
      <div class="chat-header">
        <span>Agente que te guIA<span class="stat-icon">🤖</span></span>
        <button @click="toggleChat">✖</button>
      </div>

      <!-- MENSAJES -->
      <div class="chat-messages" ref="messagesContainer">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message', msg.role, { formatted: msg.isFormatted }]"
        >
          <div v-if="msg.isFormatted && msg.datos" class="response-data">
            <div class="data-item">
              <span class="data-label">📋 Respuesta:</span>
              <span class="data-value">{{ msg.text }}</span>
            </div>
            <div v-if="msg.datos.pregunta_interpretada" class="data-item">
              <span class="data-label">🔍 Interpretada como:</span>
              <span class="data-value">{{ msg.datos.pregunta_interpretada }}</span>
            </div>
            <!-- <div v-if="msg.datos.similitud" class="data-item">
              <span class="data-label">✅ Coincidencia:</span>
              <span class="data-value">{{ (msg.datos.similitud * 100).toFixed(0) }}%</span>
            </div> -->
          </div>
          <div v-else class="text-message">
            {{ msg.text }}
          </div>
        </div>

        <!-- LOADING -->
        <div v-if="loading" class="message bot">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>

      <!-- INPUT -->
      <div class="chat-input">
        <input
          v-model="input"
          @keyup.enter="enviarMensaje"
          placeholder="Escribí tu consulta..."
        />
        <button @click="enviarMensaje" :disabled="loading">
          ➤
        </button>
      </div>

    </div>
  </div>
</template>

<script>
export default {
  name: "ChatBot",

  data() {
    return {
      open: false,
      input: "",
      loading: false,
      messages: [
        {
          role: "bot",
          text: "Hola 👋 ¿En qué puedo ayudarte con tus pedidos?"
        }
      ]
    }
  },

  computed: {
    userId() {
      // Obtener user_id del localStorage (guardado en login)
      return parseInt(localStorage.getItem('userId')) || 2
    }
  },

  methods: {
    toggleChat() {
      this.open = !this.open
    },

    formatearRespuesta(respuesta) {
      if (!respuesta) return "Sin respuesta";
      
      // Si es un número o texto muy corto
      if (respuesta.length < 100 && !isNaN(respuesta)) {
        return `📊 ${respuesta}`;
      }
      
      // Si contiene saltos de línea, es probablemente múltiples campos
      if (respuesta.includes("\n")) {
        return respuesta;
      }
      
      return respuesta;
    },

    async enviarMensaje() {
      if (!this.input || !this.input.trim()) return;

      const mensajeUsuario = this.input;

      // Mensaje del usuario
      this.messages.push({
        role: "user",
        text: mensajeUsuario,
        isFormatted: false
      });

      this.input = "";
      this.loading = true;

      try {
        const response = await fetch("http://localhost:5005/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            mensaje: mensajeUsuario,
            user_id: this.userId
          })
        });

        const data = await response.json();
        const respuestaFormateada = this.formatearRespuesta(data.respuesta);

        this.messages.push({
          role: "bot",
          text: respuestaFormateada || "No hubo respuesta",
          isFormatted: true,
          datos: data
        });

      } catch (error) {
        this.messages.push({
          role: "bot",
          text: "❌ Error conectando con el servidor",
          isFormatted: false
        });

        console.error(error);
      } finally {
        this.loading = false;
      }

      this.scrollToBottom();
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer;
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
    }
  }
}
</script>

<style scoped>
.chat-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* BOTÓN FLOTANTE */
.chat-toggle {
  background: linear-gradient(135deg, #06b6d4, #0b7285);
  color: white;
  border: 2px solid #ffd54f;
  padding: 16px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-toggle:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(6, 182, 212, 0.5);
}

/* PANEL CHAT */
.chat-box {
  width: 380px;
  height: 550px;
  background: rgba(7, 18, 38, 0.95);
  border: 2px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  margin-bottom: 15px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5),
              0 0 0 1px rgba(255, 255, 255, 0.06);
  overflow: hidden;
  backdrop-filter: blur(10px);
}

/* HEADER */
.chat-header {
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(11, 114, 133, 0.2));
  border-bottom: 2px solid rgba(255, 255, 255, 0.06);
  color: #e6eef8;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 700;
  font-size: 14px;
  letter-spacing: 0.5px;
}

.chat-header button {
  background: transparent;
  border: none;
  color: #e6eef8;
  font-size: 18px;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.chat-header button:hover {
  opacity: 1;
}

/* ÁREA DE MENSAJES */
.chat-messages {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background: linear-gradient(180deg, #071226, rgba(15, 23, 36, 0.8));
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #06b6d4;
  border-radius: 3px;
}

/* BURBUJA DE MENSAJE */
.message {
  padding: 12px 14px;
  border-radius: 10px;
  max-width: 90%;
  word-wrap: break-word;
  font-size: 13px;
  line-height: 1.5;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* MENSAJE DEL USUARIO */
.message.user {
  background: linear-gradient(135deg, #06b6d4, #0b7285);
  color: white;
  margin-left: auto;
  border-bottom-right-radius: 4px;
  box-shadow: 0 2px 8px rgba(6, 182, 212, 0.2);
}

/* MENSAJE DEL BOT */
.message.bot {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.06);
  color: #e6eef8;
  margin-right: auto;
  border-bottom-left-radius: 4px;
}

/* RESPUESTA FORMATEADA */
.response-data {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.data-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.data-label {
  font-weight: 600;
  color: #ffd54f;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.data-value {
  color: #e6eef8;
  font-size: 13px;
  padding-left: 10px;
  border-left: 2px solid #06b6d4;
}

.text-message {
  word-break: break-word;
  white-space: pre-wrap;
}

/* INDICADOR DE ESCRITURA */
.typing-indicator {
  display: flex;
  gap: 4px;
  align-items: center;
  height: 20px;
}

.typing-indicator span {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #06b6d4;
  animation: bounce 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%, 80%, 100% {
    opacity: 0.3;
    transform: translateY(0);
  }
  40% {
    opacity: 1;
    transform: translateY(-8px);
  }
}

/* ÁREA DE INPUT */
.chat-input {
  display: flex;
  border-top: 2px solid rgba(255, 255, 255, 0.06);
  background: rgba(7, 18, 38, 0.5);
}

.chat-input input {
  flex: 1;
  border: none;
  padding: 12px 14px;
  background: transparent;
  color: #e6eef8;
  outline: none;
  font-size: 13px;
  font-family: inherit;
}

.chat-input input::placeholder {
  color: #a0aec0;
}

.chat-input input:focus {
  background: rgba(6, 182, 212, 0.05);
}

.chat-input button {
  border: none;
  background: transparent;
  color: #06b6d4;
  padding: 12px 16px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
  border-left: 2px solid rgba(255, 255, 255, 0.06);
}

.chat-input button:hover:not(:disabled) {
  color: #ffd54f;
  background: rgba(6, 182, 212, 0.1);
}

.chat-input button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>