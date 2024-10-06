<template>
    <el-container style="height: 100vh; display: flex;">
        <div class="main-content">
            <el-row justify="center">
                <el-col :span="12">
                    <h1>{{ media_paths }}</h1>
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
                </el-col>
            </el-row>
        </div>
    </el-container>
</template>

<script>
import FileItem from './FileItem.vue';

export default {
    name: 'MainPage',
    components: {
        FileItem
    },

    data() {
        return {
            added_files: [],
            encode_files: [],
            encoded_files: [],
            media_paths: null,
            intervalId: null,
        };
    },
    methods: {
        fetchData() {
            this.$axios
                .get('/db/files') // Один запрос для получения всех файлов
                .then((response) => {
                    const files = response.data;

                    // Рассортируем файлы по статусу
                    this.added_files = files.filter(file => file.status === 'added');
                    console.log(this.added_files);
                    this.encode_files = files.filter(file => file.status === 'encode');
                    this.encoded_files = files.filter(file => file.status === 'encoded');
                })
                .catch((error) => {
                    console.error('Ошибка при получении файлов:', error);
                });
        },
        getMediaPaths() {
            this.$axios
            .get('/db/paths')
            .then((response) => {
                this.media_paths = response.data[0].path;
            })
            .catch((error) => {
                console.error('Ошибка при получении путей:', error);
            });
        }
    },
    mounted() {
        // Запускаем функцию сразу при монтировании компонента
        this.getMediaPaths();
        this.fetchData();

        // Устанавливаем интервал для повторного запуска fetchData каждые 5 секунд
        this.intervalId = setInterval(this.fetchData, 5000);
    },
}
</script>

<style>
.main-content {
    text-align: left;
    /* Центрируем текст */
    width: 100%;
    /* Заполняем всю ширину колонки */
}
</style>