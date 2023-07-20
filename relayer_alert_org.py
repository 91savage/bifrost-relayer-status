import telegram
import asyncio
import datetime
from web3 import Web3
import os
# from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes,CommandHandler
from telegram import Update


#load.env (docker 용)
token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = int(os.getenv('chat_id'))
group_id= os.getenv('group_id')

# load_dotenv()

# ## my_chat ID
# chat_id = int(os.environ.get('chat_id'))
# ## 채팅방 ID
# group_id = os.environ.get('group_id')
# token = os.environ.get('TELEGRAM_BOT_TOKEN')

relayerAddress = '0x0705D5b6804C022E5c10AbBa86186de5f59A42a8'
bot = telegram.Bot(token)
w3 = Web3(Web3.HTTPProvider('https://public-01.mainnet.thebifrost.io/rpc'))


## 로그 폴더 경로
folder = "logs"
## 로그 파일 리스트
file_list =os.listdir(folder)
## 마지막 로그 파일 시간 체크
latest_file = max(file_list, key=lambda f: os.path.getctime(os.path.join(folder, f)))
    

# balance 체크
async def check_balance():
    global balance
    balance = round(w3.from_wei(w3.eth.get_balance(relayerAddress),'ether'),2)  
    if balance < 1000:
        await time_check()
    else :
        pass

## 알림 시간 체크
async def time_check():
    ## 현재 시간
    now = datetime.datetime.now()
    timestamp_now = now.strftime('%Y-%m-%d %H:%M:%S')
    ## 마지막 파일 +7일
    after7 = datetime.datetime.strptime(latest_file, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(days=7)
    str_after7 = after7.strftime("%Y-%m-%d %H:%M:%S")
    ## 지금 시간이 마지막 로그로부터 7일이내인 경우 알람 중지 
    if latest_file < timestamp_now < str_after7:
        pass
    else :
        await send_balance()


## 알림 전송
async def send_balance():
    await bot.send_message(group_id,text = f"Balance : {balance} BFC")

## 가장 최근 저장된 파일 시간 체크
async def latest_file_time():
    file_list =os.listdir(folder)
    latest_file = max(file_list, key=lambda f: os.path.getctime(os.path.join(folder, f)))
    
    return latest_file

## 오래된 파일 삭제
async def delete_old_file():
    file_list =os.listdir(folder)
    max_files = 5 # 폴더에 저장되는 최대 파일 갯수

    if len(file_list) >= max_files:
        oldest_file = min(file_list, key=lambda f: os.path.getctime(os.path.join(folder,f)))
        os.remove(os.path.join(folder, oldest_file))

##########################커맨드##########################

## /help *명령어 목록
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    id = update.effective_chat.id

    send_text = "[명령어 안내] \n"
    send_text = send_text + "/balance : 현재 Balance 확인 \n"
    send_text = send_text + "/stop : Alarm 중지 (7일동안) \n"

    await bot.send_message(id, text=send_text)
    await latest_file_time()

## /balance *잔고 전송 
async def account_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    id = update.effective_chat.id
    balance = round(w3.from_wei(w3.eth.get_balance(relayerAddress),'ether'),2)

    if balance < 1000 :
        await bot.send_message(id,text= "❗Relayer 충전이 필요합니다.")
    else :
        pass

    await bot.send_message(id,text = f"Balance : {balance} BFC")

## /stop *알람 중지  
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ## 현재 시간
    now = datetime.datetime.now()
    timestamp_now = now.strftime('%Y-%m-%d %H:%M:%S')
    ## 7일 뒤
    after7 = now + datetime.timedelta(days=7)
    timestamp_after7 = after7.strftime('%Y-%m-%d %H:%M:%S')
    ## 그룹 ID
    id = update.effective_chat.id
    ## 명령어를 호출한 계정 ID
    user_id = update.message.from_user.id

    filename = f"{timestamp_now}"
    log_content = f"Function executed at : {timestamp_now} \n" f"Function will be stoped at {timestamp_after7}"
    
    ## 호출한 계정과 나의 계정이 일치 할 때
    if user_id == chat_id :
        # 오래된 파일 삭제
        await delete_old_file()

        # 새로운 파일 생성
        file_path = os.path.join(folder, filename)
        with open(file_path, "w") as file:
            file.write(log_content)
    
        # 출금 정보 출력
        await bot.send_message(id,f" 출금 신청 시간: {timestamp_now} \n" f"출금 가능 시간: {timestamp_after7}") 
    else :
        await bot.send_message(id,"권한이 없습니다.")



async def schedule():
    while True:
        await check_balance()
        await asyncio.sleep(86400)


if __name__ == "__main__":
    application = ApplicationBuilder().token(token).build()

    help_handler = CommandHandler('help', help)
    balance_handler = CommandHandler('balance', account_balance)
    stop_handler = CommandHandler('stop', stop)

    application.add_handler(help_handler)
    application.add_handler(balance_handler)
    application.add_handler(stop_handler)

    loop = asyncio.get_event_loop()
    loop.create_task(schedule())

    try:
        loop.run_until_complete(application.run_polling())
    except KeyboardInterrupt:
        loop.stop()