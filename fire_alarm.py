# fireAlarm
''' initiated when power is applied,
Runs through sequence of notifications.
Can be shutdown using button - primarily for testing
'''

#!/usr/bin/python

# Rev 1.0 - set up timing
# Rev 1.1 - add notifications, Nexmo tests
# Rev A.0 - field release
# Rev 0.2.0 - revised 10/09/20 for new Nexmo system
# Rev A.2 - Feb 8, 2022, use Twilio, add giblets


import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime
from pytz import timezone

# files required in folder
import RPiUtilities
import config
import Twilio_SMS as sms


class alarmReact():
    def __init__(self):
        '''set up initial conditions
        '''
        self.redLED = 12
        self.yellowLED = 7
        self.pinButton1 = 11
        self.numberBlinks = 3   # start blinks
        self.pollingDelay = .1  # time between polling actions

        # initialize rpi gpio
        GPIO.setmode(GPIO.BOARD)

        # set up GPIO output channel
        GPIO.setup((self.redLED, self.yellowLED), GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.pinButton1, GPIO.IN)

        # buttonState: 0 is no button pressed, 99 is any button when backlight is off, (1-3) button pressed
        self.buttonState = 0

        # buttonAction indicates whether the requested action is complete (1) or yet to be completed (0)
        self.buttonAction = 0

        # debounce time in milliseconds
        self.buttonDebounce = 300

        #### INTERRUPTS - BUTTONS ####
        GPIO.add_event_detect(self.pinButton1, GPIO.RISING, bouncetime=self.buttonDebounce, callback=self.reactToButton)


    #### TIMER FUNCTIONS ####
    def runTimer(self):
        '''main operations occurs here
        Runs through series of notifications based on time since on
        Shutdown occurs by exiting timing loop then shuts down in __main__
        '''
        # set timer variables
        runningSeconds = 0  # cumulative seconds since activation
        action = 0 # sequential counter for actions
        lastFloatSecond = 0
        lastSecond = 0
        flipFlop = 0

        run = True

        while run is True:
            thisSecond = float(datetime.now().strftime('%S.%f'))
            if lastFloatSecond + self.pollingDelay >= 60:
                    lastFloatSecond = 0
                    lastSecond = int(thisSecond)
                    runningSeconds += 1

            #### PACED POLLING ####
            if thisSecond > lastFloatSecond + self.pollingDelay:
                # index the timer
                lastFloatSecond = thisSecond

                if int(thisSecond) > lastSecond:
                    lastSecond = int(thisSecond)
                    runningSeconds += 1

                # Flash LEDs to indicate operation ####
                flipFlop += 1
                if flipFlop > 10:
                    GPIO.output(self.redLED, GPIO.HIGH)
                    GPIO.output(self.yellowLED, GPIO.LOW)
                if flipFlop > 20:
                    GPIO.output(self.redLED, GPIO.LOW)
                    GPIO.output(self.yellowLED, GPIO.HIGH)
                    flipFlop = 0

                # Notifications
                timeNow = datetime.now(timezone(config.timeZone)).strftime('%H:%M:%S')
                if action < 1:
                    action += 1
                    print('send first text ', timeNow)
                    message = 'ALARM: fire sprinkler -- FIRST text: ' + timeNow
                    sms.send_SMS_message(message, config.phoneBrad)
                    print('')
                elif runningSeconds >= 60 and action == 1:
                    action += 1
                    print('send second text ', timeNow)
                    message = 'ALARM: fire sprinkler -- SECOND text: ' + timeNow
                    sms.send_SMS_message(message, config.phoneBrad)
                    print('')
                elif runningSeconds >= 120 and action == 2:
                    action += 1
                    print('send third text ', timeNow)
                    message = 'ALARM: fire sprinkler -- THIRD text: ' + timeNow
                    sms.send_SMS_message(message, config.phoneBrad, config.phoneAnn)
                    print('')
                elif runningSeconds >= 200 and runningSeconds/int(60/self.pollingDelay) == int(runningSeconds/int(60/self.pollingDelay)):
                    print('send recurring text ', timeNow)
                    message = 'ALARM: fire sprinkler -- MORE THAN 10 MINUTES: ' + timeNow
                    sms.send_SMS_message(message, config.phoneBrad, config.phoneAnn)
                    print('')

                # check and react to buttonState
                if self.buttonState != 0:
                    # blink yellow LED 5 times
                    for i in range(0, 6):
                        GPIO.output(self.yellowLED, GPIO.HIGH)
                        sleep(.5)
                        GPIO.output(self.yellowLED, GPIO.LOW)
                        sleep(.5)

                    # then exit runTimer and shutdown in main
                    run = False

                # Require buttons to be released before next press
                self.buttonCheckRelease()

    def reactToButton(self, buttonPin):
        '''function call from button interrupt for a single button
        '''
        sleep(.01)  # this is part of the debounce

        self.buttonState = 1

        print('button ', self.buttonState, ' pressed')

    def buttonCheckRelease(self):
        '''sets self.buttonState to 0 only if all buttons are not pressed
        - this is the only place self.buttonState can be set to 0
        - self.buttonState is the button pressed
        '''
        sleep(.01)  # this is part of the debounce

        button1 = GPIO.input(self.pinButton1)

        if button1 == False:
            self.buttonState = 0

def remote_startUp():
    '''function for call from startUpProgram
    This allows auto start up from a common file
    Can also be called in differentdirectory in RPi'''
    app = alarmReact()
    app.runTimer()

    # shut off GPIO and shutdown 
    GPIO.cleanup()
    RPiUtilities.shutdownRPI()

if __name__ == '__main__':
    print('initiate alarm sequence ', datetime.now(timezone(config.timeZone)).strftime('%H:%M:%S'))
    app = alarmReact()
    app.runTimer()

    # shut off GPIO and shutdown 
    GPIO.cleanup()
    RPiUtilities.shutdownRPI()


print('fireAlarm complete')

