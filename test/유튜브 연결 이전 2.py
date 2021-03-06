from __future__ import print_function
from urllib.request import urlopen, Request
import urllib
import bs4
from bs4 import BeautifulSoup as bs
import requests
import re
import ex1_kwstest as kws
import ex2_getVoice2Text as gv2t
import ex4_getText2VoiceStream as tts
import ex6_queryVoice as dss
import Adafruit_DHT as dht
import time
import random
import MicrophoneStream as MS
from datetime import datetime
import threading

url1 = requests.get('https://search.naver.com/search.naver?query=날씨')
soup1 = bs(url1.text,'html.parser')
#지역
location=soup1.find('div',class_='select_box').find('span',class_='btn_select').text

humidity_loc=urllib.parse.quote(location+ ' 습도')
url2=requests.get('https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query='+humidity_loc)
soup2=bs(url2.text,'html.parser')
data1=soup1.find('div',class_='detail_box')
data2 = data1.findAll('dd')
#but_commu = 0


##===============================================================
def nowdate():
    now = datetime.now()
    nowdate = str(now.month).zfill(2) + str(now.day).zfill(2)
    nowdate = int(nowdate)
    return nowdate
def nowtime():
    now = datetime.now()
    nowtime = str(now.hour).zfill(2) + str(now.minute).zfill(2)
    nowtime = int(nowtime)
    return nowtime

#온도
def temp():
    temp=soup1.find('p', class_='info_temperature').find('span', class_='todaytemp').text
    return temp

#습도
def hum():
    humidity_withpersent=soup2.find('div',class_='info_list humidity _tabContent').find('dd',class_='weather_item _dotWrapper').text
    hum=int(re.findall('\d+',humidity_withpersent)[0])
    return hum

#미세먼지
def fine_dust():
    fine_dust=data2[0].find('span',class_='num').text
    return fine_dust

#초미세먼지
def ultra_fine_dust():
    ultra_fine_dust = data2[1].find('span',class_='num').text
    return ultra_fine_dust

#미세먼지를 수치로
def fd_level():
    fine_dust_num=int(re.findall('\d+',fine_dust())[0])
    if (fine_dust_num<=30):
        return("좋음")
    elif(fine_dust_num>=31)and(fine_dust_num<=80):
        return("보통")
    elif(fine_dust_num>=81)and(fine_dust_num<=150):
        return("나쁨")
    else:
        return("매우 나쁨")
    
#초미세먼지를 수치로
def ufd_level():
    ultra_fine_dust_num=int(re.findall('\d+',ultra_fine_dust())[0])
    if (ultra_fine_dust_num<=15):
        return("좋음")
    elif(ultra_fine_dust_num>=16)and(ultra_fine_dust_num<=50):
        return("보통")
    elif(ultra_fine_dust_num>=51)and(ultra_fine_dust_num<=100):
        return("나쁨")
    else:
        return("매우 나쁨")
    
##===============================================================
down_t = ["창문을 열어 환기를 시켜주세요",
          "선풍기를 집 밖을 향해서 틀어주세요",
          "커튼을 쳐주세요",
          "물을 마셔주세요",
          "따뜻한 물로 샤워해주세요"]  # 3 

down_h = ["창문을 열어 환기를 시켜주세요",
          "제습기를 틀어주세요",
          "환풍기를 틀어주세요",
          "물을 마셔주세요"] # 3

down_t_dust = ["선풍기를 집 밖을 향해서 틀어주세요",
               "커튼을 쳐주세요",
               "물을 마셔주세요",
               "따뜻한 물로 샤워해주세요"] # 2


down_h_dust = ["제습기를 틀어주세요",
              "환풍기를 틀어주세요",
              "물을 마셔주세요"]   # 2

up_t = ["난방을 틀어주세요.",
        "따뜻한 물로 샤워해주세요.",
        "따뜻한 물을 마셔주세요.",
        "내복을 입어주세요.",
        "양말을 신어주세요.",  
        "목에 손수건을 둘러주세요." ]   # 1

up_h = ["가습기를 틀어주세요",
        "빨래나 물에 젖은 손수건을 널어주세요",
        "목에 손수건이 스카프를 둘러주세요",
        "물을 마셔주세요" ]   # 1

##==========================================================
def season_select():
    season = ""
    date = nowdate()

    if 622 <= date < 823:
        season = "여름"
    elif 1122 <= date <= 1231 or date < 306:
        season = "겨울"
    else:
        season = "그외"
    
    return season

##==========================================================

def giveSolution():
    today_t= float(temp())
    today_h = float(hum())
    fine_dust2 = int(re.findall('\d+',fine_dust())[0])
    humidity, temperature = dht.read_retry(dht.DHT22, 4)
    h= humidity
    t= temperature
    ans = ""
    season = season_select()

    if season == '여름':
        if today_t - t >= 8:
            print("현재 밖과의 온도차가 매우 큽니다.")
            print("에어컨이나 선풍기의 전원을 꺼주세요.")
            ans = "현재 밖과의 온도차가 매우 큽니다. 에어컨이나 선풍기의 전원을 꺼주세요."
        else:
            if t >= 30 and h >= 65:
                print("현재 온도는 높고 습도도 높습니다.")

                if fine_dust2 >= 75 or today_h > h :
                    ans = down_t_dust[random.randrange(0,2)] + '그리고' + down_h_dust[random.randrange(0,2)]
                else:
                    ans = down_t[random.randrange(0,3)] + '그리고' + down_h[random.randrange(0,3)]

            elif t >= 30 and h <= 35:
                print("현재 온도는 높고 습도는 낮습니다.")
                ans = down_t[random.randrange(0,3)] + '그리고' + up_h[random.randrange(0,1)]
                
            elif t >= 30 and 35 < h < 65:
                print("현재 온도가 높습니다. ")
                ans = down_t[random.randrange(0,3)]
                 
            elif t < 30 and h >= 65:
                print("현재 습도가 높습니다. ")
                if fine_dust2 >= 75 or today_h > h :
                    ans = down_h_dust[random.randrange(0,2)]
                else:
                    ans = down_h[random.randrange(0,3)]

            elif t < 30 and h <= 35:
                print("현재 습도가 낮습니다. ")
                ans = up_h[random.randrange(0,1)]
                
            else:
                print("현재 온도와 습도가 모두 쾌적한 상태입니다, ")
                ans = "현재 온도와 습도가 모두 쾌적한 상태입니다"

    elif season == '겨울':
        if t <= 22 and h >= 65:
            print("현재 온도는 낮고 습도는 높습니다.")
            if fine_dust2 >= 75 or today_h > h :
                ans = up_t[random.randrange(0,1)] + '그리고' + down_h_dust[random.randrange(0,2)]
            else:
                ans = up_t[random.randrange(0,1)] + '그리고' + down_h[random.randrange(0,3)]

        elif t <= 22 and h <= 35:
            print("현재 온도는 낮고 습도도 낮습니다.")
            ans = up_t[random.randrange(0,1)] + '그리고' + up_h[random.randrange(0,1)]

        elif t <= 22 and 35<h<65:
            print("현재 온도가 낮습니다.")
            ans = up_t[random.randrange(0,1)]

        elif t > 22 and h >= 65:
            print("현재 습도가 높습니다.")
            if fine_dust2 >= 75 or today_h > h :
                ans = down_h_dust[random.randrange(0,2)]
            else:
                ans = down_h[random.randrange(0,3)]

        elif t > 22 and h <= 35:
            print("현재 습도가 낮습니다. ")
            ans = up_h[random.randrange(0,1)]

        else:
            print("온도와 습도가 모두 쾌적한 상태입니다.")
            ans = "현재 온도와 습도가 모두 쾌적한 상태입니다"

    else:
        if today_t - t >= 8:
            print("현재 밖과의 온도 차이가 매우 큽니다.")
            print("에어컨이나 선풍기의 전원을 꺼주세요.")
            ans = "현재 밖과의 온도 차이가 매우 큽니다. 에어컨이나 선풍기의 전원을 꺼주세요."

        else:
            if 29 <= t and h >= 65:
                print("현재 온도가 높고 습도도 높습니다. ")
                if fine_dust2 >= 75 or today_h > h :
                    ans = down_t_dust[random.randrange(0,2)] + '그리고' + down_h_dust[random.randrange(0,2)]
                else:
                    ans = down_t[random.randrange(0,3)] + '그리고' + down_h[random.randrange(0,3)]

            elif 29 <= t and h <= 35:
                print("현재 온도가 높고 습도는 낮습니다.")
                ans = down_t[random.randrange(0,3)] + '그리고' + up_h[random.randrange(0,1)]

            elif 22 >= t and h >= 65:
                print("현재 온도는 낮고 습도는 높습니다.")
                if fine_dust2 >= 75 or today_h > h :
                    ans = up_t[random.randrange(0,1)] + '그리고' + down_h_dust[random.randrange(0,2)]
                else:
                    ans = up_t[random.randrange(0,1)] + '그리고' + down_h[random.randrange(0,3)]

            elif 22 >= t and h <= 35:
                print("현재 온도는 낮고 습도도 낮습니다.")
                ans = up_t[random.randrange(0,1)] + '그리고' + up_h[random.randrange(0,1)]

            elif 29 <= t and 35 < h < 65 :
                print("현재 온도가 높습니다.")
                ans = down_t[random.randrange(0,3)]

            elif 22 >= t and 35 < h < 65 :
                print("현재 온도가 낮습니다.")
                ans = up_t[random.randrange(0,1)]

            elif 22 < t < 29 and h >= 65 :
                print("현재 습도가 높습니다.")
                if fine_dust2 >= 75 or today_h > h :
                    ans = down_h_dust[random.randrange(0,2)]
                else:
                    ans = down_h[random.randrange(0,3)]

            elif 22 < t < 29 and h <= 35 :
                print("현재 습도가 낮습니다.")
                ans = up_h[random.randrange(0,1)]

            else:
                print("현재 온도와 습도가 모두 쾌적한 상태입니다,")
                ans = "현재 온도와 습도가 모두 쾌적한 상태입니다"
    
    return ans


##===============================================================
def gs_call():
    tts.getText2VoiceStream(giveSolution(), "result_TTS.wav")
    MS.play_file("result_TTS.wav")
            
    threading.Timer(600, gs_call).start()

##===============================================================
def checkCommand(result):
    humidity, temperature = dht.read_retry(dht.DHT22, 4)
    
    text = result
    ###
    if (text.find("온도 알려줘") >= 0)or(text.find("지금 몇도야")>=0):
        print("현재 실내 온도는 {0:0.1f} 도 입니다 ".format(temperature))
        return("현재 실내 온도는 {0:0.1f} 도 입니다ㅏ, ,".format(temperature))
    
    ###
    elif text.find("습도 알려줘") >= 0:
        print("현재 실내 습도는 {0:0.1f} 퍼센트 입니다 ".format(humidity))
        return("현재 실내 습도는 {0:0.1f} 퍼센트 입니다ㅏ. ".format(humidity))
    
    ###
    elif text.find("날씨 알려줘") >= 0:
        #print("현재 온도는 {0:0.1f}도 이고, 습도는 {1:0.1f} 퍼센트 입니다 ".format(temperature, humidity))
        #return ("현재 온도는 {0:0.1f}도 이고, 습도는 {1:0.1f} 퍼센트 입니다 ".format(temperature, humidity))
        print("현재 {0:s}의 온도는 {1:s} 도 이고, 미세먼지는 {2:s}, 초미세먼지는 {3:s}이고, 습도는 {4:d} 퍼센트입니다 ".format(location,temp(),fd_level(),ufd_level(),hum()))
        return("현재 {0:s}의 온도는 {1:s} 도 이고, 미세먼지는 {2:s}, 초미세먼지는 {3:s}이고, 습도는 {4:d} 퍼센트입니다 ".format(location,temp(),fd_level(),ufd_level(),hum()))

        #return ("현재 {0:s}의 온도는 {1:s} 도 이고, 미세먼지는 {2:s}, 초미세먼지는 {3:s} 입니다ㅏ.".format(location,temp(),fd_level(),ufd_level()))
    
    ###
    elif text.find("미세먼지")>=0:
        print("현재 {0:s}의 미세먼지는 {1:s}로 {2:s}, 초미세먼지는 {3:s}로 {4:s}입니다. ".format(location,fine_dust(),fd_level(),ultra_fine_dust(),ufd_level()))
        return ("현재 {0:s}의 미세먼지는 {1:s}로 {2:s}, 초미세먼지는 {3:s}로 {4:s}입니다ㅏ. ".format(location,fine_dust(),fd_level(),ultra_fine_dust(),ufd_level()))
    ###
    elif text.find("현재 상태 알려줘")>=0:
        return giveSolution()
        
    ###
    elif text.find("대화하자") >= 0:
        but_commu = 1
        return ("저와 대화하고 싶으시면 지금 당장 버튼을 눌러주세요")
    
    else:
        print("start next function")
        return("정확한 명령을 말해주세요요오~")
    
    ###
##===============================================================
def main(): #Example7 KWS+STT
    KWSID = ['기가지니', '지니야', '친구야', '자기야']
    global but_commu
    but_commu = 0
    gs_call()  
    while 1:
        if but_commu == 0:
            time.sleep(5)
            recog1 = kws.test(KWSID[0])
            if recog1 == 200:
                print('KWS Dectected …\n Start STT…')
                text = gv2t.getVoice2Text()
                print('Recognized Text: '+ text)
                tts.getText2VoiceStream(checkCommand(text), "result_TTS.wav")
                MS.play_file("result_TTS.wav")
                time.sleep(2)
                            
            else:
                print('KWS Not Dectected …')
            
        if but_commu == 1:
            recog2 = kws.btn_test(KWSID[0])
            if recog2 == 200:
                print('KWS Dectected ...\n Start STT...')
                text = dss.queryByVoice()
                tts_result = tts.getText2VoiceStream(text, "result_mesg.wav")
                if text == '':
                    print('질의한 내용이 없습니다.')
                    but_commu = 0
                elif tts_result == 500:
                    print("TTS 동작 에러입니다.\n")
                    but_commu = 0
                    break
                else:
                    MS.play_file("result_mesg.wav")
                    but_commu = 0
                    time.sleep(2)
            else:
                print('KWS Not Dectected ...')
        
if __name__ == '__main__':
    main()
    