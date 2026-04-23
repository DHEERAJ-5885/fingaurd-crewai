import speech_recognition as sr
import pyttsx3
import requests
import re
import time
from word2number import w2n

recognizer = sr.Recognizer()
engine = pyttsx3.init()

MIC_INDEX = 2  # change if needed


# 🔊 Speak
def speak(text):
    print("FinGuard:", text)
    engine.say(text)
    engine.runAndWait()


# 🎤 STRONG LISTEN (handles pause + avoids cutting speech)
def listen():
    try:
        with sr.Microphone(device_index=MIC_INDEX) as source:
            print("🎤 Listening...")

            recognizer.adjust_for_ambient_noise(source, duration=1)

            recognizer.energy_threshold = 120
            recognizer.pause_threshold = 1.5   # 🔥 waits longer before cutting speech
            recognizer.dynamic_energy_threshold = True

            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)

        text = recognizer.recognize_google(audio)
        print("You:", text)
        return text.lower()

    except sr.UnknownValueError:
        print("❌ Could not understand")
    except sr.WaitTimeoutError:
        print("⏱ Timeout")
    except Exception as e:
        print("Error:", e)

    return None


# 🔢 ULTRA NUMBER EXTRACTION (FIXES ALL YOUR ISSUES)
def extract_number(text):
    if not text:
        return None

    text = text.lower().strip()

    # exit command
    if any(w in text for w in ["exit", "stop", "close", "quit"]):
        return "EXIT"

    # ✅ ZERO handling
    if text in ["0", "zero"]:
        return 0

    # ✅ 2k, 5k
    k_match = re.search(r'(\d+)\s*k', text)
    if k_match:
        return int(k_match.group(1)) * 1000

    # ✅ 5 thousand
    th_match = re.search(r'(\d+)\s*thousand', text)
    if th_match:
        return int(th_match.group(1)) * 1000

    # ✅ Rs 5000 / ₹5000
    money_match = re.search(r'(?:rs|₹)?\s*(\d+)', text)
    if money_match:
        return int(money_match.group(1))

    # ✅ digits like 5000 (no breaking)
    nums = re.findall(r'\d+', text)
    if nums:
        return int("".join(nums))  # 🔥 joins properly

    # ✅ words like "five thousand"
    try:
        return w2n.word_to_num(text)
    except:
        pass

    return None


# 🧠 Parse partial sentence
def parse_partial(text, data):

    if not text:
        return data

    num = extract_number(text)

    if num == "EXIT":
        speak("Goodbye.")
        exit()

    if any(w in text for w in ["earn", "salary", "balance", "have"]):
        if num is not None:
            data["balance"] = num

    if "rent" in text:
        if num is not None:
            data["rent"] = num

    if "food" in text:
        if num is not None:
            data["food"] = num

    if "spend" in text and "future" not in text:
        if num is not None:
            data["spend"] = num

    if "upcoming" in text:
        if num is not None:
            data["upcoming"] = num

    if "future" in text:
        if num is not None:
            data["future_spend"] = num

    if "month" in text:
        if num is not None:
            data["months"] = num

    return data


# 🔥 ASK VALUE (VOICE FIRST → RETRY → TYPE)
def ask_value(key, question, data):

    while data[key] == 0:

        speak(question)

        # 🎤 Try voice 3 times
        for _ in range(3):
            voice = listen()

            if voice:
                num = extract_number(voice)

                if num == "EXIT":
                    speak("Goodbye.")
                    exit()

                if num is not None:
                    data[key] = num
                    return data

                print("⚠️ Not clear, retrying...")

        # ⏳ fallback delay
        print("⌛ Speak again OR type in 5 seconds...")
        time.sleep(5)

        user_input = input("Type here (or Enter to retry): ").lower()

        if user_input in ["exit", "stop", "close", "quit"]:
            speak("Goodbye.")
            exit()

        if user_input == "":
            continue

        num = extract_number(user_input)

        if num is not None:
            data[key] = num
            return data
        else:
            speak("Invalid number.")

    return data


# 🔥 Ask all values
def ask_missing(data):

    flow = [
        ("balance", "Tell me your total balance."),
        ("rent", "What is your monthly rent?"),
        ("food", "How much do you spend on food?"),
        ("upcoming", "Any upcoming expenses?"),
        ("spend", "How much do you want to spend now?"),
        ("future_spend", "Any future big expenses?"),
        ("months", "For how many months should I plan?")
    ]

    for key, question in flow:
        data = ask_value(key, question, data)

    return data


# 🔥 API CALL
def call_api(data):
    try:
        url = "http://127.0.0.1:8000/analyze"

        response = requests.post(url, json=data)

        if response.status_code != 200:
            print("API ERROR:", response.text)
            speak("Server error.")
            return None

        return response.json()

    except Exception as e:
        print("Error:", e)
        speak("Backend not running.")
        return None


# -------- MAIN --------
if __name__ == "__main__":

    speak("Hey, I am FinGuard. Tell me your money situation.")

    while True:

        command = listen()

        if not command:
            speak("I didn't hear you. Try again.")
            continue

        if any(w in command for w in ["exit", "stop", "close", "quit"]):
            speak("Goodbye.")
            break

        data = {
            "balance": 0,
            "rent": 0,
            "food": 0,
            "upcoming": 0,
            "spend": 0,
            "future_spend": 0,
            "months": 0
        }

        # 🔥 smart parsing
        data = parse_partial(command, data)

        # 🔥 fill missing
        data = ask_missing(data)

        speak("Analyzing your finances...")

        result = call_api(data)

        if result:
            speak(f"You have {result['remaining']} rupees left.")
            speak(f"Decision is {result['final_decision']}")