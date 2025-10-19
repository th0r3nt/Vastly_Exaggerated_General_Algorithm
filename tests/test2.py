import asyncio
import datetime

async def toast():
    now1 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Toast made at {now1}")
    await asyncio.sleep(5)
    now2 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Toast finished at {now2}")

async def make_toast():
    print("Making toast...")
    await toast()


if __name__ == "__main__":
    asyncio.run(make_toast())

