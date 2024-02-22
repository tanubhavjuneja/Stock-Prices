import customtkinter as ctk
from PIL import Image
import yfinance as yf
import time as tm
from datetime import datetime,time
from apscheduler.schedulers.background import BackgroundScheduler
import tkfilebrowser
import os
stock_data = {'HDFCBANK.BO':'HDFC Bank','COALINDIA.BO': 'Coal India', 'HUDCO.BO': 'HUDCO', 'ONGC.BO': 'ONGC', 'ADANIGREEN.BO': 'Adani Green', 'VEDL.BO': 'Vedanta', 'PAYTM.BO': 'Paytm', 'TITAN.BO': 'Titan', 'GAIL.BO': 'GAIL'}
scheduler=None
def check_market():
    global scheduler,scheduler_running
    if scheduler==None:
        scheduler = BackgroundScheduler()
    if datetime.today().weekday() != "Sunday" or "Saturday":
        if time(9, 15) <= datetime.now().time()<= time(15,30):
            scheduler_running=True
            scheduler.add_job(update_stock_prices,'interval', seconds=1, max_instances=150)
            scheduler.start()
            return
    scheduler_running=False
    scheduler.add_job(check_market, trigger='cron', hour=9, minute=15)
    scheduler.start()
def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="2d")
    return data
def close_window():
    global scheduler
    scheduler.shutdown(wait=False)
    tm.sleep(1)
    stock_window.destroy()
def check_open():
    global scheduler,count,count1,scheduler_running
    if count>50:
        scheduler.shutdown(wait=False)
        scheduler_running=False
        scheduler = BackgroundScheduler()
        scheduler.add_job(check_market, trigger='cron', hour=9, minute=15)
        scheduler.start()
    if count1>5:
        scheduler.shutdown(wait=False)
        scheduler=None
        check_market()
    for i, (symbol, name) in enumerate(stock_data.items()):
        stock_info = get_stock_data(symbol)
        if stock_info.empty or len(stock_info) < 2:
            count+=1
        else:
            count=0
            count1+=1
def get_stock_prices():
    global price_labels,count,previous_close,scheduler,count1,scheduler_running,gap_labels
    count=0
    count1=0
    gap_labels=[]
    price_labels=[]
    if scheduler_running==True:
        scheduler.add_job(check_open,'interval', seconds=1, max_instances=150)
    for i, (symbol, name) in enumerate(stock_data.items()):
        while True:
            try:
                stock_info = get_stock_data(symbol)
                if stock_info.empty or len(stock_info) < 2:
                    break  # Break the inner loop if no data is found
                current_price = (stock_info['Close'].iloc[-1]) // 0.01 / 100
                previous_close = stock_info['Close'].iloc[-2]
                stock_label = ctk.CTkLabel(stock_frame, height=30, width=200, anchor="w", font=("Arial", 15, "bold"),
                                            text=f"{name}", fg_color="gray14")
                stock_label.grid(row=i, column=0, sticky='w')
                gap = (current_price - previous_close) // 0.01 / 100
                gap_per = gap / current_price * 100 // 0.01 / 100
                gap_label = ctk.CTkLabel(stock_frame, height=30, width=100, anchor="e", font=("Arial", 15, "bold"),
                                            text=f"{gap}({gap_per}%)", fg_color="gray14")
                gap_label.grid(row=i, column=1, sticky='e')
                gap_labels.append(gap_label)
                price_label = ctk.CTkLabel(stock_frame, text=f"{current_price}", width=80,
                                            font=("Arial", 20, "bold"),
                                            text_color="green" if current_price > previous_close else "red",
                                            fg_color="gray14", bg_color="gray14")
                price_label.grid(row=i, column=2, sticky='e')
                price_labels.append(price_label)
                break 
            except Exception as e:
                time.sleep(5) 
                continue
def update_stock_prices():
    global price_labels,scheduler,count,scheduler_running,gap_labels
    for i, (symbol, name) in enumerate(stock_data.items()):
        stock_info = get_stock_data(symbol)
        if stock_info.empty or len(stock_info) < 2:
            continue
        current_price = (stock_info['Close'].iloc[-1])//0.01/100
        previous_close = stock_info['Close'].iloc[-2]
        gap=(current_price-previous_close)//0.01/100
        gap_per=gap/current_price*100//0.01/100
        gap_label=gap_labels[i]
        price_label = price_labels[i]
        gap_label.configure(text=f"{gap}({gap_per}%)")
        price_label.configure(text=f"{current_price}", text_color="green" if current_price > previous_close else "red")
        print(current_price)
    if time(15,30)<datetime.now().time():
        scheduler.shutdown(wait=False)
        scheduler=None
        scheduler_running=False
        check_market()
def read_file_location():
    global mfl
    try:
        file=open('stock_location.txt', 'r')
        mfl = file.read().strip()
        file.close()
        if not os.path.isfile(os.path.join(mfl, 'close.png')):
            get_file_location()
    except FileNotFoundError:
        get_file_location()
def get_file_location():
    global main
    main=ctk.CTk()
    main.geometry("200x50+860+420")
    main.attributes('-topmost', True)
    main.attributes("-alpha",100.0)
    main.lift()
    file_button = ctk.CTkButton(main, text="Select File Location",command=select_file_location,width=1)
    file_button.pack(pady=10)
    main.mainloop()
def select_file_location():
    global main
    mfl = str(tkfilebrowser.askopendirname())+"/"
    mfl = mfl.replace('\\', '/')
    file=open('stock_location.txt', 'w')
    file.write(mfl)
    file.close()
    main.destroy()
    read_file_location()
read_file_location()
stock_window = ctk.CTk()
stock_window.title("Mood")
stock_window.geometry("420x340+1490+500")
stock_window.overrideredirect(True)
close_icon = ctk.CTkImage(Image.open(mfl + "close.png"), size=(13, 13))
close_button = ctk.CTkButton(stock_window, image=close_icon, command=close_window, fg_color="gray14", text="", width=1)
close_button.place(relx=0.928, rely=0.01)
stock_label = ctk.CTkLabel(stock_window, text="Stock Prices", font=("Arial", 20, "bold"))
stock_label.place(relx=0.05, rely=0.02)
stock_frame = ctk.CTkFrame(stock_window,fg_color="gray14")
stock_frame.place(relx=0.05, rely=0.2)
check_market()
get_stock_prices()
stock_window.mainloop()