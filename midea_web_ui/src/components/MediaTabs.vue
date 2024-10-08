<template>
  <el-tabs v-model="activeTab">
    <el-tab-pane v-for="(path, index) in media_paths" :key="index" :label="path.split('/').pop()" :name="path">
      <el-container v-if="encode_files.length > 0">
        <el-header style="height: 20px;">Кодируется</el-header>
        <el-main>
          <div v-for="(file, index) in encode_files" :key="index">
            <FileItem :file="file" />
          </div>
        </el-main>
      </el-container>
      <el-container v-if="added_files.length > 0">
        <el-header style="height: 20px;">В очереди</el-header>
        <el-main>
          <div v-for="(file, index) in added_files" :key="index">
            <FileItem :file="file" />
          </div>
        </el-main>
      </el-container>
      <el-container v-if="encoded_files.length > 0">
        <el-header style="height: 20px;">Завершено</el-header>
        <el-main>
          <div v-for="(file, index) in encoded_files" :key="index">
            <FileItem :file="file" />
          </div>
        </el-main>
      </el-container>
    </el-tab-pane>
  </el-tabs>
</template>

<script>
import FileItem from './FileItem.vue';

export default {
  name: 'MediaTabs',
  components: {
    FileItem
  },
  props: {
    files: {
      type: Array,
      required: true,
    },
    media_paths: {
      type: Array,
      required: true,
    }
  },
  data() {
    return {
      added_files: [],
      encode_files: [],
      encoded_files: [],
      activeTab: '',
    }
  },
  mounted() {
    if (this.media_paths.length > 0) {
      this.activeTab = this.media_paths[0];
    }
    console.log(this.media_paths);
    this.filterFiles();
  },
  methods: {
    filterFiles() {
      this.added_files = this.files.filter(file => file.status === 'added');
      this.encode_files = this.files.filter(file => file.status === 'encode');
      this.encoded_files = this.files.filter(file => file.status === 'encoded');
    }
  },
  watch: {
    files: {
      handler() {
        this.filterFiles();
      },
      immediate: true,
      deep: true
    },

    media_paths: {
      handler(newPaths) {
        // Обновляем активную вкладку, когда обновляются media_paths
        if (newPaths.length > 0 && !this.activeTab) {
          this.activeTab = newPaths[0];
        }
      },
      immediate: true
    }
  }
};
</script>