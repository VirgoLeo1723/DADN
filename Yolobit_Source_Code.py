from aiot_lcd1602 import LCD1602
from yolobit import *
button_a.on_pressed = None
button_b.on_pressed = None
button_a.on_pressed_ab = button_b.on_pressed_ab = -1
from mqtt import *
import time
from event_manager import *
from machine import Pin, SoftI2C
from aiot_dht20 import DHT20
import random

aiot_lcd1602 = LCD1602()

def on_mqtt_message_receive_callback__dadn_annouce_(message):
  global id2, tempData, temp, sensor_delay, no_plant, watering_delay, public_data, i, watering_flag, watering_message, sensor_flag, RawData, create_message, remove_message, begin, sensor_state, m, no_sensor
  # Initialize system
  #
  if message.rfind(';ID') + 1 != 0 and begin == 0:
    begin = 1
    no_plant = (int((message[ : int((message.find(';ID') + 1) - 1)]))) + 0
  if message[-1] != 'D' and begin == 1:
    if message.find(';W') + 1 != 0:
      watering_message = message
      watering_start()
    elif message.find(';N') + 1 != 0:
      aiot_lcd1602.move_to(0, 1)
      aiot_lcd1602.putstr('                ')
      aiot_lcd1602.move_to(0, 1)
      aiot_lcd1602.putstr('ADDING')
      create_message = message
      create_new_handle()
    elif message.find(';R') + 1 != 0:
      aiot_lcd1602.move_to(0, 1)
      aiot_lcd1602.putstr('                ')
      aiot_lcd1602.move_to(0, 1)
      aiot_lcd1602.putstr('REMOVING')
      remove_message = message
      remove_handle()

event_manager.reset()

aiot_dht20 = DHT20(SoftI2C(scl=Pin(22), sda=Pin(21)))

# Mô tả hàm này...
def watering_handle():
  global id2, message, tempData, temp, sensor_delay, no_plant, watering_delay, public_data, i, watering_message, watering_flag, sensor_flag, RawData, create_message, remove_message, begin, sensor_state, m, no_sensor, aiot_lcd1602, aiot_dht20
  if watering_flag == 1 and watering_delay == 0:
    if watering_message == '3;W':
      pin14.write_analog(round(translate(0, 0, 100, 0, 1023)))
    elif watering_message == '4;W':
      pin15.write_analog(round(translate(0, 0, 100, 0, 1023)))
    aiot_lcd1602.move_to(0, 1)
    aiot_lcd1602.putstr('                ')
    send_feedback(watering_message)
    watering_flag = 0
    watering_delay = 0
  else:
    watering_delay = (watering_delay if isinstance(watering_delay, (int, float)) else 0) + -1

# Mô tả hàm này...
def sensor_fsm():
  global id2, message, tempData, temp, sensor_delay, no_plant, watering_delay, public_data, i, watering_message, watering_flag, sensor_flag, RawData, create_message, remove_message, begin, sensor_state, m, no_sensor, aiot_lcd1602, aiot_dht20
  if sensor_Timeout() == 1:
    public_data = getSensorData(sensor_state)
    if sensor_state <= 2:
      sensor_state = (sensor_state if isinstance(sensor_state, (int, float)) else 0) + 1
    else:
      sensor_state = 0
    mqtt.publish('dadn.sensor', public_data)

def upRange(start, stop, step):
  while start <= stop:
    yield start
    start += abs(step)

def downRange(start, stop, step):
  while start >= stop:
    yield start
    start -= abs(step)

# Mô tả hàm này...
def getSensorData(id2):
  global message, tempData, temp, sensor_delay, no_plant, watering_delay, public_data, i, watering_message, watering_flag, sensor_flag, RawData, create_message, remove_message, begin, sensor_state, m, no_sensor, aiot_lcd1602, aiot_dht20
  if id2 == 1:
    tempData = 'T'
  elif id2 == 2:
    tempData = 'M'
  else:
    tempData = 'L'
  for i in (1 <= float(no_plant)) and upRange(1, float(no_plant), 1) or downRange(1, float(no_plant), 1):
    tempData = ''.join([str(x2) for x2 in [tempData, ';', RawData[int(i - 1)][int(id2 - 1)]]])
  return tempData

# Mô tả hàm này...
def watering_start():
  global id2, message, tempData, temp, sensor_delay, no_plant, watering_delay, public_data, i, watering_message, watering_flag, sensor_flag, RawData, create_message, remove_message, begin, sensor_state, m, no_sensor, aiot_lcd1602, aiot_dht20
  if watering_message == '3;W':
    pin14.write_analog(round(translate(100, 0, 100, 0, 1023)))
  elif watering_message == '4;W':
    pin15.write_analog(round(translate(100, 0, 100, 0, 1023)))
  aiot_lcd1602.move_to(0, 1)
  aiot_lcd1602.putstr('....Watering....')
  watering_flag = 1
  watering_delay = 1

# Mô tả hàm này...
def sensor_Timeout():
  global id2, message, tempData, temp, sensor_delay, no_plant, watering_delay, public_data, i, watering_message, watering_flag, sensor_flag, RawData, create_message, remove_message, begin, sensor_state, m, no_sensor, aiot_lcd1602, aiot_dht20
  if sensor_flag == 1:
    temp = 1
    sensor_flag = 0
  else:
    temp = 0
  return temp

# Mô tả hàm này...
def getAllSensorData():
  global id2, message, tempData, temp, sensor_delay, no_plant, watering_delay, public_data, i, watering_message, watering_flag, sensor_flag, RawData, create_message, remove_message, begin, sensor_state, m, no_sensor, aiot_lcd1602, aiot_dht20
  aiot_dht20.read_dht20()
  RawData[0] = [aiot_dht20.dht20_temperature(), round(translate((pin1.read_analog()), 0, 4095, 0, 100)), round(translate((pin0.read_analog()), 0, 4095, 0, 100))]
  if no_plant > 1:
    for m in (2 <= float(no_plant)) and upRange(2, float(no_plant), 1) or downRange(2, float(no_plant), 1):
      RawData[int(m - 1)] = [(aiot_dht20.dht20_temperature()) + random.randint(-5, 5), (round(translate((pin1.read_analog()), 0, 4095, 0, 100))) + random.randint(-5, 5), (round(translate((pin0.read_analog()), 0, 4095, 0, 100))) + random.randint(-5, 5)]

# Mô tả hàm này...
def sensor_run():
  global id2, message, tempData, temp, sensor_delay, no_plant, watering_delay, public_data, i, watering_message, watering_flag, sensor_flag, RawData, create_message, remove_message, begin, sensor_state, m, no_sensor, aiot_lcd1602, aiot_dht20
  sensor_delay = (sensor_delay if isinstance(sensor_delay, (int, float)) else 0) + -1
  if sensor_delay == 0:
    sensor_delay = 10
    sensor_flag = 1

# Mô tả hàm này...
def create_new_handle():
  global id2, message, tempData, temp, sensor_delay, no_plant, watering_delay, public_data, i, watering_message, watering_flag, sensor_flag, RawData, create_message, remove_message, begin, sensor_state, m, no_sensor, aiot_lcd1602, aiot_dht20
  no_plant = (int((create_message[ : int((create_message.find(';N') + 1) - 1)]))) + 0
  send_feedback(create_message)

# Mô tả hàm này...
def remove_handle():
  global id2, message, tempData, temp, sensor_delay, no_plant, watering_delay, public_data, i, watering_message, watering_flag, sensor_flag, RawData, create_message, remove_message, begin, sensor_state, m, no_sensor, aiot_lcd1602, aiot_dht20
  no_plant = (int((remove_message[ : int((remove_message.find(';R') + 1) - 1)]))) - 1
  send_feedback(remove_message)

# Mô tả hàm này...
def send_feedback(message):
  global id2, tempData, temp, sensor_delay, no_plant, watering_delay, public_data, i, watering_message, watering_flag, sensor_flag, RawData, create_message, remove_message, begin, sensor_state, m, no_sensor, aiot_lcd1602, aiot_dht20
  mqtt.publish('dadn.annouce', (str(message) + 'D'))

def on_event_timer_callback_P_w_g_J_Y():
  global id2, message, tempData, temp, sensor_delay, no_plant, watering_delay, public_data, i, watering_flag, watering_message, sensor_flag, RawData, create_message, remove_message, begin, sensor_state, m, no_sensor
  mqtt.publish('dadn.test', (str(RawData) + 'D'))

event_manager.add_timer_event(5000, on_event_timer_callback_P_w_g_J_Y)

if True:
  aiot_lcd1602.move_to(4, 0)
  aiot_lcd1602.putstr('AR PLANT')
  display.show(Image.SMILE)
  mqtt.connect_wifi('Star 4_3188', 'yenkun1723')
  mqtt.connect_broker(server='io.adafruit.com', port=1883, username='Leo2308', password='aio_Dehb72bO0aUOjBrWEcyQfSmzi7lR')
  no_plant = 1
  no_sensor = 3
  sensor_delay = 2
  sensor_flag = 0
  sensor_state = 0
  watering_flag = 0
  watering_delay = 0
  create_message = not len('')
  remove_message = not len('')
  watering_message = not len('')
  RawData = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
  mqtt.publish('dadn.annouce', '0;I')
  begin = 0

while True:
  if watering_delay == 0:
    aiot_lcd1602.move_to(0, 1)
    aiot_lcd1602.putstr('                ')
    aiot_lcd1602.move_to(0, 1)
    aiot_lcd1602.putstr((''.join([str(x) for x in ['Moistrure:', round(translate((pin1.read_analog()), 0, 4095, 0, 100)), '%']])))
  mqtt.on_receive_message('dadn.annouce', on_mqtt_message_receive_callback__dadn_annouce_)
  time.sleep_ms(1000)
  if begin == 1:
    sensor_fsm()
    sensor_run()
    watering_handle()
    getAllSensorData()
    event_manager.run()
    aiot_dht20.read_dht20()
