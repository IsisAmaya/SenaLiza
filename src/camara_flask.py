"""
Este módulo captura video de la cámara, procesa los frames usando Mediapipe y un modelo de 
PyTorch para predecir letras en lenguaje de señas.
"""

import cv2  # pylint: disable=no-member
import mediapipe as mp
import numpy as np
import torch
import torch.nn.functional as F


# Cargar el modelo de PyTorch
model_global = torch.load(
    r"D:\Universidad\Septimo Semestre\Proyecto Integrador II\proyecto\SenaLiza\src\senalizaV5.pt",
    map_location=torch.device("cpu"),
)
model_global.eval()

mp_hands = mp.solutions.hands
hands_global = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

letter_pred_global = [
    "A", "B", "C", "D", "E", "F", "H", "I", "K", "L", "M", "N", "O", "P", "Q", 
    "R", "T", "U", "V", "W", "X", "Y",
]


def initialize_camera():
    """Inicializa la cámara."""
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # pylint: disable=no-member
    return cap


def process_frame(frame, model, hands, letter_pred):  # pylint: disable=too-many-locals
    """Procesa el frame capturado y devuelve la predicción."""
    height, width, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # pylint: disable=no-member
    result = hands.process(frame_rgb)
    hand_landmarks = result.multi_hand_landmarks

    if hand_landmarks:
        for hand_landmarks_set in hand_landmarks:
            x_max, y_max, x_min, y_min = 0, 0, width, height
            for landmark in hand_landmarks_set.landmark:
                x_coord, y_coord = int(landmark.x * width), int(landmark.y * height)
                x_max, x_min = max(x_coord, x_max), min(x_coord, x_min)
                y_max, y_min = max(y_coord, y_max), min(y_coord, y_min)

            y_min -= 20
            y_max += 20
            x_min -= 20
            x_max += 20

            analysis_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # pylint: disable=no-member
            analysis_frame = analysis_frame[y_min:y_max, x_min:x_max]
            analysis_frame = cv2.resize(analysis_frame, (64, 64))  # pylint: disable=no-member
            analysis_frame = (
                torch.tensor(analysis_frame, dtype=torch.float32)
                .unsqueeze(0)
                .unsqueeze(0)
                / 255.0
            )
            analysis_frame = analysis_frame.repeat(1, 3, 1, 1)

            with torch.no_grad():
                prediction = model(analysis_frame)
                prediction = F.softmax(prediction, dim=1)
                pred_array = prediction.numpy()[0]
                letter_prediction = letter_pred[np.argmax(pred_array)]

            # Dibujar predicción en el frame
            cv2.putText(
                frame,
                f"Pred: {letter_prediction}",
                (x_min, y_min - 10),
                cv2.FONT_HERSHEY_SIMPLEX,  # pylint: disable=no-member
                1,
                (0, 0, 255),  # pylint: disable=no-member
                2,
            )

    return frame
