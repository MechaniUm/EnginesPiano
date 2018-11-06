import RPi.GPIO as GPIO
import pygame
from threading import Thread
import time
import smbus
import csv

pin_count = 12
pins = [
    5, 6, 12, 16,
    17, 18, 22, 23,
    24, 25, 26, 27
]
is_playing = [False for i in range(0, pin_count)]
keys_pressed = 0
cur_ptrn_id = 0
addr_1 = 0x38
addr_2 = 0x39

patterns = []

def bytes_from_file(filename, chunksize=8192):
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(chunksize)
            if chunk:
                for b in chunk:
                    yield b
            else:
                break

def i2c_thread():
    global keys_pressed
    global cur_ptrn_id
    global patterns
    cleared = False
    try:
        bus = smbus.SMBus(1)
        while(True):
            if (keys_pressed > 0):
                bus.write_i2c_block_data(addr_1, 0, [patterns[cur_ptrn_id][0]])
                bus.write_i2c_block_data(addr_2, 0, [patterns[cur_ptrn_id][1]])
                cur_ptrn_id += 1
                if cur_ptrn_id == len(patterns):
                    cur_ptrn_id = 0
                time.sleep(patterns[cur_ptrn_id][2])
                cleared = False
            if (keys_pressed == 0 and not cleared):
                cleared = True
                bus.write_i2c_block_data(addr_1, 0, [0x00])
                bus.write_i2c_block_data(addr_2, 0, [0x00])
    except:
        print("I2C Error")
        
if __name__ == "__main__":
    
    GPIO.setmode(GPIO.BCM)
    
    FILENAME = "lamps.csv"

    with open(FILENAME, "r", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            x = 0
            y = 0
            for c in row[0].split():
                if int(c) <= 6:
                    x |= 1 << (int(c) - 1)
                else:
                    y |= 1 << (int(c) - 7)
            patterns.append([x, y, float(row[1])])
    
    pygame.init()
    launch_sound = pygame.mixer.Sound("/home/pi/audio/start.ogg")
    launch_sound.play()
    print(len(patterns))
    print(patterns)
    for pin in pins:
        GPIO.setup(pin, GPIO.IN)
    thread = Thread(target = i2c_thread)
    thread.start()
    sounds = [pygame.mixer.Sound("/home/pi/audio/audio_" + str(i) + ".ogg") for i in range(1, pin_count+1)]
    
    
    try:
        while(True):
            for i in range(0, pin_count):
                if GPIO.input(pins[i]) == 1:
                    if not is_playing[i]:
                        is_playing[i] = True
                        sounds[i].play(-1)
                        keys_pressed += 1
                else:
                    if is_playing[i]:
                        is_playing[i] = False
                        sounds[i].fadeout(700)
                        keys_pressed -= 1
    except:
        print("Bye")
        GPIO.cleanup()
