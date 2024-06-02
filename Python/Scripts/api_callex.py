import requests

# Replace with your actual API keys and endpoints

weather_url = f"https://api.openweathermap.org/data/2.5/onecall?lat=40.331273&lon=-74.733383&appid=5d4f8bc74b59db309aebec3d5fcd9c1f"

news_api_key = "a05e105f90c94ae7b96addd53d6f86a6"
news_url = "https://api.worldnewsapi.com/search-news?text=openai&language=en"

# Make the API calls
weather_response = requests.get(weather_url)
news_response = requests.get(news_url, params={"apiKey": news_api_key})

# Check if the requests were successful and get JSON data
if weather_response.status_code == 200:
    weather_data = weather_response.json()
    temperature = weather_data["current"]["temp"]
    print(f"Current temperature in Lebanon: {temperature}K")
else:
    print("Failed to retrieve weather data.")

if news_response.status_code == 200:
    news_data = news_response.json()
    print("Today's headlines:")
    for article in news_data["articles"][:5]:  # Show first 5 articles
        print(f"Title: {article['title']}")
else:
    print("Failed to retrieve news data.")
