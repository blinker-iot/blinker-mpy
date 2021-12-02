try:
    import modules.urequests as requests
except ImportError:
    import requests
import ujson
from modules.simple import MQTTClient
from Blinker.BlinkerConfig import *
from Blinker.BlinkerDebug import *
from BlinkerUtility.BlinkerUtility import *

class MQTTProtocol(object):
    host = ''
    port = ''
    subtopic = ''
    pubtopic = ''
    deviceName = ''
    clientID = ''
    userName = ''
    password = ''
    uuid = ''
    msgBuf = ''
    isRead = False
    isAliRead = False
    isDuerRead = False
    state = CONNECTING
    isAlive = False
    isAliAlive = False
    isDuerAlive = False
    printTime = 0
    aliPrintTime = 0
    duerPrintTime = 0
    kaTime = 0
    aliKaTime = 0
    duerKaTime = 0
    debug = BLINKER_DEBUG
    smsTime = 0
    pushTime = 0
    wechatTime = 0
    weatherTime = 0
    aqiTime = 0

class BlinkerMQTT(MQTTProtocol):
    def checkKA(self):
        if self.isAlive is False:
            return False
        if (millis() - self.kaTime) < BLINKER_MQTT_KEEPALIVE:
            return True
        else:
            self.isAlive = False
            return False

    def checkAliKA(self):
        if self.isAliAlive is False:
            return False
        if (millis() - self.aliKaTime) < BLINKER_MQTT_KEEPALIVE:
            return True
        else:
            self.isAliAlive = False
            return False

    def checkDuerKA(self):
        if self.isDuerAlive is False:
            return False
        if (millis() - self.duerKaTime) < BLINKER_MQTT_KEEPALIVE:
            return True
        else:
            self.isDuerAlive = False
            return False

    def checkCanPrint(self):
        if self.checkKA() is False:
            BLINKER_ERR_LOG("MQTT NOT ALIVE OR MSG LIMIT")
            return False
        if (millis() - self.printTime) >= BLINKER_MQTT_MSG_LIMIT or self.printTime == 0:
            return True
        BLINKER_ERR_LOG("MQTT NOT ALIVE OR MSG LIMIT")
        return False

    def checkAliCanPrint(self):
        if self.checkAliKA() is False:
            BLINKER_ERR_LOG("MQTT NOT ALIVE OR MSG LIMIT")
            return False
        if (millis() - self.aliPrintTime) >= BLINKER_MQTT_MSG_LIMIT or self.aliPrintTime == 0:
            return True
        BLINKER_ERR_LOG("MQTT NOT ALIVE OR MSG LIMIT")
        return False

    def checkDuerCanPrint(self):
        if self.checkDuerKA() is False:
            BLINKER_ERR_LOG("MQTT NOT ALIVE OR MSG LIMIT")
            return False
        if (millis() - self.duerPrintTime) >= BLINKER_MQTT_MSG_LIMIT or self.duerPrintTime == 0:
            return True
        BLINKER_ERR_LOG("MQTT NOT ALIVE OR MSG LIMIT")
        return False

    def checkSMS(self):
        if (millis() - self.smsTime) >= BLINKER_SMS_MSG_LIMIT or self.smsTime == 0:
            return True
        BLINKER_ERR_LOG("SMS MSG LIMIT")
        return False

    def checkPUSH(self):
        if (millis() - self.pushTime) >= BLINKER_PUSH_MSG_LIMIT or self.pushTime == 0:
            return True
        BLINKER_ERR_LOG("PUSH MSG LIMIT")
        return False

    def checkWECHAT(self):
        if (millis() - self.wechatTime) >= BLINKER_PUSH_MSG_LIMIT or self.wechatTime == 0:
            return True
        BLINKER_ERR_LOG("WECHAT MSG LIMIT")
        return False

    def checkWEATHER(self):
        if (millis() - self.weatherTime) >= BLINKER_WEATHER_MSG_LIMIT or self.weatherTime == 0:
            return True
        BLINKER_ERR_LOG("WEATHER MSG LIMIT")
        return False

    def checkAQI(self):
        if (millis() - self.aqiTime) >= BLINKER_AQI_MSG_LIMIT or self.aqiTime == 0:
            return True
        BLINKER_ERR_LOG("AQI MSG LIMIT")
        return False

    def delay100ms(self):
        start = millis()
        time_run = 0
        while time_run < 100:
            time_run = millis() - start

    def delay10s(self):
        start = millis()
        time_run = 0
        while time_run < 10000:
            time_run = millis() - start

    def checkAuthData(self, data):
        if data['detail'] == BLINKER_CMD_NOTFOUND:
            while True:
                BLINKER_ERR_LOG("Please make sure you have put in the right AuthKey!")
                self.delay10s()

    @classmethod
    def getInfo(cls, auth, aliType, duerType):
        host = 'https://iot.diandeng.tech'
        url = '/api/v1/user/device/diy/auth?authKey=' + auth

        if aliType :
            url = url + aliType

        if duerType :
            url = url + duerType

        r = requests.get(host + url)

        data = r.json()
        cls().checkAuthData(data)
        # if cls().isDebugAll() is True:
        BLINKER_LOG_ALL('Device Auth Data: ', data)
        
        data = r.json()
        deviceName = data['detail']['deviceName']
        iotId = data['detail']['iotId']
        iotToken = data['detail']['iotToken']
        productKey = data['detail']['productKey']
        uuid = data['detail']['uuid']
        broker = data['detail']['broker']

        bmt = cls()

        BLINKER_LOG_ALL('deviceName: ', deviceName)
        BLINKER_LOG_ALL('iotId: ', iotId)
        BLINKER_LOG_ALL('iotToken: ', iotToken)
        BLINKER_LOG_ALL('productKey: ', productKey)
        BLINKER_LOG_ALL('uuid: ', uuid)
        BLINKER_LOG_ALL('broker: ', broker)
        BLINKER_LOG_ALL('host + url: ', host + url)

        if broker == 'aliyun':
            bmt.host = BLINKER_MQTT_ALIYUN_HOST
            bmt.port = BLINKER_MQTT_ALIYUN_PORT
        else:
            bmt.host = data['detail']['host'].replace('mqtts://','')
            bmt.port = data['detail']['port']
        bmt.subtopic = '/device/' + deviceName + '/r'
        bmt.pubtopic = '/device/' + deviceName + '/s'
        bmt.clientID = deviceName
        bmt.userName = iotId
        bmt.deviceName = deviceName
        bmt.password = iotToken
        bmt.uuid = uuid

        # if bmt.isDebugAll() is True:
        BLINKER_LOG_ALL('clientID: ', bmt.clientID)
        BLINKER_LOG_ALL('userName: ', bmt.userName)
        BLINKER_LOG_ALL('password: ', bmt.password)
        BLINKER_LOG_ALL('subtopic: ', bmt.subtopic)
        BLINKER_LOG_ALL('pubtopic: ', bmt.pubtopic)
        return bmt

def on_message(topic, msg):
    BLINKER_LOG_ALL('payload: ', msg)
    data = ujson.loads(msg)

class MQTTClients():
    def __init__(self):
        self.auth = ''
        self._isClosed = False
        self.client = None
        self.bmqtt = None
        self.mProto = BlinkerMQTT()
        self.aliType = ''
        self.duerType = ''
        self.isMQTTinit = False
        self.mqttPing = 0

    def start(self, auth, aliType, duerType):
        self.auth = auth
        self.aliType = aliType
        self.duerType = duerType  

    def on_message(self, topic, msg):
        BLINKER_LOG_ALL('payload: ', msg)
        data = ujson.loads(msg)
        fromDevice = data['fromDevice']
        data = data['data']
        data = ujson.dumps(data)
        BLINKER_LOG_ALL('fromDevice:', fromDevice, ', data: ', data)
        if fromDevice == self.bmqtt.uuid :
            BLINKER_LOG_ALL('from uuid')
            self.bmqtt.msgBuf = data
            self.bmqtt.isRead = True
            self.bmqtt.isAlive = True
            self.bmqtt.kaTime = millis()
        elif fromDevice == 'AliGenie':
            BLINKER_LOG_ALL('from aligenie')
            self.bmqtt.msgBuf = data
            self.bmqtt.isAliRead = True
            self.bmqtt.isAliAlive = True
            self.bmqtt.aliKaTime = millis()    
        elif fromDevice == 'DuerOS':
            BLINKER_LOG_ALL('from dueros')
            self.bmqtt.msgBuf = data
            self.bmqtt.isDuerRead = True
            self.bmqtt.isDuerAlive = True
            self.bmqtt.duerKaTime = millis()          

    def pub(self, msg, state=False):
        if state is False:
            if self.bmqtt.checkCanPrint() is False:
                return
        payload = {'fromDevice': self.bmqtt.deviceName, 'toDevice': self.bmqtt.uuid, 'data': msg , 'deviceType': 'OwnApp'}
        payload = ujson.dumps(payload)
        # if self.bmqtt.isDebugAll() is True:
        BLINKER_LOG_ALL('Publish topic: ', self.bmqtt.pubtopic)
        BLINKER_LOG_ALL('payload: ', payload)
        self.client.publish(self.bmqtt.pubtopic, payload)
        self.bmqtt.printTime = millis()

    def aliPrint(self, msg):
        if self.bmqtt.checkAliCanPrint() is False:
            return
        payload = {'fromDevice': self.bmqtt.deviceName, 'toDevice': 'AliGenie_r', 'data': msg , 'deviceType': 'vAssistant'}
        payload = ujson.dumps(payload)
        # if self.bmqtt.isDebugAll() is True:
        BLINKER_LOG_ALL('Publish topic: ', self.bmqtt.pubtopic)
        BLINKER_LOG_ALL('payload: ', payload)
        self.client.publish(self.bmqtt.pubtopic, payload)
        self.bmqtt.aliPrintTime = millis()

    def duerPrint(self, msg):
        if self.bmqtt.checkDuerCanPrint() is False:
            return
        payload = {'fromDevice': self.bmqtt.deviceName, 'toDevice': 'DuerOS_r', 'data': msg , 'deviceType': 'vAssistant'}
        payload = ujson.dumps(payload)
        # if self.bmqtt.isDebugAll() is True:
        BLINKER_LOG_ALL('Publish topic: ', self.bmqtt.pubtopic)
        BLINKER_LOG_ALL('payload: ', payload)
        self.client.publish(self.bmqtt.pubtopic, payload)

    def sms(self, msg):
        if self.bmqtt.checkSMS() is False:
            return
        payload = ujson.dumps({'deviceName':self.bmqtt.deviceName, 'key': self.auth, 'msg': msg})
        response = requests.post('https://iot.diandeng.tech/api/v1/user/device/sms',
                                 data=payload, headers={'Content-Type': 'application/json'})

        self.bmqtt.smsTime = millis()
        data = response.json()
        # if self.bmqtt.isDebugAll() is True:
        BLINKER_LOG_ALL('response: ', data)
        if data[BLINKER_CMD_MESSAGE] != 1000:
            BLINKER_ERR_LOG(data[BLINKER_CMD_DETAIL])

    def push(self, msg):
        if self.bmqtt.checkPUSH() is False:
            return
        payload = ujson.dumps({'deviceName':self.bmqtt.deviceName, 'key': self.auth, 'msg': msg})
        response = requests.post('https://iot.diandeng.tech/api/v1/user/device/push',
                                 data=payload, headers={'Content-Type': 'application/json'})

        self.bmqtt.pushTime = millis()
        data = response.json()
        # if self.bmqtt.isDebugAll() is True:
        BLINKER_LOG_ALL('response: ', data)
        if data[BLINKER_CMD_MESSAGE] != 1000:
            BLINKER_ERR_LOG(data[BLINKER_CMD_DETAIL])

    def wechat(self, title, state, msg):
        if self.bmqtt.checkWECHAT() is False:
            return
        payload = ujson.dumps({'deviceName':self.bmqtt.deviceName, 'key': self.auth, 'title':title, 'state':state, 'msg': msg})
        response = requests.post('https://iot.diandeng.tech/api/v1/user/device/wxMsg/',
                                 data=payload, headers={'Content-Type': 'application/json'})

        self.bmqtt.pushTime = millis()
        data = response.json()
        # if self.bmqtt.isDebugAll() is True:
        BLINKER_LOG_ALL('response: ', data)
        if data[BLINKER_CMD_MESSAGE] != 1000:
            BLINKER_ERR_LOG(data[BLINKER_CMD_DETAIL])

    def dataUpdate(self, msg):
        payload = ujson.dumps({'deviceName':self.bmqtt.deviceName, 'key': self.auth, 'data': msg})
        response = requests.post('https://iot.diandeng.tech/api/v1/user/device/cloudStorage/',
                                 data=payload, headers={'Content-Type': 'application/json'})

        self.bmqtt.pushTime = millis()
        data = response.json()
        # if self.bmqtt.isDebugAll() is True:
        BLINKER_LOG_ALL('response: ', data)
        if data[BLINKER_CMD_MESSAGE] != 1000:
            BLINKER_ERR_LOG(data[BLINKER_CMD_DETAIL])
            return False
        return True

    def weather(self, city):
        if self.bmqtt.checkWEATHER() is False:
            return
        host = 'https://iot.diandeng.tech'
        url = '/api/v1/user/device/weather/now?deviceName=' + self.bmqtt.deviceName + '&key=' + self.auth + '&location=' + city

        r = requests.get(url=host + url)
        data = ''

        self.bmqtt.weatherTime = millis()

        # if r.status_code != 200:
        #     BLINKER_ERR_LOG('Device Auth Error!')
        #     return
        # else:
        data = r.json()
        return data['detail']

    def aqi(self, city):
        if self.bmqtt.checkAQI() is False:
            return
        host = 'https://iot.diandeng.tech'
        url = '/api/v1/user/device/weather/now?deviceName=' + self.bmqtt.deviceName + '&key=' + self.auth + '&location=' + city

        r = requests.get(url=host + url)
        data = ''       

        self.bmqtt.aqiTime = millis()

        # if r.status_code != 200:
        #     BLINKER_ERR_LOG('Device Auth Error!')
        #     return
        # else:
        data = r.json()
        return data['detail']

    def connect(self):
        if self.isMQTTinit is False :
            self.bmqtt = self.mProto.getInfo(self.auth, self.aliType, self.duerType)
            self.isMQTTinit = True
            self.client = MQTTClient(client_id = self.bmqtt.clientID, 
                server = self.bmqtt.host, port = self.bmqtt.port, 
                user = self.bmqtt.userName, password =self.bmqtt.password, 
                keepalive = 60, ssl = True)
            self.client.set_callback(self.on_message)
            self.client.connect()
            self.client.subscribe(self.bmqtt.subtopic)

            self.mqttPing = millis()

            self.bmqtt.state = CONNECTED
        else :
            try:
                self.client.check_msg()
                self.mProto.delay100ms()
            except Exception as error:
                self.client.disconnect()
                MQTTClients.reconnect(self)

    def reconnect(self):
        try:
            MQTTClients.register(self)

            self.client = MQTTClient(client_id = self.bmqtt.clientID, 
                server = self.bmqtt.host, port = self.bmqtt.port, 
                user = self.bmqtt.userName, password =self.bmqtt.password, 
                keepalive = 60, ssl = True)
            self.client.set_callback(self.on_message)
            self.client.connect(clean_session = True)
            self.client.subscribe(self.bmqtt.subtopic)
        except Exception as error:
            BLINKER_ERR_LOG('MQTT reconnect failed...')

    def register(self):
        self.bmqtt = self.mProto.getInfo(self.auth, self.aliType, self.duerType)
