<template>
    <el-container style="height: 100vh; display: flex;">
        <div class="main-content">
            <el-row justify="center">
                <el-col :span="12">
                    <MediaTabs :media_paths="media_paths" :files="files" />
                </el-col>
            </el-row>
        </div>
    </el-container>
</template>

<script>
import MediaTabs from './MediaTabs.vue';

export default {
    name: 'MainPage',
    components: {
        MediaTabs
    },

    data() {
        return {
            files: [],
            media_paths: [],
            intervalId: null,
        };
    },
    methods: {
        fetchData() {
            this.$axios
                .get('/db/files')
                .then((response) => {
                    this.files = response.data;


                })
                .catch((error) => {
                    console.error('Ошибка при получении файлов:', error);
                });
        },
        getMediaPaths() {
            this.$axios
            .get('/db/paths')
            .then((response) => {
                this.media_paths = response.data.map(item => item.path);
                console.log('media paths: ', this.media_paths);
            })
            .catch((error) => {
                console.error('Ошибка при получении путей:', error);
            });
        }
    },
    mounted() {
        this.getMediaPaths();
        this.fetchData();

        this.intervalId = setInterval(this.fetchData, 5000);
    },
}
</script>

<style>
.main-content {
    text-align: left;
    width: 100%;
}
</style>