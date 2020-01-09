from machine import Pin,PWM
import network, BlynkLib
import time, urequests

#網路設定
sta_if=network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('nptumis','123456789') #記得手機要同一個網路
while not sta_if.isconnected():
    pass
print("Wifi已連線")

token = 'As5-L2Ha0sMqirSecGVkFEPMjNDxKBJo' #權杖
blynk = BlynkLib.Blynk(token)
relay = Pin(14, Pin.OUT, value=0) #D5

#抓open data
res = urequests.get("http://opendata.epa.gov.tw/webapi/Data/ATM00698/?$filter=SiteName%20eq%20%27%E9%AB%98%E9%9B%84%27&$skip=0&$top=1&format=json") #政府資料開放平台AQI網址
j = res.json()
print("測站名稱:", j[0]["SiteName"])
print("資料建置時間:", j[0]["DataCreationDate"])
print("溫度(℃):", j[0]["Temperature"])
print("相對溼度(%)：", j[0]["Moisture"])
t = j[0]["Temperature"]
t1=[]
t1 = t.split("(", 1)
temp = float(t1[0])
humi = int(j[0]["Moisture"])

#LED燈控制
rled=PWM(Pin(12))
gled=PWM(Pin(13))
bled=PWM(Pin(15))
def setduty(r,g,b):
    time.sleep(1)
    rled.duty(r)
    gled.duty(g)

def alarmBeep(pwm):
   pwm.freq(1000)     #設定頻率為 1KHz    
   pwm.duty(512)      #設定工作週期為 50%
   time.sleep(1)          #持續時間 1 秒
   pwm.deinit()          #停止發聲
   time.sleep(2)          #持續時間 2 秒

def alarmClockBeep(pwm):
   for i in range(1,5):        #4 次迴圈 (1~4)
       pwm.freq(1000)       #設定頻率為 1KHz  
       pwm.duty(512)         #設定工作週期為 50%
       time.sleep_ms(100)  #持續時間 0.1 秒
       pwm.deinit()             #停止發聲
       time.sleep_ms(200)   #持續時間 0.2 秒
   time.sleep_ms(800)

pwm=PWM(Pin(4)) #D2

#判斷氣溫濕度
def funTemp(temp):
    if temp>27:
        print("toooooo hot，建議開啟電扇")
        setduty(500,0,0)
        alarmBeep(pwm)
    elif temp<=27 and temp>23:
        print("Is good，關閉電扇")
        setduty(0,500,0)
        alarmClockBeep(pwm)
    elif temp<=23:
        print("tooooo cold，建議關閉電扇")
        setduty(0,0,500)
        alarmClockBeep(pwm)
funTemp(temp)

#提供相關資料給各虛擬角位
def v1_handler(temp):    
    blynk.virtual_write(1, temp)

def v2_handler(humi):
    blynk.virtual_write(2, humi)

def v3_handler(value):
    relay.value(int(value[0]))

v1_handler(temp)
v2_handler(humi)
blynk.on("readV1", v1_handler)
blynk.on("readV2", v2_handler)
blynk.on("V3", v3_handler)

while True:
    blynk.run()