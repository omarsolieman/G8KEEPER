import time
import board
import busio
import adafruit_ds3231

# Create the I2C object with custom SDA/SCL pins
i2c = busio.I2C(scl=board.GP21, sda=board.GP20)

# Create the RTC instance
rtc = adafruit_ds3231.DS3231(i2c)

# Check if the RTC has a valid date and time set
invalid_datetime = time.struct_time((2000, 1, 1, 0, 0, 0, 0, 0, 0))
is_rtc_initialized = rtc.datetime != invalid_datetime

while True:
    print("\nRTC Menu:")
    print("1. Set the time")
    print("2. Check the time")
    print("3. Check status and connection")
    print("4. Exit")
    choice = input("Enter your choice (1-4): ")

    if choice == "1":
        if is_rtc_initialized:
            print("RTC is already initialized.")
            year = int(input("Enter year (YYYY): "))
            month = int(input("Enter month (MM): "))
            day = int(input("Enter day (DD): "))
            hour = int(input("Enter hour (HH): "))
            minute = int(input("Enter minute (MM): "))
            second = int(input("Enter second (SS): "))

            new_time = time.struct_time((year, month, day, hour, minute, second, 0, -1, -1))
            rtc.datetime = new_time
            print("RTC initialized with the new time.")
            is_rtc_initialized = True
        else:
            year = int(input("Enter year (YYYY): "))
            month = int(input("Enter month (MM): "))
            day = int(input("Enter day (DD): "))
            hour = int(input("Enter hour (HH): "))
            minute = int(input("Enter minute (MM): "))
            second = int(input("Enter second (SS): "))

            new_time = time.struct_time((year, month, day, hour, minute, second, 0, -1, -1))
            rtc.datetime = new_time
            print("RTC initialized with the new time.")
            is_rtc_initialized = True

    elif choice == "2":
        if is_rtc_initialized:
            current_time = rtc.datetime
            print("Current Time:", current_time)
        else:
            print("RTC is not initialized yet.")

    elif choice == "3":
        if is_rtc_initialized:
            print("RTC is initialized and connected.")
            temp_c = rtc.temperature
            temp_f = temp_c * 9 / 5 + 32
            print("Temperature: %0.2f C (%0.2f F)" % (temp_c, temp_f))
        else:
            print("RTC is not initialized or not connected properly.")

    elif choice == "4":
        print("Exiting...")
        break

    else:
        print("Invalid choice. Please try again.")