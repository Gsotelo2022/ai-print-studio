<template>
  <section class="hero-showcase-root">
    <div class="bg-logo" aria-hidden="true"></div>
    <div class="hero-inner">
      <div class="text-block">
        <h1 class="title">Diseños Únicos a tu estilo</h1>
        <p class="subtitle">Crea tus propias estampas personalizables subiendo tus ideas e imágenes, y deja que nuestra IA te ayude a generar diseños únicos.</p>
      </div>

      <div class="showcase-visual">
        <div class="circle">
          <img src="../assets/calabera.png" alt="Calabera" class="calabera" />
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
// no logic necesario por ahora
</script>

<style scoped>
.hero-showcase-root {
  position: relative;
  padding: 60px 0 40px;
  min-height: 420px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.hero-showcase-root .bg-logo {
  position: absolute;
  right: 48px;
  top: 40px;
  width: 420px;
  height: 420px;
  background-image: url('../assets/background.png');
  background-size: cover;
  background-position: center;
  opacity: 0.10;
  border-radius: 50%;
  filter: blur(2px) saturate(0.9);
  pointer-events: none;
}
.hero-inner {
  max-width: 1100px;
  width: 100%;
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 48px;
  align-items: center;
  z-index: 2;
}
.text-block .title {
  font-size: 36px;
  color: var(--color-primary);
  margin-bottom: 12px;
  font-weight: 900;
}
.text-block .subtitle {
  color: var(--color-text-light);
  line-height: 1.6;
}
.showcase-visual {
  display: flex;
  align-items: center;
  justify-content: center;
}
.circle {
  width: 360px;
  height: 360px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(15,17,36,0.6), rgba(6,182,212,0.06));
  box-shadow: 0 20px 40px rgba(0,0,0,0.35);
  border: 6px solid rgba(255,255,255,0.04);
  overflow: hidden;
}
.calabera {
  width: 240px;
  height: auto;
  object-fit: contain;
}

@media (max-width: 900px) {
  .hero-inner { grid-template-columns: 1fr; gap: 28px; }
  .hero-showcase-root .bg-logo { display: none; }
  .circle { width: 320px; height: 320px; }
}

@media (max-width: 480px) {
  .text-block .title { font-size: 28px; }
  .circle { width: 220px; height: 220px; }
  .calabera { width: 160px; }
}
</style>
