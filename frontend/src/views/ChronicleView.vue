<template>
  <main class="chronicle-page">
    <section class="chronicle-card">
      <p class="section-kicker">HAKIMI CHRONICLE</p>

      <h1>编年史</h1>

      <div class="coming-box">
        <div class="icon">🐱</div>
        <h2>该功能正在开发</h2>
        <p>敬请期待</p>
      </div>

      <RouterLink class="back-button" to="/">返回首页 →</RouterLink>
    </section>
  </main>
</template>

<style scoped>
.chronicle-page {
  display: flex;
  min-height: calc(100vh - 120px);
  align-items: center;
  justify-content: center;
  padding: 100px 24px;
}

.chronicle-card {
  width: min(900px, 100%);
  padding: 70px;
  border-radius: 40px;
  background: #2c312d;
  color: white;
  box-shadow: 0 30px 70px rgba(35, 40, 35, 0.22);
}

.section-kicker {
  margin: 0 0 15px;
  color: #f6d35d;
  font-size: 14px;
  font-weight: 900;
  letter-spacing: 0.15em;
}

h1 {
  margin: 0;
  font-size: 64px;
  letter-spacing: -0.06em;
}

.coming-box {
  margin-top: 50px;
  padding: 50px;
  border-radius: 32px;
  background: rgba(255, 255, 255, 0.08);
  text-align: center;
}

.icon {
  font-size: 60px;
}

.coming-box h2 {
  margin: 25px 0 0;
  font-size: 32px;
}

.coming-box p {
  margin: 15px 0 0;
  color: #f6d35d;
  font-size: 20px;
}

.back-button {
  display: inline-flex;
  margin-top: 40px;
  padding: 15px 30px;
  border-radius: 999px;
  background: #f6d35d;
  color: #292929;
  font-weight: 900;
  text-decoration: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.back-button:hover {
  box-shadow: 0 10px 0 #d8b845;
  transform: translateY(-2px);
}

@media (max-width: 620px) {
  .chronicle-page {
    padding: 48px 16px 80px;
  }

  .chronicle-card {
    padding: 38px 26px;
    border-radius: 30px;
  }

  h1 {
    font-size: 46px;
  }

  .coming-box {
    margin-top: 34px;
    padding: 36px 20px;
  }

  .coming-box h2 {
    font-size: 26px;
  }
}
</style>
