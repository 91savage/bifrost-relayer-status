# unbonding.py
import unbonding

import telegram
import asyncio
from web3 import Web3
import os
import time

from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes,CommandHandler
from telegram import Update

############################ Local에서 실행 할 때 ########################
# from dotenv import load_dotenv
## env 파일 사용
# load_dotenv()
# ## my_chat ID
# chat_id = int(os.environ.get('chat_id'))
# ## 채팅방 ID
# group_id = os.environ.get('group_id')
# token = os.environ.get('TELEGRAM_BOT_TOKEN')

############################ Docker에서 실행 할 때 ########################
## my_chat ID
chat_id = os.environ.get('chat_id')
## 채팅방 ID
group_id = os.environ.get('group_id')
token = os.environ.get('TELEGRAM_BOT_TOKEN')
########################################################################

relayerAddress = '0x0705D5b6804C022E5c10AbBa86186de5f59A42a8'
bot = telegram.Bot(token)
w3 = Web3(Web3.HTTPProvider('https://public-01.mainnet.thebifrost.io/rpc'))

## unbonding.py 임포트
current_round = unbonding.cround
execute_round = unbonding.eround
remaining_round = unbonding.rround

# alert 함수 stop용
stop_event = asyncio.Event()


## /help 명령어 목록
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    id = update.effective_chat.id

    send_text = "[명령어 안내] \n"
    send_text = send_text + "/balance : 현재 Balance 확인 \n"
    send_text = send_text + "/request : 출금신청 여부 확인 (라운드당 12시간) \n"

    await bot.send_message(id, text=send_text)


# /balance 체크
async def balance_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    id = update.effective_chat.id
    balance = round(w3.from_wei(w3.eth.get_balance(relayerAddress),'ether'),2)

    if balance < 1000 :
        await bot.send_message(id,text= f"❗Relayer 충전이 필요합니다.\n \n Ballance : {balance} BFC")
    else :
        await bot.send_message(id,text = f"✅ Balance : {balance} BFC")

#/request 체크
async def request_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    id = update.effective_chat.id
    balance = round(w3.from_wei(w3.eth.get_balance(relayerAddress),'ether'),2)
    
    await bot.send_message(id,createText(balance))
    
# 알림 메시지 작성    
def createText(balance):
    if execute_round == None :
        return unbonding_check(balance)
    return round_check()

# unbonding 체크
def unbonding_check(balance):    
    if balance < 1000 :
        return  "😂 출금예약이 필요합니다."
    return f"✅ 정상입니다. Balance: {balance} BFC"

# round 체크    
def round_check():
    if current_round >= execute_round :
        return "✅ Unstaking이 가능합니다."
    return f"👍 출금이 진행 중입니다. 남은 라운드는 {remaining_round} Round 입니다."

# Balance 알림
async def balance_alert():
    balance = round(w3.from_wei(w3.eth.get_balance(relayerAddress),'ether'),2)
    
    if execute_round == None and balance < 1000 :
        await bot.send_message(group_id,text= f"❗Relayer 충전이 필요합니다.\n \n Ballance : {balance} BFC")
    
# unbondiong 알림
async def unbonding_alert() :
    balance = round(w3.from_wei(w3.eth.get_balance(relayerAddress),'ether'),2)
    if execute_round != None and balance <1000 :
        await bot.send_message(group_id, text= f"🔔 출금 신청이 완료 되었습니다. 출금 가능 라운드는 {execute_round} 입니다.")
        stop_event.set()
    
    
# balance 스케쥴 24시간에 한번
async def schedule_balance():
    while True:
        await balance_alert()
        await asyncio.sleep(86400)
        
## unbonding 스케쥴
async def schedule_unbonding():
    while True:
        await unbonding_alert()
        await asyncio.sleep(300)
        if stop_event.is_set():
            stop_event.clear()
            await asyncio.sleep(7 * 24 * 60 * 60)
            await bot.send_message(group_id, text= f"🔔 이제 unstaking 가능합니다.")
            await asyncio.sleep(7 * 24 * 60 * 60) 


if __name__ == "__main__":
    application = ApplicationBuilder().token(token).build()

    help_handler = CommandHandler('help', help)
    balance_handler = CommandHandler('balance', balance_check)
    request_handler = CommandHandler('request', request_check)

    application.add_handler(help_handler)
    application.add_handler(balance_handler)
    application.add_handler(request_handler)

    loop = asyncio.get_event_loop()
    loop.create_task(schedule_balance())
    loop.create_task(schedule_unbonding())
    

    try:
        loop.run_until_complete(application.run_polling())
    except KeyboardInterrupt:
        loop.stop()
    application.run_polling()
    
    
