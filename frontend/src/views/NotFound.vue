<template>
  <div class="not-found-container">
    <div class="error-content">
      <h1 class="error-code">404</h1>
      <div class="band-character">
        <img src="@/assets/img/anon-404.gif" alt="Kasumi surprised" class="character-image">
      </div>
      <h2 class="error-message">Oops! Mygo了吗？</h2>
      <p class="error-description">
        像找不到正确的音符一样，这个页面似乎不存在...
      </p>
      <div class="action-buttons">
        <el-button type="danger" class="back-button" @click="goHome">
          <i class="el-icon-arrow-left"></i> 回到主页
        </el-button>
      </div>
    </div>
    <div class="music-notes">
      <span class="note note-1">♪</span>
      <span class="note note-2">♫</span>
      <span class="note note-3">♬</span>
      <span class="note note-4">♩</span>
      <span class="note note-5">♪</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound',
  methods: {
    goHome() {
      this.$router.push('/event');
    }
  }
}
</script>

<style src="@/assets/css/notfound.css"></style>