# AR Snake Game

AR(증강현실) 환경에서 손 제스처로 조작하는 스네이크 게임입니다.
MediaPipe를 이용한 손 모양 인식, OpenCV를 통한 실시간 카메라 배경,
Pygame을 활용한 인터페이스, 그리고 Arduino와의 시리얼 통신까지 통합된 프로젝트입니다.



## 주요 기능

* 손 제스처(보자기, 주먹, 검지만, 새끼손가락)로 상하좌우 조작
* 사과를 먹으면 점수와 뱀 길이 증가
* 벽이나 자기 몸에 충돌하면 생명(Credit) 감소
* 점수 상위 5개 저장 및 화면에 실시간 표시
* 시리얼 통신으로 Arduino와 연동 가능 (게임 상태 전송)



## 실행 환경

* Windows 운영체제 (전체화면 해상도 자동 인식)
* Python 3.8 이상
* 웹캠 필수

### 필수 패키지 설치

```bash
pip install pygame opencv-python mediapipe pyserial numpy
```



## 디렉토리 구조

```
ar_snake_game/
├── ar_snake_game.py           # 메인 실행 파일
├── config.py                  # 시리얼 포트 설정 파일
├── score.json                 # 점수 기록 저장
├── font/
│   └── GeekbleMalang2TTF.ttf  # 게임 UI 폰트
├── invader_res/
│   ├── laser.wav              # 사과 획득 사운드
│   └── explosion.wav          # 충돌 사운드
└── README.md
```



## 조작 방법

| 제스처               | 동작     |
| ----------------- | ------ |
| 보자기 (손가락 다 핀 상태)  | 위쪽 이동  |
| 주먹 (손가락 모두 접은 상태) | 아래쪽 이동 |
| 검지만 핀 상태          | 왼쪽 이동  |
| 새끼손가락만 핀 상태       | 오른쪽 이동 |

* 게임 시작 전: 주먹을 쥔 후 손을 펴면 게임이 시작됩니다.



## 순위 시스템

* 최고 점수 5개가 `score.json`에 저장됩니다.
* 게임 시작 화면과 우측 UI에 실시간으로 표시됩니다.



## Arduino 연동

시리얼 포트를 통해 다음 메시지가 전송됩니다:

* `Start` – 게임 시작
* `Apple` – 사과 획득
* `Die` – 충돌 발생
* `GameOver` – 생명 0으로 게임 종료

`config.py` 예시:

```python
SERIAL_PORT = "COM3"  # Windows 기준 포트 번호 설정
```

## 실행화면

x

## 라이선스

MIT License
