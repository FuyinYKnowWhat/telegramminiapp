'''
------------------------------------------------------------------------------------------------------------------------------------
CONFIGURACIONES:
'''
from datetime import datetime
import telebot
from telebot import types
import csv
import json
import pandas as pd

API_KEY = '7360378964:AAHgR-GFM0Q2yFtsXJ73Dl6o2gvfQiy8Ckw'
bot = telebot.TeleBot(API_KEY)

'''
------------------------------------------------------------------------------------------------------------------------------------
FUNCIONES:
'''

def create_inline_menu():
    keyboard = types.InlineKeyboardMarkup()
    shop_button = types.InlineKeyboardButton(text="Visit the shop", callback_data="visit_shop")
    inventory_button = types.InlineKeyboardButton(text="View inventory list", callback_data="view_inventory")
    keyboard.add(shop_button, inventory_button)
    return keyboard


def create_shop_button():
    keyboard = types.InlineKeyboardMarkup()
    shop_button = types.InlineKeyboardButton(text="Get your avocados!", callback_data="get_avocados")
    keyboard.add(shop_button)
    return keyboard

def create_avocado_popup():
    keyboard = types.InlineKeyboardMarkup()
    new_order_button = types.InlineKeyboardButton(text="Avocado with BB", callback_data="new_order")
    keyboard.add(new_order_button)
    return keyboard


def load_brands():
    df = pd.read_excel('products.xlsx', sheet_name='Brand', header=None)
    brands = []

    # Initialize column index
    col_start = 0

    while col_start < df.shape[1]:
        # Check if the column is the beginning of a new section (by checking if the header exists)
        if pd.notna(df.iloc[0, col_start]):
            section = df.iloc[:, col_start:col_start + 4].dropna(how='all')
            section.columns = ["ID", "ParentID", "Type", "Name"]  # Assign proper column names
            section_dict = section.iloc[1:].to_dict(orient='records')
            brands.extend(section_dict)
        
        # Move to the next possible section
        col_start += 5  # Assuming a 1-column gap between sections

    # Write the collected data to JSON
    with open('brands.json', 'w') as json_file:
        json.dump(brands, json_file, indent=4)

    print(f"Extracted {len(brands)} brand records.")


def load_items():
    df = pd.read_excel('products.xlsx', sheet_name='Item', header=None)
    items = []

    col_start = 0

    while col_start < df.shape[1]:
        if pd.notna(df.iloc[0, col_start]):
            section = df.iloc[:, col_start:col_start + 7].dropna(how='all')  # Update to 7 columns
            section.columns = ["ID", "ParentID", "Type", "Name", "Qty", "ParentName", "Code"]  # Add "Code" here
            section_dict = section.iloc[1:].to_dict(orient='records')
            items.extend(section_dict)
        
        col_start += 8  # Update the skip to 8 columns

    with open('items.json', 'w') as json_file:
        json.dump(items, json_file, indent=4)

    print(f"Extracted {len(items)} item records.")


def load_prices():
    df = pd.read_excel('products.xlsx', sheet_name='Price', header=0)
    prices = []

    for _, row in df.iterrows():
        price_record = {
            "AccountID": row['Account ID'],
            "ItemID": row['ItemID'],
            "Price": row['Price'] if pd.notna(row['Price']) else "NA",
            "Notes": row['Notes']
        }
        prices.append(price_record)
    
    with open('prices.json', 'w') as json_file:
        json.dump(prices, json_file, indent=4)

    print(f"Extracted {len(prices)} price records.")


# Include this function in the main execution block
if __name__ == '__main__':
    load_brands()
    load_items()
    load_prices()  # Add this line
    print('JSON files generated.')


def consultarProductos(message):
    chat_id = 5608085328
    catalogo = []
    cargarCatalogo(catalogo)
    string = message.text
    campos = string.split(' ')
    for elementos in catalogo:
        if elementos['Id'] == campos[0]:
            bot.send_photo(chat_id,photo=open(f'catalogo/{campos[0]}.png', 'rb'))
            bot.reply_to(message,f"{elementos['Nombre']} | {elementos['Talla']}")


def create_shop_webapp_button():
    keyboard = types.InlineKeyboardMarkup()
    shop_button = types.InlineKeyboardButton(
        text="Visit the shop",
        web_app=types.WebAppInfo(url="https://fuyinyknowwhat.github.io/telegramminiapp/")
    )
    keyboard.add(shop_button)
    return keyboard



'''
------------------------------------------------------------------------------------------------------------------------------------
TELEGRAM:
'''

#LIST ALL PRODUCTS
@bot.message_handler(commands=['list'])
def list_inventory(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Here is the inventory list...")
    # Implement the inventory list display logic here



# Set the menu button to display only the hamburger icon
def set_menu_button(chat_id):
    menu_button = types.MenuButtonCommands(
        text=""  # Setting the text to an empty string to display only the hamburger icon
    )
    bot.set_chat_menu_button(chat_id=chat_id, menu_button=menu_button)


#MODOS


# Start command handler
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    chat_id = message.chat.id
    set_menu_button(chat_id)
    bot.send_message(chat_id, "Welcome to the shop! Use the menu to visit the shop or view the inventory list.")


# Command handler for visiting the shop
@bot.message_handler(commands=['visitshop'])
def visit_shop(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Click the button below to visit the shop.", reply_markup=create_shop_webapp_button())


# Command handler for viewing the inventory
@bot.message_handler(commands=['viewinventory'])
def view_inventory(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Here is the inventory list...")
    # Implement the inventory list display logic here


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    if call.data == "visit_shop":
        bot.send_message(call.message.chat.id, "Welcome to Jessica's Avocado Stall! 🥑\n\nWhether you're looking for the freshest avocados for your guacamole, seeking some ripe ones for your toast, or just exploring our avocado-themed merchandise, you've come to the right place!\n\nTap on the button below to dive into our green world of avocados today! 🌱", reply_markup=create_shop_button())
    elif call.data == "view_inventory":
        list_inventory(call.message)
    elif call.data == "get_avocados":
        bot.send_message(call.message.chat.id, "We are open\nShop with us Mon-Sat!\n\nSunday orders delivered on Mon", reply_markup=create_avocado_popup())
    elif call.data == "new_order":
        bot.send_message(call.message.chat.id, "Please enter your order details in the format: Item, Quantity")



@bot.callback_query_handler(func=lambda call: call.data == "new_order")
def new_order(call):
    bot.send_message(call.message.chat.id, "Please enter your order details in the format: Item, Quantity")


#STOCK


#ANALISIS DE TEXTO


'''
------------------------------------------------------------------------------------------------------------------------------------
PRUEBAS:
'''

'''
------------------------------------------------------------------------------------------------------------------------------------
MAIN:
'''
now = datetime.now()
if __name__ == '__main__':
    print('Bot Running!')
    bot.infinity_polling()
    print('fin')
    #rutina copia de seguridad --> DIARIA
    now = datetime.now()


