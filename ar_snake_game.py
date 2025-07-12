import pygame as pg
import time
import random
import cv2
import numpy as np
import mediapipe as mp
import serial
import ctypes
import config
import json

# 🤚: 위 / ✊: 아래 / ☝️: 왼쪽 / : 오른쪽

port = config.SERIAL_PORT
# Pygame 및 OpenCV 초기화
pg.init()
pg.display.set_caption("스네이크 게임")

ctypes.windll.user32.SetProcessDPIAware()

# 정확한 화면 해상도 가져오기
user32 = ctypes.windll.user32
Width, Height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
# 현재 화면 크기 가져오기 (전체화면)

Screen = pg.display.set_mode(
    (Width, Height), pg.FULLSCREEN | pg.NOFRAME | pg.HWSURFACE | pg.DOUBLEBUF
)

py_serial = serial.Serial(
    # Window
    port=port,
    # 보드 레이트 (통신 속도)
    baudrate=9600,
)

# 게임 설정
CS = 50
SL = 5
Snake = []
X_Dir, Y_Dir = 1, 0
Score = 0
count = 10
Credit = 5
n = 0
grid_width = Width // CS - 10  # 화면 너비에 맞는 열의 수
grid_height = Height // CS  # 화면 높이에 맞는 행의 수
CS = min(Width // grid_width, Height // grid_height)
Px, Py = grid_width // 2, grid_height // 2
dead = True
Ax = random.randint(5, grid_width - 5)
Ay = random.randint(5, grid_height - 5)
# 투명한 스네이크 Surface 생성
snake_surface = pg.Surface((Width, Height), pg.SRCALPHA)

# 폰트 & 사운드 설정
Font_30 = pg.font.Font("font/GeekbleMalang2TTF.ttf", 30)
Font_50 = pg.font.Font("font/GeekbleMalang2TTF.ttf", 50)
Font_80 = pg.font.Font("font/GeekbleMalang2TTF.ttf", 80)
Apple_snd = pg.mixer.Sound("invader_res/laser.wav")
Die_snd = pg.mixer.Sound("invader_res/explosion.wav")

Running = True
Game = False  # 초기에는 게임이 실행되지 않도록 설정
cap = cv2.VideoCapture(0)

# MediaPipe 초기화
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

file = open("./score.json", "r", encoding="utf-8")
score_info = json.load(file)

file.close()


def save_score_to_file(filename, res):
    f = open(filename, "w", encoding="utf-8")
    f.write(res)
    f.close()


# 보드 그리기
def Draw_Board():
    snake_surface.fill((255, 255, 255, 0))  # 투명한 배경 유지
    for r in range(grid_height):
        for c in range(grid_width):
            pg.draw.rect(
                snake_surface, (50, 50, 50), (c * CS + 10, r * CS + 10, CS, CS), 1
            )


# 뱀 그리기
def Draw_Snake():
    for idx, s in enumerate(Snake):
        if idx == 0:
            pg.draw.rect(
                snake_surface, (0, 255, 0), (s[0] * CS + 10, s[1] * CS + 10, CS, CS)
            )
            pg.draw.circle(
                snake_surface,
                (255, 255, 255),
                (s[0] * CS + 10 + 10, s[1] * CS + 10 + 10),
                7,
            )
            pg.draw.circle(
                snake_surface,
                (255, 255, 255),
                (s[0] * CS + 35 + 10, s[1] * CS + 10 + 10),
                7,
            )
            pg.draw.circle(
                snake_surface,
                (0, 0, 0),
                (s[0] * CS + 10 + 10, s[1] * CS + 10 + 10),
                5,
            )
            pg.draw.circle(
                snake_surface,
                (0, 0, 0),
                (s[0] * CS + 35 + 10, s[1] * CS + 10 + 10),
                5,
            )
        else:
            pg.draw.rect(
                snake_surface, (0, 255, 0), (s[0] * CS + 10, s[1] * CS + 10, CS, CS)
            )


# 사과 그리기
def Draw_Apple():
    global Ax, Ay, SL, Score
    if len(Snake) > 0 and Snake[0] == (Ax, Ay):
        while True:
            Ax, Ay = random.randint(3, grid_width - 3), random.randint(
                3, grid_height - 3
            )
            if not (Ax, Ay) in Snake:
                py_serial.write("Apple\n".encode())
                Score += 1
                SL += 1
                Apple_snd.play()

                break
    pg.draw.rect(snake_surface, (255, 0, 0), (Ax * CS + 10, Ay * CS + 10, CS, CS))


def Draw_Score():
    global Font, Score, White_color, Score_Text, Font_30, Font_50, Font_80
    Score_Text = Font_30.render("Score: " + str(Score), True, (0, 0, 255))
    Screen.blit(Score_Text, (grid_width * CS + 20, 10))


def Draw_Credit():
    global Credit
    Credit_Text = Font_30.render("Credit:" + str(Credit), True, (255, 0, 0))
    Screen.blit(Credit_Text, (grid_width * CS + 20, 30 * 2))


def Draw_Info():
    global leaderboard
    text = Font_30.render("------------------------", True, (255, 0, 0))
    Screen.blit(text, (grid_width * CS + 20, 90))
    text = Font_30.render("<조작법>", True, (255, 0, 0))
    Screen.blit(text, (grid_width * CS + 20, 120))

    text = Font_30.render("위: 보자기", True, (255, 0, 0))
    Screen.blit(text, (grid_width * CS + 20, 180))

    text = Font_30.render("아래: 주먹", True, (255, 0, 0))
    Screen.blit(text, (grid_width * CS + 20, 210))

    text = Font_30.render("왼쪽: 검지만 핌", True, (255, 0, 0))
    Screen.blit(text, (grid_width * CS + 20, 240))

    text = Font_30.render("오른쪽: 새끼손가락만 핌", True, (255, 0, 0))
    Screen.blit(text, (grid_width * CS + 20, 270))

    text = Font_30.render("------------------------", True, (0, 255, 0))
    Screen.blit(text, (grid_width * CS + 20, 300))

    text = Font_30.render("Top 5", True, (255, 0, 0))
    Screen.blit(text, (grid_width * CS + 20, 330))

    text = Font_30.render(
        "1. " + str(leaderboard[0]["score"]) + "  -  " + leaderboard[0]["time"],
        True,
        (255, 0, 0),
    )
    Screen.blit(text, (grid_width * CS + 25, 360))

    text = Font_30.render(
        "2. " + str(leaderboard[1]["score"]) + "  -  " + leaderboard[1]["time"],
        True,
        (255, 0, 0),
    )
    Screen.blit(text, (grid_width * CS + 20, 390))

    text = Font_30.render(
        "3. " + str(leaderboard[2]["score"]) + "  -  " + leaderboard[2]["time"],
        True,
        (255, 0, 0),
    )
    Screen.blit(text, (grid_width * CS + 20, 420))

    text = Font_30.render(
        "4. " + str(leaderboard[3]["score"]) + "  -  " + leaderboard[3]["time"],
        True,
        (255, 0, 0),
    )
    Screen.blit(text, (grid_width * CS + 20, 450))

    text = Font_30.render(
        "5. " + str(leaderboard[4]["score"]) + "  -  " + leaderboard[4]["time"],
        True,
        (255, 0, 0),
    )
    Screen.blit(text, (grid_width * CS + 20, 480))


# 뱀 이동 로직
def Move_Snake():
    global Px, Py, X_Dir, Y_Dir, SL, Credit, Running, count, Snake, dead
    Px += X_Dir
    Py += Y_Dir

    # 벽 충돌 시 사망
    if Px < 0 or Px >= grid_width or Py < 0 or Py >= grid_height:
        Credit -= 1
        if Credit > 0:
            py_serial.write("Die\n".encode())
        count = 0
        Px, Py = grid_width // 2, grid_height // 2
        X_Dir, Y_Dir = 0, 0
        Snake = []
        dead = True
        Die_snd.play()

    for s in Snake[1:]:
        if Px == s[0] and Py == s[1] and count >= 5:
            Credit -= 1
            if Credit > 0:
                py_serial.write("Die\n".encode())
            count = 0
            Px, Py = grid_width // 2, grid_height // 2
            X_Dir, Y_Dir = 0, 0
            Snake = []

            dead = True
            Die_snd.play()

    Snake.insert(0, (Px, Py))
    while len(Snake) > SL:
        Snake.pop()
    count += 1


def get_closest_hand(results):
    """가장 가까운 손 하나만 반환 (손목 Y 좌표 기준)"""
    if not results.multi_hand_landmarks:
        return None  # 손이 감지되지 않으면 반환 X

    # 손목 (landmark[0])의 Y 좌표를 기준으로 가장 가까운 손 찾기
    closest_hand = min(
        results.multi_hand_landmarks, key=lambda hand: hand.landmark[0].y
    )
    return closest_hand


# 손 제스처로 방향 제어
def detect_gesture(hand_landmarks):
    global X_Dir, Y_Dir
    if hand_landmarks:
        # 각 손가락의 첫 번째 마디와 손끝의 상대적 위치를 기준으로 판단
        wrist = hand_landmarks[0]  # 손목
        thumb_1st_joint = hand_landmarks[1]  # 엄지 첫번째 마디
        thumb_tip = hand_landmarks[4]  # 엄지 끝
        index_1st_joint = hand_landmarks[5]  # 검지 첫번째 마디
        index_tip = hand_landmarks[8]  # 검지 끝
        middle_1st_joint = hand_landmarks[9]  # 중지 첫번째 마디
        middle_tip = hand_landmarks[12]  # 중지 끝
        ring_1st_joint = hand_landmarks[13]  # 약지 첫번째 마디
        ring_tip = hand_landmarks[16]  # 약지 끝
        pinky_1st_joint = hand_landmarks[17]  # 새끼 첫번째 마디
        pinky_tip = hand_landmarks[20]  # 새끼 끝

        is_thumb_open = thumb_tip.x < thumb_1st_joint.x
        is_index_open = index_tip.y < index_1st_joint.y
        is_middle_open = middle_tip.y < middle_1st_joint.y
        is_ring_open = ring_tip.y < ring_1st_joint.y
        is_pinky_open = pinky_tip.y < pinky_1st_joint.y

        if (
            not is_index_open
            and not is_middle_open
            and not is_ring_open
            and not is_pinky_open
            and not Y_Dir == -1
        ):
            X_Dir = 0
            Y_Dir = 1

        elif (
            is_index_open
            and is_middle_open
            and is_ring_open
            and is_pinky_open
            and not Y_Dir == 1
        ):
            X_Dir = 0
            Y_Dir = -1

        elif (
            is_pinky_open
            and not is_index_open
            and not is_middle_open
            and not is_ring_open
            and not X_Dir == -1
        ):
            X_Dir = 1
            Y_Dir = 0

        elif (
            is_index_open
            and not is_middle_open
            and not is_ring_open
            and not is_pinky_open
            and not X_Dir == 1
        ):
            X_Dir = -1
            Y_Dir = 0


# 게임 시작 전에 손이 인식될 때까지 대기
def wait_for_start():
    global Running, leaderboard
    rock = False
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = np.rot90(frame_rgb)

        frame_rgb_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        results = hands.process(frame_rgb_bgr)

        if results.multi_hand_landmarks:

            for landmarks in results.multi_hand_landmarks:
                # 손 랜드마크 그리기
                mp_drawing.draw_landmarks(
                    frame_rgb_bgr, landmarks, mp_hands.HAND_CONNECTIONS
                )
                hand_landmarks = landmarks.landmark

                if hand_landmarks:
                    # 각 손가락의 첫 번째 마디와 손끝의 상대적 위치를 기준으로 판단
                    wrist = hand_landmarks[0]  # 손목
                    thumb_1st_joint = hand_landmarks[1]  # 엄지 첫번째 마디
                    thumb_tip = hand_landmarks[4]  # 엄지 끝
                    index_1st_joint = hand_landmarks[5]  # 검지 첫번째 마디
                    index_tip = hand_landmarks[7]  # 검지 끝
                    middle_1st_joint = hand_landmarks[9]  # 중지 첫번째 마디
                    middle_tip = hand_landmarks[11]  # 중지 끝
                    ring_1st_joint = hand_landmarks[13]  # 약지 첫번째 마디
                    ring_tip = hand_landmarks[15]  # 약지 끝
                    pinky_1st_joint = hand_landmarks[17]  # 새끼 첫번째 마디
                    pinky_tip = hand_landmarks[19]  # 새끼 끝

                    # 손가락이 펴졌는지 접혔는지 판단
                    is_thumb_open = thumb_tip.x < thumb_1st_joint.x
                    is_index_open = index_tip.y < index_1st_joint.y
                    is_middle_open = middle_tip.y < middle_1st_joint.y
                    is_ring_open = ring_tip.y < ring_1st_joint.y
                    is_pinky_open = pinky_tip.y < pinky_1st_joint.y

                    # 주먹 상태 체크 (모든 손가락이 접혀있는 경우)
                    if (
                        not is_index_open
                        and not is_middle_open
                        and not is_ring_open
                        and not is_pinky_open
                    ):
                        rock = True
                    if rock:
                        if (
                            is_index_open
                            and is_middle_open
                            and is_ring_open
                            and is_pinky_open
                        ):
                            return True

        # OpenCV ndarray를 Pygame Surface로 변환
        frame_rgb_bgr = np.rot90(frame_rgb_bgr)
        frame_rgb_bgr = pg.surfarray.make_surface(frame_rgb_bgr)
        frame_rgb_bgr = pg.transform.scale(
            frame_rgb_bgr, (Width, Height)
        )  # 전체화면에 맞춤

        # 화면에 캠 영상 표시
        Screen.blit(frame_rgb_bgr, (0, 0))  # 캠 영상

        text = Font_50.render(
            "게임 시작을 위해 오른손을 인식시킨 후 주먹을 쥐었다 펴주세요",
            True,
            (255, 0, 0),
        )
        Screen.blit(text, (Width // 2 - 50 * 11 - 30, 50))

        text = Font_50.render(
            "뱀을 조작해 사과를 먹으면 점수가 증가합니다.", True, (255, 0, 0)
        )
        Screen.blit(text, (Width // 2 - 50 * 11 - 30, 250))

        text = Font_50.render(
            "뱀이 벽이나 자기 몸에 부딪히면 죽고 Credit이 감소합니다", True, (255, 0, 0)
        )
        Screen.blit(text, (Width // 2 - 50 * 11 - 30, 310))

        text = Font_50.render("( Credit이 0이 되면 GameOver)", True, (255, 0, 0))
        Screen.blit(text, (Width // 2 - 50 * 11 - 30, 370))

        text = Font_50.render("조작법", True, (0, 255, 0))
        Screen.blit(text, (Width // 2 - 50 * 11 - 30, 500))

        text = Font_50.render("위: 보자기", True, (0, 255, 0))
        Screen.blit(text, (Width // 2 - 50 * 11 - 30, 600))

        text = Font_50.render("아래: 주먹", True, (0, 255, 0))
        Screen.blit(text, (Width // 2 - 50 * 11 - 30, 650))

        text = Font_50.render("왼쪽: 검지만 핌", True, (0, 255, 0))
        Screen.blit(text, (Width // 2 - 50 * 11 - 30, 700))

        text = Font_50.render("오른쪽: 새끼손가락만 핌", True, (0, 255, 0))
        Screen.blit(text, (Width // 2 - 50 * 11 - 30, 750))

        text = Font_50.render("Top 5", True, (255, 0, 0))
        Screen.blit(text, (Width // 2 - 50 * 11 - 30, 850))

        text = Font_50.render(
            "1. " + str(leaderboard[0]["score"]) + "  -  " + leaderboard[0]["time"],
            True,
            (255, 0, 0),
        )
        Screen.blit(text, (Width // 2 - 50 * 11 - 30, 920))

        text = Font_50.render(
            "2. " + str(leaderboard[1]["score"]) + "  -  " + leaderboard[1]["time"],
            True,
            (255, 0, 0),
        )
        Screen.blit(text, (Width // 2 - 50 * 11 - 30, 970))

        text = Font_50.render(
            "3. " + str(leaderboard[2]["score"]) + "  -  " + leaderboard[2]["time"],
            True,
            (255, 0, 0),
        )
        Screen.blit(text, (Width // 2 - 50 * 11 - 30, 1020))

        text = Font_50.render(
            "4. " + str(leaderboard[3]["score"]) + "  -  " + leaderboard[3]["time"],
            True,
            (255, 0, 0),
        )
        Screen.blit(text, (Width // 2 - 50 * 11 - 30, 1070))

        text = Font_50.render(
            "5. " + str(leaderboard[4]["score"]) + "  -  " + leaderboard[4]["time"],
            True,
            (255, 0, 0),
        )
        Screen.blit(text, (Width // 2 - 50 * 11 - 30, 1120))

        pg.display.update()


def Game_Over():
    global Score
    py_serial.write("GameOver\n".encode())
    Screen.fill((0, 0, 0))
    text = Font_80.render("GAME OVER", True, (255, 0, 0))
    Screen.blit(text, (Width // 2 - (80 * 3.5), Height // 2 - 40))
    pg.display.update()
    time.sleep(1.5)
    Screen.fill((0, 0, 0))
    text = Font_80.render(f"Score: {Score}", True, (255, 0, 0))
    Screen.blit(text, (Width // 2 - (80 * 3.5), Height // 2 - 40))
    score_data = {
        "time": time.strftime("%m/%d %H:%M:%S", time.localtime(time.time())),
        "score": Score,
    }
    score_info.append(score_data)
    save_score_to_file("./score.json", json.dumps(score_info))

    pg.display.update()
    time.sleep(2)


# 게임 루프
while Running:
    leaderboard = []
    scores = score_info.copy()
    for i in range(5):
        if len(scores) > 0:
            max = {"time": "", "score": 0}
            for score in scores:
                if max["score"] < score["score"]:
                    max["score"] = score["score"]
                    max["time"] = score["time"]
            leaderboard.append(max)
            scores.remove(max)
        else:
            leaderboard.append("-")

    if wait_for_start():  # 손이 인식될 때까지 대기
        Game = True
        Score = 0
        Credit = 5
        SL, Snake = 5, []
        py_serial.write("Start\n".encode())
        while Game:
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb = np.rot90(frame_rgb)

            frame_rgb_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            results = hands.process(frame_rgb_bgr)

            closest_hand = get_closest_hand(results)

            if closest_hand:
                for landmarks in results.multi_hand_landmarks:
                    # 손 랜드마크 그리기
                    mp_drawing.draw_landmarks(
                        frame_rgb_bgr, landmarks, mp_hands.HAND_CONNECTIONS
                    )
                    # 손 제스처 인식하여 방향 변경
                    detect_gesture(landmarks.landmark)

            # OpenCV ndarray를 Pygame Surface로 변환
            frame_rgb_bgr = np.rot90(frame_rgb_bgr)
            frame_rgb_bgr = pg.surfarray.make_surface(frame_rgb_bgr)
            frame_rgb_bgr = pg.transform.scale(
                frame_rgb_bgr, (Width, Height)
            )  # 전체화면에 맞춤

            # 화면에 캠 영상과 게임 요소 표시
            Screen.blit(frame_rgb_bgr, (0, 0))  # 캠 영상
            Draw_Board()
            Draw_Snake()
            Draw_Apple()
            Draw_Credit()
            Draw_Score()
            Draw_Info()
            Screen.blit(snake_surface, (0, 0))  # 게임 요소 오버레이

            if dead == False:
                Move_Snake()
                n = 0
            else:
                if n < 5:
                    text = Font_80.render("3", True, (255, 0, 0))
                    Screen.blit(text, (Width // 2 - 40, Height // 2 - 40))
                elif n < 10:
                    text = Font_80.render("2", True, (255, 0, 0))
                    Screen.blit(text, (Width // 2 - 40, Height // 2 - 40))
                elif n < 15:
                    text = Font_80.render("1", True, (255, 0, 0))
                    Screen.blit(text, (Width // 2 - 40, Height // 2 - 40))
                else:
                    dead = False
            if Credit == 0:
                Game_Over()

                Game = False
            pg.display.update()
            n += 1
            # print(n)
            time.sleep(0.07)

cap.release()
pg.quit()
