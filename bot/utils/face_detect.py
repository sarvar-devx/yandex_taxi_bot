import cv2
import numpy as np


async def has_face(bot, file_id: str) -> bool:
    file = await bot.get_file(file_id)
    file_bytes = await bot.download_file(file.file_path)
    np_arr = np.frombuffer(file_bytes.read(), np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    return len(faces) > 0
