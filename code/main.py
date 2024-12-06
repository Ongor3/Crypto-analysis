import os
import requests
import openai
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.config import Config

# Set your OpenAI API key (you can also do this by setting OPENAI_API_KEY in your environment)
openai.api_key = os.environ.get("OPENAI_API_KEY", "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")

# Global coins list
url = 'https://api.coingecko.com/api/v3/coins/list'
response = requests.get(url)
coins_list = response.json()

########################################
# Screen 1: Crypto Price Viewer
########################################

class CryptoPriceViewer(Screen):
    def __init__(self, **kwargs):
        super(CryptoPriceViewer, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.top_label = Label(text='Top 10 Cryptocurrencies', font_size='20sp', size_hint_y=None, height=40)
        self.layout.add_widget(self.top_label)

        # Scrollable area for top cryptocurrencies
        self.scrollview = ScrollView(size_hint=(1, None), size=(self.width, 300))
        self.top_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.top_layout.bind(minimum_height=self.top_layout.setter('height'))
        self.scrollview.add_widget(self.top_layout)
        self.layout.add_widget(self.scrollview)

        # Search Bar
        self.search_layout = BoxLayout(size_hint_y=None, height=40)
        self.search_input = TextInput(hint_text='Enter cryptocurrency name or symbol', size_hint_x=0.7)
        self.search_button = Button(text='Search', size_hint_x=0.3, on_press=self.search_crypto)
        self.search_layout.add_widget(self.search_input)
        self.search_layout.add_widget(self.search_button)
        self.layout.add_widget(self.search_layout)

        # Result Label
        self.result_label = Label(text='', font_size='16sp', size_hint_y=None, height=40)
        self.layout.add_widget(self.result_label)

        # Navigation to second page
        self.nav_button = Button(text='Go to News & AI Analysis', size_hint_y=None, height=40, on_press=self.go_to_news)
        self.layout.add_widget(self.nav_button)

        self.add_widget(self.layout)
        self.refresh_top_cryptos()

    def go_to_news(self, instance):
        self.manager.current = 'news'

    def get_top_cryptocurrencies(self):
        """Fetch the top 10 cryptocurrencies by market cap."""
        url = 'https://api.coingecko.com/api/v3/coins/markets'
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': '10',
            'page': '1',
            'sparkline': 'false'
        }
        response = requests.get(url, params=params)
        data = response.json()
        top_cryptos = []
        for coin in data:
            crypto = {
                'name': coin['name'],
                'symbol': coin['symbol'].upper(),
                'price': "${:,.2f}".format(coin['current_price'])
            }
            top_cryptos.append(crypto)
        return top_cryptos

    def refresh_top_cryptos(self):
        self.top_layout.clear_widgets()
        top_cryptos = self.get_top_cryptocurrencies()
        for crypto in top_cryptos:
            label = Label(text=f"{crypto['name']} ({crypto['symbol']}): {crypto['price']}", size_hint_y=None, height=30)
            self.top_layout.add_widget(label)

    def get_crypto_price(self, crypto_id):
        """Get the current price of a specific cryptocurrency."""
        url = 'https://api.coingecko.com/api/v3/simple/price'
        params = {
            'ids': crypto_id,
            'vs_currencies': 'usd'
        }
        response = requests.get(url, params=params)
        data = response.json()
        if crypto_id in data:
            return data[crypto_id]['usd']
        else:
            return None

    def search_crypto(self, instance):
        """Search for a cryptocurrency by name or symbol and display its price."""
        crypto_name = self.search_input.text.strip()
        if not crypto_name:
            self.result_label.text = "Please enter a cryptocurrency name or symbol."
            return
        crypto_id = None
        display_name = ''
        for coin in coins_list:
            if coin['name'].lower() == crypto_name.lower() or coin['symbol'].lower() == crypto_name.lower():
                crypto_id = coin['id']
                display_name = coin['name']
                break
        if crypto_id:
            price = self.get_crypto_price(crypto_id)
            if price is not None:
                self.result_label.text = f"The current price of {display_name} is ${price:,.2f}"
            else:
                self.result_label.text = "Price not found."
        else:
            self.result_label.text = "Cryptocurrency not found."


########################################
# Screen 2: News, Social Media Trends & AI Analysis
########################################

class NewsScreen(Screen):
    def __init__(self, **kwargs):
        super(NewsScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Title
        self.news_label = Label(text='Recent Crypto News & Trends', font_size='20sp', size_hint_y=None, height=40)
        self.layout.add_widget(self.news_label)

        # Button to fetch news
        self.fetch_button = Button(text='Fetch Latest News & Updates', size_hint_y=None, height=40, on_press=self.fetch_news)
        self.layout.add_widget(self.fetch_button)

        # Scrollable area for news
        self.scrollview = ScrollView(size_hint=(1, None), size=(self.width, 300))
        self.news_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.news_layout.bind(minimum_height=self.news_layout.setter('height'))
        self.scrollview.add_widget(self.news_layout)
        self.layout.add_widget(self.scrollview)

        # AI Interaction
        self.ai_input_layout = BoxLayout(size_hint_y=None, height=40)
        self.ai_input = TextInput(hint_text='Ask the AI (e.g., Why is Bitcoin trending?)', size_hint_x=0.7)
        self.ai_button = Button(text='Ask AI', size_hint_x=0.3, on_press=self.ask_ai)
        self.ai_input_layout.add_widget(self.ai_input)
        self.ai_input_layout.add_widget(self.ai_button)
        self.layout.add_widget(self.ai_input_layout)

        # AI Result Label
        self.ai_result_label = Label(text='', font_size='16sp', size_hint_y=None, height=100)
        self.layout.add_widget(self.ai_result_label)

        # Back to main page
        self.back_button = Button(text='Back to Prices', size_hint_y=None, height=40, on_press=self.go_back)
        self.layout.add_widget(self.back_button)

        self.add_widget(self.layout)

        self.fetched_news = []  # Store fetched news items for context

    def go_back(self, instance):
        self.manager.current = 'prices'

    def update_label_text_size(self, instance, size):
        instance.text_size = (size[0], None)

    def fetch_news(self, instance):
        """Fetch recent crypto-related news or status updates for sentiment analysis."""
        # Using CoinGecko's Status Updates endpoint as a placeholder for news/social media trends
        url = "https://api.coingecko.com/api/v3/status_updates"
        response = requests.get(url)
        data = response.json()
        updates = data.get('status_updates', [])

        self.news_layout.clear_widgets()
        self.fetched_news = []

        # Limit to top 5 updates for brevity
        for update in updates[:5]:
            title = update.get('project', {}).get('name', 'Unknown Project')
            description = update.get('description', 'No Description')
            self.fetched_news.append(description)
            label_text = f"[{title}] {description}"
            label = Label(
                text=label_text,
                font_size='14sp',
                size_hint_y=None,
                height=60,
                halign='left',
                valign='top'
            )
            label.text_size = (None, None)  # Explicitly set the text size to wrap
            label.bind(size=self.update_label_text_size)
            self.news_layout.add_widget(label)

        # After fetching news, we could analyze sentiment
        # For demonstration, we won't call sentiment analysis automatically, but we could.

    def ask_ai(self, instance):
        """Send the user's question along with recent news to OpenAI for a contextual answer."""
        user_question = self.ai_input.text.strip()
        if not user_question:
            self.ai_result_label.text = "Please enter a question for the AI."
            return

        # Combine fetched news into a context prompt
        context = "Here are some recent cryptocurrency updates:\n"
        for idx, item in enumerate(self.fetched_news, start=1):
            context += f"{idx}. {item}\n"

        # Prompt for the model
        prompt = (f"{context}\n"
                  f"User question: {user_question}\n\n"
                  f"Answer the user’s question as best as you can, analyzing sentiment and context.")

        # Call OpenAI API
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "You are a helpful crypto analyst."},
                          {"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            answer = response.choices[0].message['content'].strip()
            self.ai_result_label.text = answer
        except Exception as e:
            self.ai_result_label.text = f"Error: {str(e)}"


########################################
# App and ScreenManager
########################################

class CryptoApp(App):
    def build(self):
        sm = ScreenManager()
        prices_screen = CryptoPriceViewer(name='prices')
        news_screen = NewsScreen(name='news')

        sm.add_widget(prices_screen)
        sm.add_widget(news_screen)
        sm.current = 'prices'
        return sm


if __name__ == '__main__':
    CryptoApp().run()
