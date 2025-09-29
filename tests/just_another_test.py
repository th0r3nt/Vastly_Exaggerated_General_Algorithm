import datetime

now = datetime.datetime.now()
time_str = now.strftime("%H:%M")

print(f"Definitely not now {time_str}")