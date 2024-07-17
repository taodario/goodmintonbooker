import pytest
from datetime import datetime, time, timedelta
import time as time_module

def wait_until_time(desired_hour, desired_minute, desired_seconds):
    desired_time = time(desired_hour, desired_minute, desired_seconds)
    desired_datetime = datetime.combine(datetime.today(), desired_time)
    max_time = desired_datetime + timedelta(seconds=1)

    while True:
        now = datetime.now().time()
        if desired_time <= now < max_time.time():
            print("The desired time has been reached: " + desired_time.strftime("%H:%M:%S"))
            return True
        # loop every 100 ms
        time_module.sleep(0.1)
        print("... waiting... current time is " + now.strftime("%H:%M:%S"))

def test_wait_until_time():
    now = datetime.now()
    # Set desired time to 5 seconds from now
    test_hour = now.hour
    test_minute = now.minute
    test_second = (now.second + 5) % 60

    print(f"Current time: {now.strftime('%H:%M:%S')}")
    print(f"Waiting until: {test_hour:02d}:{test_minute:02d}:{test_second:02d}")
    result = wait_until_time(test_hour, test_minute, test_second)
    assert result is True

if __name__ == "__main__":
    pytest.main()
