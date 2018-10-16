import RPi.GPIO as GPIO
import pygame

pin_count = 12

GPIO.setmode(GPIO.BCM)
pins = [5, 6, 12, 16,
       17, 18, 22, 23,
       24, 25, 26, 27]
is_playing = [False for i in range(0, pin_count)]
for pin in pins:
    GPIO.setup(pin, GPIO.IN)
    
pygame.init()
sounds = [pygame.mixer.Sound("audio_" + str(i) + ".ogg") for i in range(1, pin_count)]

try:
    while(True):
        for i in range(0, pin_count):
            if GPIO.input(pins[i]) == 1:
                if not is_playing[i]:
                    sounds[i].play(-1)
            else:
                if is_playing[i]:
                    sounds[i].stop()
except:
    print("Bye")
    GPIO.cleanup()