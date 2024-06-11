# rtc_setup.py
import time
import board
import busio
import adafruit_ds3231

class RTCManager:
    def __init__(self, i2c):
        self.i2c = i2c
        self.rtc = adafruit_ds3231.DS3231(self.i2c)

    def handle_set_time(self):
        # Prompt the user for input to set the RTC time
        print("Enter the current date and time:")
        year = int(input("Year (YYYY): "))
        month = int(input("Month (MM): "))
        day = int(input("Day (DD): "))
        hour = int(input("Hour (HH): "))
        minute = int(input("Minute (MM): "))
        second = int(input("Second (SS): "))

        # Set the RTC time using the user input
        self.rtc.datetime = time.struct_time((year, month, day, hour, minute, second, 0, -1, -1))
        print("RTC time set successfully!")

    def handle_check_time(self):
        # Get the current time from the RTC
        current_time = self.rtc.datetime
        return current_time

    def handle_check_status(self):
        # Get the current temperature from the RTC
        temp_c = self.rtc.temperature
        temp_f = temp_c * 9/5 + 32
        return temp_c, temp_f