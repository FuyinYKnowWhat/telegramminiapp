'''
------------------------------------------------------------------------------------------------------------------------------------
CONFIGURACIONES:
'''
from datetime import datetime
import telebot
from telebot import types
import argparse
import cv2
import csv
API_KEY = '7203669480:AAE8M929NIKKHPt26404dYH8t6rzy-B5LPU'
bot = telebot.TeleBot(API_KEY)

'''
------------------------------------------------------------------------------------------------------------------------------------
FUNCIONES:
'''
def guardarStock(stock):
    fichero = open('stock.csv', 'w')
    for elementos in stock:
        fichero.write(f"{elementos['Id']};{elementos['Cantidad']};\n")
    fichero.close()

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


def cargarStock(stock):
    fichero = open('stock.csv', 'r')
    datos = fichero.readlines()
    for linea in datos:
        campos = linea.split(';')
        nuevo = {'Id':campos[0],'Cantidad':campos[1]}
        stock.append(nuevo)
    fichero.close

def current_date_format(date):
    months = ("Enero", "Febrero", "Marzo", "Abri", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
    day = date.day
    month = months[date.month - 1]
    year = date.year
    messsage = str(day)+'_'+month+'_'+str(year)
    return messsage

def copiaSeguridaStock(stock):
    now = datetime.now()
    date = current_date_format(now)
    fichero = open(f'copias de seguridad/CS_stock({date}).csv', 'w')
    for elementos in stock:
        fichero.write(f"{elementos['Id']};{elementos['Cantidad']};\n")
    fichero.close()

def cargarModo(modo):
    fichero = open('modo.csv', 'r')
    datos = fichero.readlines()
    for linea in datos:
        campos = linea.split(';')
        modo[campos[0]] = campos[1]
    fichero.close

def guardarModo(modo,message):
    print(f'Se a cambiado a modo de {modo}')
    bot.reply_to(message,f'modo {modo}')
    fichero = open('modo.csv', 'w')
    if modo == 'stock':
        fichero.write("stock;1;\nproductos;0;\nadmin;0;\n")
    elif modo == 'productos':
        fichero.write("stock;0;\nproductos;1;\nadmin;0;\n")
    elif modo == 'admin':
        fichero.write("stock;0;\nproductos;0;\nadmin;1;\n")
    fichero.close()

def guardarCatalogo(catalogo):
    fichero = open('catalogo.csv', 'w')
    for elementos in catalogo:
        fichero.write(f"{elementos['Id']};{elementos['Nombre']};{elementos['Talla']};\n")
    fichero.close()

def cargarCatalogo(catalogo):
    fichero = open('catalogo.csv', 'r')
    datos = fichero.readlines()
    for linea in datos:
        campos = linea.split(';')
        nuevo = {'Id':campos[0],'Nombre':campos[1],'Talla':campos[2]}
        catalogo.append(nuevo)
    fichero.close   

def editarStock(message):
    stock = []
    cargarStock(stock)
    string = message.text
    campos = string.split(' ')
    if campos[1] != '?':
        for elementos in stock:
            ID = elementos['Id']
            if ID == campos[0]:
                bot.reply_to(message,'then = ' + elementos['Cantidad'])
                elementos['Cantidad'] = int(elementos['Cantidad']) + int(campos[1])
                bot.reply_to(message,'now = ' + str(elementos['Cantidad']))
    elif campos[1] == '?':
        for elementos in stock:
            ID = elementos['Id']
            if ID == campos[0]:
                bot.reply_to(message,elementos['Cantidad'])
                break
    print(stock)
    guardarStock(stock)   

def load_products():
    products = []
    with open('products.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            products.append({
                "BrandName": row["BrandName"], 
                "ItemName": row["ItemName"], 
                "Qty": int(row["Qty"]),
                "Price": float(row.get("Price", 0)),
                "Category": row.get("Category", ""),
                "SKU": row.get("SKU", "")
            })
    return products

products = load_products()

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

'''
------------------------------------------------------------------------------------------------------------------------------------
TELEGRAM:
'''

#LIST ALL PRODUCTS
@bot.message_handler(commands=['listproducts'])
def list_products(message):
    response = "Product List:\n"
    for product in products:
        response += f'{product["BrandName"]} - {product["ItemName"]}: {product["Qty"]} available at {product["Price"]}\n'
    bot.reply_to(message, response)


#START
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    web_app_button = types.KeyboardButton(text="Visit the shop", web_app=types.WebAppInfo(url="https://your-web-app-url"))
    markup.add(web_app_button)
    bot.send_message(message.chat.id, "Welcome! Please choose an option:", reply_markup=markup)
    
#MODOS
@bot.message_handler(commands=['modostock'])
def stock(message):
    guardarModo('stock',message)

@bot.message_handler(commands=['modoproductos'])
def productos(message):
    guardarModo('productos',message)

@bot.message_handler(commands=['modoadmin'])
def admin(message):
    guardarModo('admin',message)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    if call.data == "visit_shop":
        bot.send_message(call.message.chat.id, "Welcome to Jessica's Avocado Stall! 🥑\n\nWhether you're looking for the freshest avocados for your guacamole, seeking some ripe ones for your toast, or just exploring our avocado-themed merchandise, you've come to the right place!\n\nTap on the button below to dive into our green world of avocados today! 🌱", reply_markup=create_shop_button())
    elif call.data == "view_inventory":
        list_products(call.message)
    elif call.data == "get_avocados":
        bot.send_message(call.message.chat.id, "We are open\nShop with us Mon-Sat!\n\nSunday orders delivered on Mon", reply_markup=create_avocado_popup())
    elif call.data == "new_order":
        bot.send_message(call.message.chat.id, "Please enter your order details in the format: Item, Quantity")



@bot.callback_query_handler(func=lambda call: call.data == "new_order")
def new_order(call):
    bot.send_message(call.message.chat.id, "Please enter your order details in the format: Item, Quantity")


#STOCK
@bot.message_handler(commands=['stock'])
def ImprimirStock(message):
    stock = []
    cargarStock(stock)
    stockString = ''
    for elementos in stock:
        stockString = stockString +'\n'+ elementos['Id']+ '-->' + elementos['Cantidad']
    bot.reply_to(message,stockString)

#ANALISIS DE TEXTO
@bot.message_handler(content_types=['text'],)
def ComandoPrincipal(message):
    modo ={}
    cargarModo(modo)
    if modo['stock'] == '1':
        editarStock(message)
    elif modo['productos'] == '1':
        consultarProductos(message)
    elif modo['admin'] == '1':
        bot.reply_to(message,'modo admin')

'''
------------------------------------------------------------------------------------------------------------------------------------
PRUEBAS:
'''

'''
------------------------------------------------------------------------------------------------------------------------------------
MAIN:
'''
now = datetime.now()
date1 = current_date_format(now)
date2 = date1
if __name__ == '__main__':
    print('bot en marcha')
    bot.infinity_polling()
    print('fin')
    #rutina copia de seguridad --> DIARIA
    now = datetime.now()
    date1 = current_date_format(now)
    if date1 != date2:
        stock = []
        cargarStock(stock)
        copiaSeguridaStock(stock)
        date2 = date1

