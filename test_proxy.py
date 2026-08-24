import httpx
import asyncio

async def test_proxy()
    # Замените на ваш прокси
    proxy_url = http94.130.86.1103128  # Пример публичного прокси
    
    try
        async with httpx.AsyncClient(proxies=proxy_url, timeout=30.0) as client
            response = await client.get(httpsapi.telegram.org)
            print(f✅ Прокси работает! Статус {response.status_code})
            
            # Проверка с токеном бота
            import config
            response = await client.get(fhttpsapi.telegram.orgbot{config.TELEGRAM_TOKEN}getMe)
            print(f✅ Бот доступен через прокси!)
            print(response.json())
    except Exception as e
        print(f❌ Прокси не работает {e})

if __name__ == __main__
    asyncio.run(test_proxy())