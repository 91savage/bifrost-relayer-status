# bifrost-status #

바이프로스트 Relayer의 Account Balance 상태 조회와, unbonding 을 위한 상태 알림을 해주는 bot 입니다.

### 사용 버전 및 라이브러리 ###

* Python 3.11
* python-telegram-bot 20.2
* web3 = 6.5.0
* setuptools = 68.0.0
* substrate-interface = 1.7.3


### 운영환경 설치 방법 ###

1. Docker 설치
    - https://docs.docker.com/engine/install/

2. Docker-Compose 설치
    - https://docs.docker.com/compose/install/

3. Git Clone 및 Build
    - git clone git@bitbucket.org:coinplugin/bifrost-relayer-bot.git
    - cd bifrost-relayer-bot
    - docker build -t bifrost-relayer-bot .

4. init & Run
    - cp env-example .env
    - vim .env
    -   TELEGRAM_BOT_TOKEN =
        chat_id = 
        group_id = 
    - 3개 값 입력 후 저장
    - docker-compose up -d

5. 구동 확인
    - docker ps -a 
    - docker-compose logs -f

### 개발환경 방법 ###

1. Python 3.11 및 Poetry 설치
    - https://python-poetry.org/docs/

2. poetry-dotenv-plugin 설치
    - poetry self add poetry-dotenv-plugin

3. env-example로 .env 파일 생성 및 수정
    - cp env-example .env
    - vim .env // 이후 텔레그램 봇 토큰 추가

4. 의존성 설치
    - poetry install

5. 실행
    - poetry shell
    - poetry update
    - python relayer_alert.py // 실행

### 명령어 목록 ###

1. 상태 확인 관련
    - /help - 명령어 목록
    - /balance - 현재 Balance 확인
    - /request - 출금신청 여부 확인 (라운드당 12시간)



### 작업 예정 목록 ###

1. 소켓통신으로 알람 받기
