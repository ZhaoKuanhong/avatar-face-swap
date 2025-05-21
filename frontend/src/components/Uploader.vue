<template>
  <hr>
  <div>
    <h2>上传你的头像</h2>

<!--    <div>-->
<!--      <h3>方式一：选择本地图片</h3>-->
<!--      <input type="file" @change="handleLocalFileUpload">-->
<!--      <button @click="uploadLocalFile" :disabled="!localFile || !selectedFace">上传本地图片</button>-->
<!--    </div>-->

    <div>
      <h3>输入 QQ 号获取头像</h3>
        <el-row :gutter="20">
          <el-col :span="16">
            <el-input type="number" v-model="qqNumber" placeholder="输入你的 QQ 号"/>
          </el-col>
          <el-col :span="8">
            <el-button @click="fetchQQAvatar" :disabled="!qqNumber || !selectedFace || qqAvatarLoading">
              {{ qqAvatarLoading ? '获取中...' : '获取 QQ 头像' }}
            </el-button>
          </el-col>
        </el-row>

      <div v-if="qqAvatarUrl">
        <h4>QQ 头像预览:</h4>
        <div>
          <img :src="qqAvatarUrl" alt="QQ Avatar" style="max-width: 100px; max-height: 100px;"/>
        </div>
        <el-button  type="primary" @click="confirmDialogVisible = true" :disabled="qqAvatarUploading" v-loading="qqAvatarUploading">
          {{ '使用此 QQ 头像' }}
        </el-button>

      </div>
      <p v-if="qqAvatarError" class="error">{{ qqAvatarError }}</p>
    </div>

<!--    <p v-if="uploadMessage">{{ uploadMessage }}</p>-->
<!--    <p v-if="uploadError" class="error">{{ uploadError }}</p>-->

    <el-dialog
      v-model="uploadDialogVisible"
      width="75vw"
      style="max-width:500px"
      >
      <el-result
        :icon="uploadResult"
        :title="uploadMessage"
      >
        <template #extra>
          <el-button type="primary" @click="uploadDialogVisible = false">Back</el-button>
        </template>
      </el-result>
    </el-dialog>

    <el-dialog
      v-model="confirmDialogVisible"
      title="请确认您的选择"
      width="75vw"
      style="max-width:500px"
    >
      <div class="image-group">
        <div class="block">
          <img  :src="`${this.selectedFaceUrl}`" :alt="selectedFace" class="face-image" style="height: 100px">
          <span class="demonstration">当前选择大头</span>
        </div>
        <div class="block">
          <img :src="qqAvatarUrl" alt="QQ Avatar" style="width: 100px; height: 100px;"/>
          <span class="demonstration">当前选择头像</span>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="confirmDialogVisible = false">取消</el-button>
          <el-button  type="primary" @click="uploadQQAvatar" :disabled="qqAvatarUploading" v-loading="qqAvatarUploading">
          {{ qqAvatarUploading ? '上传中...' : '确认' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

  </div>
</template>

<script>
import { apiClient } from "@/api/axios.js";

export default {
  props: {
    eventId: {
      type: String,
      required: true,
    },
    selectedFace: {
      type: String,
      default: null,
    },
    selectedFaceUrl:{
      type: String,
      default: null,
    },
  },
  data() {
    return {
      confirmDialogVisible: false,
      uploading: false,
      localFile: null,
      qqNumber: '',
      qqAvatarUrl: null,
      qqAvatarLoading: false,
      qqAvatarError: '',
      qqAvatarUploading: false,
      uploadDialogVisible: false,
      uploadMessage: '',
      uploadError: '',
      uploadedImageUrl: null,
      uploadedFilename: null,
      uploadResult: '',
      baseUrl: import.meta.env.VITE_API_BASE_URL,
    };
  },
  methods: {
    handleLocalFileUpload(event) {
      this.localFile = event.target.files[0];
      this.uploadMessage = '';
      this.uploadError = '';
      this.uploadedImageUrl = null;
      this.uploadedFilename = null;
    },
    async uploadLocalFile() {
      if (!this.localFile) {
        this.uploadError = '请选择一个本地文件';
        return;
      }
      if (!this.selectedFace) {
        this.uploadError = '请先选择一张脸';
        return;
      }

      const formData = new FormData();
      formData.append('file', this.localFile);

      try {
        const response = await apiClient.post(`/upload/${this.eventId}/${this.selectedFace}`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        this.uploadMessage = response.data.message;
        this.uploadedImageUrl = URL.createObjectURL(this.localFile);
        this.uploadedFilename = response.data.filename;
        this.$emit('avatar-uploaded', response.data.filename);
      } catch (error) {
        console.error('本地图片上传失败:', error);
        this.uploadError = '本地图片上传失败，请稍后重试。';
        if (error.response && error.response.data && error.response.data.error) {
          this.uploadError = error.response.data.error;
        }
      }
    },
   async fetchQQAvatar() {
      if (!this.qqNumber) {
        this.qqAvatarError = '请输入 QQ 号';
        return;
      }
      this.qqAvatarLoading = true;
      this.qqAvatarError = '';
      this.qqAvatarUrl = `https://q1.qlogo.cn/g?b=qq&nk=${this.qqNumber}&s=640`;
      this.qqAvatarLoading = false;
      // 浏览器的 <img> 标签会处理图片的加载和错误
    },
    async uploadQQAvatar() {
      if (!this.qqAvatarUrl) {
        this.qqAvatarError = '请先获取 QQ 头像';
        return;
      }
      if (!this.selectedFace) {
        this.uploadError = '请先选择一张脸';
        return;
      }

      this.qqAvatarUploading = true;
      this.uploadMessage = '';
      this.uploadError = '';
      this.uploadedImageUrl = null;
      this.uploadedFilename = null;

      try {
        const uploadResponse = await apiClient.post(`/upload-qq-avatar/${this.eventId}/${this.selectedFace}`, {
          qqNumber: this.qqNumber,
          faceId: this.selectedFace,
          eventId: this.eventId,
        });

        this.uploadMessage = uploadResponse.data.message;
        this.uploadedFilename = `${this.selectedFace.split('.')[0]}.jpg`;
        this.uploadedImageUrl = this.qqAvatarUrl;

        // 添加检查文件存在的轮询
        await this.verifyFileExists();

        // 文件确认存在后，触发上传完成事件
        this.$emit('avatar-uploaded', this.uploadedFilename, this.qqAvatarUrl);
        this.uploadResult = 'success';

      } catch (error) {
        console.error('上传 QQ 头像失败:', error);
        this.uploadError = '上传 QQ 头像失败，请稍后重试。';
        this.uploadResult = 'error';
        if (error.response && error.response.data && error.response.data.error) {
          this.uploadError = error.response.data.error;
        }
      } finally {
        this.qqAvatarUploading = false;
        this.confirmDialogVisible = false;
        this.uploadDialogVisible = true;
      }
    },

    async verifyFileExists() {
      let attempts = 0;
      const maxAttempts = 10;
      const delay = 500; // 500ms

      while (attempts < maxAttempts) {
        try {
          // 尝试获取文件
          const response = await apiClient.head(
              `/events/${this.eventId}/faces/upload/${this.uploadedFilename}`,
              { validateStatus: status => status < 500 }
          );

          if (response.status === 200) {
            console.log('文件已确认存在');
            return true; // 文件存在
          }
        } catch (e) {
          // 忽略错误，继续尝试
        }

        // 等待一段时间后重试
        await new Promise(resolve => setTimeout(resolve, delay));
        attempts++;
      }

      console.warn('无法确认文件是否下载完成');
      return false; // 超时
    }
  },
  emits: ['avatar-uploaded'],
};
</script>

<style scoped>
.image-group .block {
  padding: 30px 0;
  text-align: center;
  border-right: solid 1px var(--el-border-color);
  display: inline-block;
  width: 49%;
  box-sizing: border-box;
  vertical-align: top;
}
.image-group .block:last-child {
  border-right: none;
}
.image-group .demonstration {
  display: block;
  color: var(--el-text-color-secondary);
  font-size: 14px;
  margin-bottom: 20px;
}
.error {
  color: red;
}
hr {
  margin: 20px 0;
  border: 0;
  border-top: 1px solid #ccc;
}
</style>