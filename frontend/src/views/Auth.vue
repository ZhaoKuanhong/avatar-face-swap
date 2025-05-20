<template>
	<body>
        <!-- 参考：https://www.bilibili.com/video/BV1s94y1S7f2?spm_id_from=333.337.search-card.all.click&vd_source=3bc1dd4a42012fa273cf171a6833d07b -->
		<div class="container">
            <h2>Login</h2>
            <div class="input-container">
                <label for="password">密码</label>
                <input type="password" v-model="token" placeholder="输入口令">
            </div>
            <div class="button-container">
                <div>
                    <button @click="verifyToken" :disabled="loading" >验证</button>
                </div>
            </div>
        </div>
	</body>
</template>

<script>
import { useRouter } from 'vue-router';
import {apiClient} from "@/api/axios.js";

export default {
  data() {
    return {
      token: '',
      loading: false,
      errorMessage: '',
    };
  },
  setup() {
    const router = useRouter();
    return { router };
  },
  methods: {
    async verifyToken() {
      this.loading = true;
      try {
        const response = await apiClient.post('/verify', { token: this.token });
        if (response.data.token) {
          localStorage.setItem('token', response.data.token);
        }
        if (response.data.description) {
          localStorage.setItem('description', response.data.description);
        }
        await this.router.push(`/event/${response.data.event_id}`);
      } catch (error) {
        this.errorMessage = '口令验证失败，请重试。';
        if (error.response && error.response.data && error.response.data.error) {
          this.errorMessage = error.response.data.error;
            ElNotification({
            title: 'Error',
            message: this.errorMessage,
            type: 'error',
          })
        }
      } finally {
        this.loading = false;
      }
    }
    },
};
</script>

<style scoped>
* {
    margin: 0;
    padding: 0;
    /* font-family: 'Courier New', Courier, monospace; */
    /* letter-spacing: 1px; */
}

body {
    /* border: 2px solid red; */
    display: flex;
    /* flex-direction: column; */
    align-items: center;
    justify-content: center;
    height: 100vh;
    width: 100vw;
    background: url("../assets/img/bg.jpg") no-repeat;
    background-size: cover;
}

div.container {
    backdrop-filter: blur(10px);
    background: rgba(50, 50, 50, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.5);
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 300px;
    width: 300px;
    border-top: 1px solid rgba(255, 255, 255, 0.5);
    border-left: 1px solid rgba(255, 255, 255, 0.5);
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    border-right: 1px solid rgba(255, 255, 255, 0.2);
    letter-spacing: 1px;
}

div.container > h2 {
    /* border: 1px solid red; */
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: 5px;
    letter-spacing: 2px;
    /* text-transform: uppercase; */
    user-select: none;
}

div.container > div.input-container {
    /* border: 1px solid black; */
    /* padding: 5px;
    margin: 5px; */
    margin-bottom: 5px;
    display: flex;
    flex-direction: column;
    /* width: 260px;
    height: 260px; */
    justify-content: center;
    align-items: start;
}

div.container > div.input-container > label {
    margin-bottom: 5px;
    color: rgba(255, 255, 255, 0.8);
    font-size: 15px;
    cursor: pointer;
    user-select: none;
}

div.container > div.input-container > input {
    box-sizing: border-box;
    color: rgba(255, 255, 255, 0.8);
    font-size: 15px;
    height: 35px;
    width: 250px;
    background: rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.5);
    /* border: none; */
    padding: 10px;
    border-radius: 5px;
    transition: 0.5s;
    outline: none;
    letter-spacing: 1px;
}

div.container > div.input-container > input:focus {
    border: 1px solid rgba(255, 255, 255, 1);
}

div.container > div.button-container {
    /* border: 1px solid black; */
    width: 250px;
    /* height: 100px; */
    display: flex;
    flex-direction: column;
    align-items: start;
    justify-content: center;
}

div.container > div.button-container > a {
    /* border: 1px solid red; */
    width: 100%;
    font-size: 15px;
    text-decoration: none;
    color: rgba(255, 255, 255, 0.6);
    transition: 0.2s;
    user-select: none;
    text-align: end;
}

div.container > div.button-container >a:hover {
    color: rgba(255, 255, 255, 1);
}

div.container > div.button-container > div {
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: start;
    margin-top: 10px;
}

div.container > div.button-container > div > button {
    width: 120px;
    height: 35px;
    border: 1px solid rgba(255, 255, 255, 0.6);
    background: rgba(46, 66, 94, 0.4);
    color: rgba(255, 255, 255, 0.8);
    border-radius: 5px;
    cursor: pointer;
    transition: 0.6s;
}

div.container > div.button-container > div > button:nth-of-type(2) {
    margin-left: 10px;
}

div.container > div.button-container > div > button:hover {
    border: 1px solid rgba(255, 255, 255, 1);
    background: rgba(46, 66, 94, 0.8);
}

.error {
  color: red;
}
</style>