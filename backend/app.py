from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import cv2
import os
import sqlite3
from datetime import datetime
from ultralytics import YOLO

#инициализация приложения
app = Flask(__name__)
CORS(app)

#загрузка модели YOLOv8
model = YOLO('yolov8n.pt')

#пути к папкам
UPLOAD_FOLDER = 'static/uploads/'
RESULT_FOLDER = 'static/results/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

#подключение к БД
def get_db():
    conn = sqlite3.connect('database/history.db')
    return conn

#главная страница
@app.route('/')
def index():
    return render_template('index.html')

#обработка изображения
@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'Изображение не загружено'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400
    
    #сохранение загруженного изображения
    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    #чтение изображения
    img = cv2.imread(filepath)
    
    #детекция объектов
    results = model(img)
    
    #подсчёт телефонов
    phones = 0
    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        if model.names[cls_id] == 'cell phone':
            phones += 1
    
    #визуализация результата
    result_img = results[0].plot()
    result_filename = f'result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
    result_path = os.path.join(RESULT_FOLDER, result_filename)
    cv2.imwrite(result_path, result_img)
    
    #сохранение в историю
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO history (timestamp, filename, phones_detected, result_image)
        VALUES (?, ?, ?, ?)
    ''', (datetime.now().isoformat(), filename, phones, result_filename))
    conn.commit()
    conn.close()
    
    return jsonify({
        'status': 'success',
        'phones_detected': phones,
        'result_image': result_filename
    })

#получение истории
@app.route('/history', methods=['GET'])
def get_history():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM history ORDER BY id DESC LIMIT 50')
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            'id': row[0],
            'timestamp': row[1],
            'filename': row[2],
            'phones_detected': row[3],
            'result_image': row[4]
        })
    
    return jsonify(history)

#запуск сервера
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)