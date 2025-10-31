"""
Description:
A simple Streamlit web app that connects to the WeatherBot model (ChatterBot + OpenWeatherMap)
to display live weather information and activity recommendations.
"""

# IMPORTS
import streamlit as st
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import requests
import re


# STREAMLIT UI SETUP
st.set_page_config(page_title="WeatherBot 🌤️", layout="centered")
st.title("🌤️ WeatherBot - Your AI Weather Assistant")


# CHATBOT INITIALIZATION
if "chatbot" not in st.session_state:
    chatbot = ChatBot("WeatherBot")
    trainer = ListTrainer(chatbot)
    trainer.train([
        "hi", "Hello! How can I help you today?",
        "hello", "Hi there! I'm WeatherBot, your friendly weather assistant!",
        "what is your name",
        "My name is WeatherBot. I can help you with weather forecasts and activity recommendations!",
        "thank you", "You're welcome!",
        "bye", "Goodbye! Stay safe and enjoy your day!",
        "what can you do",
        "I can check weather conditions worldwide and recommend if it's good for beach, hiking, or other activities!",
        "help",
        "Just ask me about weather in any city! Try: 'What's the weather in London?' or 'Is it good for beach in Tokyo?'"
    ])
    st.session_state.chatbot = chatbot
    st.session_state.messages = []


# WEATHER API FUNCTIONS

API_KEY = "api_key"


def get_weather(city):
    """
    Gets weather data from OpenWeatherMap API
    Returns: temp, condition, humidity, wind, rain
    """
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()



        print(f"API Response for {city}: {data.get('cod')}")

        if data.get("cod") != 200:
            error_msg = data.get('message', 'Unknown error')
            print(f"API Error: {error_msg}")
            return None

        # Extract weather parameters
        temp = round(data["main"]["temp"])
        cond = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        wind = round(wind_speed * 3.6)  # Convert m/s to km/h
        rain = data.get("rain", {}).get("1h", 0)  # Rain in last hour

        print(f"Weather data for {city}: {temp}°C, {cond}, {humidity}% humidity, {wind} km/h wind, {rain}mm rain")
        return temp, cond, humidity, wind, rain

    except Exception as e:
        print(f"API Exception for {city}: {e}")
        return None



# ACTIVITY RECOMMENDATION LOGIC
def recommend(temp, cond, humidity, wind, rain):

    cond = cond.lower()

    #Extreme cold and snow
    if "snow" in cond or temp <= 0:
        return "❄️ Freezing conditions with snow! Perfect for winter sports if equipped, otherwise stay cozy indoors with hot drinks."

    #Very cold
    elif temp <= 5:
        return "🥶 Very cold! Ideal for museum visits, indoor markets, or warm cafe hopping. Dress in layers!"

    #Heavy rain or storms
    elif "thunderstorm" in cond or rain >= 70:
        return "⛈️ Stormy weather! Stay indoors today. Perfect for museums, cinema, or exploring shopping malls safely."

    #Moderate rain
    elif "rain" in cond or rain >= 40:
        return "🌧️ Rainy day! Good for indoor activities, gallery visits, or city tours with an umbrella."

    #Extreme heat
    elif temp >= 38:
        return "🥵 Extremely hot! Stay in air-conditioned spaces. Early morning or evening outings only with plenty of water."

    #Very high heat
    elif temp >= 35:
        return "🔥 Extremely hot! Beach only in morning/evening. Stay hydrated and avoid strenuous activities."

    #Strong winds
    elif wind >= 30:
        return "💨 Strong winds! Beach swimming not safe. Good for indoor attractions or sheltered exploration."

    #Windy conditions
    elif wind >= 20:
        return "🌬️ Windy day! Beach umbrellas difficult. Good for wind-appropriate activities."

    #High humidity discomfort
    elif humidity >= 85 and temp >= 25:
        return "💦 Hot and humid! Feels much warmer. Light activities recommended with hydration breaks."

    #Excellent beach day
    elif ("clear" in cond or "sun" in cond) and 25 <= temp <= 32 and rain < 10 and wind < 20 and humidity < 80:
        return "🏖️ PERFECT BEACH DAY! Ideal for swimming, sunbathing, snorkeling, and all water activities!"

    #Good beach day
    elif ("clear" in cond or "sun" in cond) and 22 <= temp <= 35 and rain < 20 and wind < 25:
        return "🏝️ Great beach weather! Good for swimming and coastal activities."

    #Excellent hiking day
    elif 15 <= temp <= 28 and rain < 30 and wind < 25 and humidity < 85:
        return "🥾 EXCELLENT hiking weather! Perfect for nature trails, mountain walks, and outdoor adventures."

    #Outdoor Exploration
    elif 18 <= temp <= 30 and rain < 40:
        return "🏙️ Great for outdoor exploration! Ideal for city tours, parks, markets, and sightseeing."

    #Cool but pleasant
    elif 10 <= temp < 18:
        return "🧥 Cool weather! Good for brisk walks, sightseeing with light jacket, and indoor/outdoor mix."

    #Cloudy but dry
    elif ("cloud" in cond or "overcast" in cond) and rain < 20:
        return "⛅ Cloudy but dry! Excellent for outdoor activities without strong sun - perfect for photography."

    #Default for mixed conditions
    else:
        return "🌤️ Mixed weather conditions. Check local forecast and dress in layers for flexible outdoor/indoor activities."




# CHATBOT INTERFACE

# Display chat history
st.subheader("💬 Chat with WeatherBot")
for msg in st.session_state.messages:
    if "🧍‍♀️ You:" in msg:
        st.write(f"**{msg}**")
    else:
        st.write(msg)


# Chat input handler
def send_message():
    user_msg = st.session_state.chat_input.strip()
    if not user_msg:
        return

    # Add user message to chat history
    st.session_state.messages.append(f"🧍‍♀️ You: {user_msg}")

    # Extract city name
    possible_cities = re.findall(r"\b[A-Z][a-zA-Z]+\b", user_msg)

    if possible_cities:
        city = possible_cities[-1]  #Last capitalized word as city



        weather_data = get_weather(city)

        if weather_data:

            temp, cond, humidity, wind, rain = weather_data

            # Activity recommendation based on weather
            suggestion = recommend(temp, cond, humidity, wind, rain)



            weather_report = f"""
🤖 WeatherBot: **Weather Report for {city}** 🌤️

**Current Conditions:**
• Temperature: {temp}°C
• Weather: {cond.title()}
• Humidity: {humidity}%
• Wind Speed: {wind} km/h
• Rainfall: {rain}mm (last hour)

**Activity Recommendation:**
{suggestion}
"""
            st.session_state.messages.append(weather_report)
        else:
            st.session_state.messages.append(
                f"🤖 WeatherBot: Sorry, I couldn't fetch weather data for {city}. Please check the city name and try again.")

    elif any(word in user_msg.lower() for word in ['weather', 'temperature', 'forecast', 'beach', 'hiking']):
        st.session_state.messages.append(
            "🤖 WeatherBot: Please mention a city name! For example: 'What's the weather in Paris?' or 'Is it good for beach in Tokyo?'")

    else:
        # Smalltalk
        try:
            reply = str(st.session_state.chatbot.get_response(user_msg))
            st.session_state.messages.append(f"🤖 WeatherBot: {reply}")
        except:
            st.session_state.messages.append(
                "🤖 WeatherBot: I'm here to help with weather information! Ask me about weather in any city worldwide (Please start city name with capital letter 😉).")

    # Clear input field
    st.session_state.chat_input = ""


# Chat input widget
st.text_input(
    "Type your message:",
    key="chat_input",
    placeholder="Ask about weather in any city (e.g., 'weather in London', 'beach in Tokyo')...",
    on_change=send_message
)



# SIDEBAR WITH INSTRUCTIONS

with st.sidebar:
    st.header("ℹ️ How to Use")
    st.markdown("""
    **Examples to try:**
    - *What's the weather in London?*
    - *Is it good for beach in Tokyo?*
    - *Can I go hiking in Berlin?*
    - *Weather in New York*
    - *Temperature in Sydney*

    **Features:**
    🌤️ Live weather data worldwide
    🏖️ Beach activity recommendations  
    🥾 Hiking condition analysis
    💬 Natural conversation

    Just mention any city name in your message! (Please start city name with capital letter 😉)
    """)

    st.header("🔧 Technical Info")
    st.markdown("""
    **Built with:**
    - Python + Streamlit
    - ChatterBot AI
    - OpenWeatherMap API
    - Machine Learning for recommendations
    """)


# FOOTER

st.markdown("---")
st.markdown("*WeatherBot AI Assistant | Developed by: Kadzuwa Kuyeri*")
