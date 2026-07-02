const API_BASE = 'http://localhost:5000';

//основная функция
async function processImage() {
    const fileInput = document.getElementById('imageInput');
    const file = fileInput.files[0];
    const btn = document.getElementById('processBtn');
    const loading = document.getElementById('loadingText');

    //проверка выбран ли файл
    if (!file) {
        alert('Сначала выберите изображение');
        return;
    }

    //блокировка кнопки на время обработки
    btn.disabled = true;
    loading.style.display = 'inline-block';

    const formData = new FormData();
    formData.append('image', file);

    try {
        //отправка запроса на сервер
        const response = await fetch(`${API_BASE}/predict`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || 'Ошибка сервера');
        }

        const data = await response.json();

        //отображение результата
        showResult(data);

        //обновление истории
        loadHistory();

    } catch (error) {
        alert(' Ошибка: ' + error.message);
    } finally {
        //разблок кнопки
        btn.disabled = false;
        loading.style.display = 'none';
    }
}

//результат
function showResult(data) {
    const resultArea = document.getElementById('resultArea');
    const img = document.getElementById('resultImage');
    const stats = document.getElementById('stats');

    resultArea.classList.add('active');

    img.src = `/static/results/${data.result_image}?${Date.now()}`;

    const count = data.phones_detected;
    stats.innerHTML = `
         Обнаружено телефонов: 
        <strong style="font-size: 28px; color: ${count > 0 ? '#e53e3e' : '#48bb78'};">
            ${count}
        </strong>
    `;
}

//история
async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE}/history`);
        const history = await response.json();
        const list = document.getElementById('historyList');

        //если история пуста
        if (history.length === 0) {
            list.innerHTML = '<li style="color:#a0aec0; justify-content:center;">📭 История пуста</li>';
            return;
        }

        //отрисовка списка
        list.innerHTML = '';
        history.forEach(item => {
            const li = document.createElement('li');
            const date = new Date(item.timestamp).toLocaleString('ru-RU');
            li.innerHTML = `
                <span>
                    <strong>${date}</strong> — ${item.filename}
                </span>
                <span class="badge ${item.phones_detected === 0 ? 'zero' : ''}">
                     ${item.phones_detected}
                </span>
            `;
            list.appendChild(li);
        });
    } catch (error) {
        console.warn('Не удалось загрузить историю:', error);
    }
}

document.addEventListener('DOMContentLoaded', loadHistory);