<template>
    <el-container>
      <el-header style="width: 100vw">
          <h1>“{{ description }}”大头自助上传</h1>
      </el-header>
      <el-main>
        <face-selector :event-id="event_id" @face-selected="handleFaceSelected" />
        <uploader :event-id="event_id" :selected-face="selectedFace" :selected-face-url="selectedFaceUrl"  @avatar-uploaded="handleAvatarUploaded" />
      </el-main>
    </el-container>
</template>

<script>
import FaceSelector from '../components/FaceSelector.vue';
import Uploader from '../components/Uploader.vue';

export default {
  components: {
    FaceSelector,
    Uploader,
  },
  props: {
    event_id: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      selectedFace: null,
      uploadedAvatar: null,
      selectedFaceUrl: null,
      description: localStorage.getItem('description')
    };
  },
  methods: {
     handleFaceSelected(face, url) {
      this.selectedFace = face;
      this.selectedFaceUrl = url; // Assign the URL received from FaceSelector
      console.log('Parent received face:', this.selectedFace, 'URL:', this.selectedFaceUrl);
    },
    handleAvatarUploaded(filename) {
      this.uploadedAvatar = filename;
    },
  },
};
</script>

<style>

</style>