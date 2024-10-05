<template>
    <el-container style="height: 100vh; display: flex;">
        <div class="main-content">
            <el-row justify="center">
                <el-col :span="12">
                    <h1>Медиатека:</h1>
                    <el-container>
                        <el-header style="height: 20px;">Кодируется</el-header>
                        <el-main>
                            <div v-for="(file, index) in encode_files" :key="index">
                                <FileItem :file="file" />
                            </div>
                        </el-main>
                    </el-container>
                    <el-container>
                        <el-header style="height: 20px;">В очереди</el-header>
                        <el-main>
                            <div v-for="(file, index) in added_files" :key="index">
                                <FileItem :file="file" />
                            </div>
                        </el-main>
                    </el-container>
                    <el-container>
                        <el-header style="height: 20px;">Закодировано</el-header>
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
            added_files: null,
            encode_files: null,
            encoded_files: null,
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
                    this.encode_files = files.filter(file => file.status === 'encode');
                    this.encoded_files = files.filter(file => file.status === 'encoded');
                })
                .catch((error) => {
                    console.error('Ошибка при получении файлов:', error);
                });
        },
    },
    mounted() {
        // Запускаем функцию сразу при монтировании компонента
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