<template>
    <el-card class="file-card" :style="cardStyle" shadow="hover">
        <div class="file-content">
            <h4>{{ fileName }}</h4>
            <el-progress v-if="file.frames > 0 && file.status === 'encode'" :percentage="progress" :text-inside="true"
                stroke-width="18" />
            <p v-if="formattedDuration">Длительность: {{ formattedDuration }}</p>
        </div>
    </el-card>
</template>

<script>
export default {
    name: "FileItem",
    props: {
        file: {
            type: Object,
            required: true,
        },
    },
    computed: {
        cardStyle() {
            // Цвет карты в зависимости от статуса
            switch (this.file.status) {
                case "encode":
                    return "background-color: #faecd8; border-color: #f3d19e"; // Желтый для encoding
                case "added":
                    return "background-color: #e1f3d8; border-color: #b3e19d"; // Зеленый для добавленных
                case "encoded":
                    return "background-color: #d9ecff; border-color: #a0cfff"; // Синий для закодированных
                default:
                    return "background-color: #e9e9eb; border-color: #c8c9cc"; // Серый по умолчанию
            }
        },
        fileName() {
            // Получаем только имя файла из пути
            return this.file.path.split("\\").pop();
        },
        progress() {
            // Вычисляем процент прогресса
            return Math.round((this.file.frame / this.file.frames) * 100);
        },
        formattedDuration() {
            // Форматируем длительность из секунд в часы:минуты:секунды
            if (this.file.duration === 0) return null;

            const hours = Math.floor(this.file.duration / 3600);
            const minutes = Math.floor((this.file.duration % 3600) / 60);
            const seconds = this.file.duration % 60;

            let formatted = '';

            // Добавляем часы, если они есть
            if (hours > 0) {
                formatted += `${hours}ч `;
            }

            // Добавляем минуты, если они есть
            if (minutes > 0 || hours > 0) {
                formatted += `${minutes}м `;
            }

            // Добавляем секунды всегда
            formatted += `${seconds}с`;

            return formatted.trim();
        },
    },
};
</script>

<style scoped>
.file-card {
    padding: 0px;
    margin: 0px;
    border-radius: 15px;
    margin-bottom: 10px;
}
.file-content {
    padding: 0px;
    margin: 0px;
}
.file-content h4 {
    font-size: 1.2rem;
}

.file-content p {
    font-size: 1rem;
}
</style>