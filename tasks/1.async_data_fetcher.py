import os
import logging
import asyncio
import aiohttp
import dotenv
import pandas as pd
from aiohttp.client_exceptions import ClientError

logging.basicConfig(level=logging.INFO, format="%(asctime)s, %(message)s")
dotenv.load_dotenv()

CITIES = [
            "Moscow", "Saint Petersburg", "Novosibirsk", "Yekaterinburg", "Kazan",
            "Nizhny Novgorod", "Chelyabinsk", "Samara", "Omsk", "Rostov-on-Don",
            "Ufa", "Krasnoyarsk", "Voronezh", "Perm", "Volgograd", 
            "Krasnodar", "Saratov", "Tyumen", "Tolyatti", "Izhevsk",
            "Barnaul", "Irkutsk", "Khabarovsk", "Yaroslavl", "Vladivostok",
            "Tomsk", "Kemerovo", "Astrakhan", "Nizhny Tagil", "Sochi", 
        ]

async def fetch_data(url) -> dict | None:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
    except ClientError as e:
        logging.error(f"ClientError while fetching data: {e}")
    except Exception as e:
        logging.error(f"Error while fetching data: {e}")

async def fetch_all_weather_data() -> list[dict]:
    result = []
    for city in CITIES:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city},ru&appid={os.getenv('OPENWEATHER_API_KEY')}&units=metric"
        data = await fetch_data(url)
        if not data:
            logging.error(f"No data for {city}")
            continue
        try:
            city_data = {
                "city": city,
                "temperature": data["main"]["temp"],
                "description": data["weather"][0]["description"],
                "pressure": data["main"]["pressure"],
                "humidity": data["main"]["humidity"],
                "wind wpeed": data["wind"]["speed"]
            }
            result.append(city_data)
        except (KeyError, IndexError) as e:
            logging.error(f"Error while parsing data for {city}: {e}")
    return result

async def fetch_news_data() -> list[dict]:
    result = []
    url = f"https://newsapi.org/v2/everything?q=PC+gaming&apiKey={os.getenv('NEWS_API_KEY')}&language=en&pageSize=25"
    data = await fetch_data(url)
    if not data:
        logging.error(f"No data for news")
        return result
    try:
        for article in data["articles"]:
            article_data = {
                "title": article["title"],
                "description": article["description"],
                "url": article["url"],
                "source": article["source"]["name"],
                "author": article["author"],
                "published at": article["publishedAt"]
            }
            result.append(article_data)
    except (KeyError, IndexError) as e:
        logging.error(f"Error while parsing news data: {e}")
    return result

async def fetch_random_users() -> list[dict]:
    result = []
    url = "https://randomuser.me/api/?results=10"
    data = await fetch_data(url)
    if not data:
        logging.error(f"No data for random users")
        return result
    try:
        for user in data["results"]:
            user_data = {
                "name": f"{user['name']['first']} {user['name']['last']}",
                "gender": user["gender"],
                "email": user["email"],
                "phone": user["phone"],
                "country": user["location"]["country"],
                "city": user["location"]["city"],
                "age": user["dob"]["age"]
            }
            result.append(user_data)
    except (KeyError, IndexError) as e:
        logging.error(f"Error while parsing random users data: {e}")
    return result

async def write_data_to_file(data: list[dict], sheet_name: str) -> None:
    if not data:
        logging.error(f"No data to write to {sheet_name} sheet")
        return
    df = pd.DataFrame(data)
    with pd.ExcelWriter("result.xlsx", mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    logging.info(f"{sheet_name.title()} data has been written to file")

async def main():
    weather_data = await fetch_all_weather_data()
    await write_data_to_file(weather_data, "weather")
    news_data = await fetch_news_data()
    await write_data_to_file(news_data, "news")
    random_users = await fetch_random_users()
    await write_data_to_file(random_users, "users")
    logging.info("All data has been fetched and written to file")

asyncio.run(main())