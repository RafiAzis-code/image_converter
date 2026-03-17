import os
import cv2
import numpy as np
from flask import Flask, render_template, request

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# otomatis buat folder kalau belum ada
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =============================
# PROCESS IMAGE
# =============================
def process_image(image_path):
    # Load gambar
    img = cv2.imread(image_path)

    if img is None:
        raise ValueError("Gambar gagal dibaca!")

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # rata-rata RGB
    avg_rgb = np.mean(img_rgb, axis=(0, 1)).astype(int)

    # grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    avg_gray = int(np.mean(gray))
    
    gray_path = os.path.join(UPLOAD_FOLDER, 'gray_image.jpg')
    cv2.imwrite(gray_path, gray)

    # =============================
    # GRID PROCESSING
    # =============================
    grid_img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    h, w = gray.shape
    rows, cols = 10, 10
    dy, dx = h // rows, w // cols

    for i in range(rows):
        for j in range(cols):
            y1, y2 = i * dy, (i + 1) * dy
            x1, x2 = j * dx, (j + 1) * dx
            
            roi = gray[y1:y2, x1:x2]
            avg_val = int(np.mean(roi))
            
            # grid kotak
            cv2.rectangle(grid_img, (x1, y1), (x2, y2), (255, 0, 0), 1)
            
            # label angka
            cv2.putText(
                grid_img,
                str(avg_val),
                (x1 + 5, y1 + 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (0, 255, 0),
                1
            )

    grid_path = os.path.join(UPLOAD_FOLDER, 'grid_image.jpg')
    cv2.imwrite(grid_path, grid_img)
    
    return avg_rgb, avg_gray


# =============================
# ROUTE
# =============================
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' not in request.files:
            return "Tidak ada file!", 400

        file = request.files['image']

        if file.filename == '':
            return "File kosong!", 400

        # simpan file
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], 'original.jpg')
        file.save(save_path)

        try:
            avg_rgb, avg_gray = process_image(save_path)
        except Exception as e:
            return f"Error processing image: {str(e)}"

        return render_template(
            'index.html',
            original='original.jpg',
            gray='gray_image.jpg',
            grid='grid_image.jpg',
            avg_rgb=avg_rgb,
            avg_gray=avg_gray
        )

    return render_template('index.html')


# =============================
# MAIN
# =============================
if __name__ == '__main__':
    app.run(debug=True)