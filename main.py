import flet as ft
import requests
from datetime import datetime

API_KEY = "430974a0a26e5120d4c78d063715b655"
BASE_URL_CURRENT = "http://api.openweathermap.org/data/2.5/weather"
BASE_URL_FORECAST = "http://api.openweathermap.org/data/2.5/forecast"

def main(page: ft.Page):
    page.title = "Weather App"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30

    def get_weather_icon(icon_code):
        return f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

    # تابع جدید: پیشنهادهای هوشمند بر اساس وضعیت آب‌وهوا
    def get_weather_recommendation(weather_condition):
        recommendations = {
            "rain": "☔ امروز بارانی است! چتر همراه داشته باشید.",
            "snow": "❄️ برف می‌بارد! لباس گرم بپوشید و مراقب یخ‌زدگی جاده‌ها باشید.",
            "clear": "☀️ هوا آفتابی است! کرم ضدآفتاب فراموش نشود.",
            "clouds": "☁️ هوا ابری است. احتمال بارش مختصر وجود دارد.",
            "thunderstorm": "⚡ توفان رعد و برق در راه است! در صورت امکان در خانه بمانید.",
            "drizzle": "🌧️ باران نم نم است. ژاکت مناسب بپوشید.",
            "mist": "🌫️ مه آلود است. در رانندگی احتیاط کنید.",
            "smoke": "💨 هوا آلوده است. از ماسک استفاده کنید.",
            "haze": "😷 هوا غبارآلود است. فعالیت‌های بیرونی را محدود کنید.",
            "fog": "🌁 مه سنگین است. دید کم است.",
            "dust": "💨 گرد و غبار در هوا زیاد است. پنجره‌ها را ببندید.",
            "sand": "🏜️ طوفان شن! از بیرون رفتن خودداری کنید.",
            "ash": "🌋 خاکستر آتشفشانی در هوا! ماسک بزنید.",
            "squall": "🌬️ بادهای شدید در راه است. مراقب باشید.",
            "tornado": "🌪️ احتمال طوفان شدید! به پناهگاه بروید."
        }
        
        # تبدیل توصیه به فارسی (اختیاری)
        return recommendations.get(weather_condition.lower(), "✅ شرایط جوی عادی است. روز خوبی داشته باشید!")

    city_input = ft.TextField(
        label="نام شهر را وارد کنید",
        width=300,
        autofocus=True,
        suffix=ft.IconButton(
            icon=ft.icons.SEARCH,
            on_click=lambda e: fetch_weather(city_input.value)
        )
    )

    weather_info = ft.Column()

    def create_forecast_item(entry):
        date = datetime.strptime(entry['dt_txt'], "%Y-%m-%d %H:%M:%S")
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(date.strftime("%a"), size=14),
                    ft.Image(
                        src=get_weather_icon(entry['weather'][0]['icon']),
                        width=40,
                        height=40
                    ),
                    ft.Text(f"{entry['main']['temp']:.1f}°C"),
                    ft.Text(
                        f"{entry['main']['temp_min']:.0f}°|{entry['main']['temp_max']:.0f}°",
                        size=12
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5
            ),
            padding=10,
            border_radius=10,
            border=ft.border.all(1, ft.colors.BLUE_100),
            bgcolor=ft.colors.BLUE_50
        )

    def fetch_weather(city):
        if not city:
            return
            
        try:
            # Current weather
            current_params = {"q": city, "appid": API_KEY, "units": "metric"}
            current_res = requests.get(BASE_URL_CURRENT, params=current_params).json()
            if current_res["cod"] != 200:
                raise Exception(current_res["message"])
            
            # Forecast
            forecast_params = {"q": city, "appid": API_KEY, "units": "metric", "cnt": 40}
            forecast_res = requests.get(BASE_URL_FORECAST, params=forecast_params).json()
            if forecast_res["cod"] != "200":
                raise Exception(forecast_res["message"])

            weather_info.controls.clear()
            
            # دریافت پیشنهاد هوشمند
            weather_condition = current_res["weather"][0]["main"].lower()
            recommendation = get_weather_recommendation(weather_condition)
            
            # Current weather section
            current_main = ft.Row(
                controls=[
                    ft.Image(
                        src=get_weather_icon(current_res["weather"][0]["icon"]),
                        width=100,
                        height=100
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(f"{current_res['main']['temp']:.1f}°C", size=40),
                            ft.Text(current_res["weather"][0]["description"].capitalize()),
                            ft.Text(f"احساس واقعی {current_res['main']['feels_like']:.1f}°C")
                        ]
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER
            )
            
            current_details = ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text("رطوبت", color=ft.colors.BLUE),
                            ft.Text(f"{current_res['main']['humidity']}%")
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    ft.Column(
                        controls=[
                            ft.Text("باد", color=ft.colors.BLUE),
                            ft.Text(f"{current_res['wind']['speed']} m/s")
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    ft.Column(
                        controls=[
                            ft.Text("فشار", color=ft.colors.BLUE),
                            ft.Text(f"{current_res['main']['pressure']} hPa")
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    )
                ],
                spacing=30,
                alignment=ft.MainAxisAlignment.CENTER
            )

            # Forecast section
            forecast_items = []
            seen_dates = set()
            for entry in forecast_res["list"]:
                entry_date = entry["dt_txt"].split()[0]
                if entry_date not in seen_dates:
                    seen_dates.add(entry_date)
                    forecast_items.append(create_forecast_item(entry))
                if len(seen_dates) == 5:
                    break

            forecast_row = ft.Row(
                controls=forecast_items,
                spacing=20,
                scroll=ft.ScrollMode.AUTO
            )

            weather_info.controls.extend([
                ft.Text(current_res["name"], size=30, weight=ft.FontWeight.BOLD),
                current_main,
                current_details,
                ft.Divider(height=20),
                # اضافه کردن بخش پیشنهادهای هوشمند
                ft.Container(
                    content=ft.Text(recommendation, size=16, color=ft.colors.BLUE_800),
                    padding=10,
                    border_radius=10,
                    bgcolor=ft.colors.BLUE_100,
                    margin=10
                ),
                ft.Text("پیش‌بینی 5 روز آینده", size=20, weight=ft.FontWeight.BOLD),
                forecast_row
            ])
            
        except Exception as e:
            weather_info.controls.clear()
            weather_info.controls.append(
                ft.Text(f"خطا: {str(e).capitalize()}", color=ft.colors.RED)
            )
        
        page.update()

    page.add(
        ft.Column(
            [
                city_input,
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                ft.Container(
                    content=weather_info,
                    padding=20,
                    border_radius=10,
                    border=ft.border.all(2, ft.colors.BLUE_100),
                    bgcolor=ft.colors.BLUE_50
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

if __name__ == "__main__":
    ft.app(target=main)