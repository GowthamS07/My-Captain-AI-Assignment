# -*- coding: utf-8 -*-
"""
Created on Sun Apr 27 23:43:08 2025

@author: Gowtham S
"""

from nicegui import ui
import pandas as pd
import datetime

# --- Session Variables ---
winnings_selected = []
lottery_selected = []
money_received = 0
total = 0
ticket_books = {i: 49 for i in range(1, 109)}  # Each box starts at 49
sales_log = []

# --- Dynamic Labels ---
total_label = None
money_received_label = None
change_label = None
right_drawer_frame = None

# --- Functions ---

def recalculate_totals():
    global total
    total = sum(5 for _ in lottery_selected) - sum(winnings_selected)

    if total_label:
        total_label.text = f"Total Due: ${total}"
    if money_received_label:
        money_received_label.text = f"Money Received: ${money_received}"
    if change_label:
        if money_received == 0:
            change_label.text = "Change to Return: $0"
        else:
            change_label.text = f"Change to Return: ${money_received - total}"

def add_winning(amount):
    winnings_selected.append(amount)
    refresh_right_drawer()
    recalculate_totals()

def add_lottery(ticket_number):
    lottery_selected.append(ticket_number)
    if ticket_books.get(ticket_number, 0) > 0:
        ticket_books[ticket_number] -= 1  # Decrease ticket count
    refresh_right_drawer()
    recalculate_totals()

def add_money(amount):
    global money_received
    money_received += amount
    recalculate_totals()

def pay_exact_amount():
    global money_received
    if total != 0:
        money_received += total
    recalculate_totals()

def remove_winning(index):
    winnings_selected.pop(index)
    refresh_right_drawer()
    recalculate_totals()

def remove_lottery(index):
    ticket_number = lottery_selected.pop(index)
    ticket_books[ticket_number] += 1  # Restore ticket count
    refresh_right_drawer()
    recalculate_totals()

def undo_last_selection():
    if lottery_selected:
        ticket_number = lottery_selected.pop()
        ticket_books[ticket_number] += 1
    elif winnings_selected:
        winnings_selected.pop()
    refresh_right_drawer()
    recalculate_totals()

def reset_all():
    global winnings_selected, lottery_selected, money_received, total
    winnings_selected.clear()
    lottery_selected.clear()
    money_received = 0
    total = 0
    refresh_right_drawer()
    recalculate_totals()

def save_sale():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sale_data = {
        "timestamp": timestamp,
        "total_due": total,
        "money_received": money_received,
        "change_to_return": money_received - total,
        "winnings_selected": winnings_selected.copy(),
        "lottery_selected": lottery_selected.copy(),
    }
    sales_log.append(sale_data)

    df = pd.DataFrame(sales_log)
    df.to_csv('sales_log.csv', index=False)

    ui.notify("Sale Saved ✅")
    reset_all()

def refresh_right_drawer():
    right_drawer_frame.clear()
    with right_drawer_frame:
        ui.label('Selections').classes('text-xl font-bold')

        ui.label('Winnings Selected:')
        for idx, win in enumerate(winnings_selected):
            with ui.row():
                ui.label(f"${win}")
                ui.button('❌', on_click=lambda i=idx: remove_winning(i))

        ui.separator()

        ui.label('Lottery Boxes Selected:')
        for idx, lot in enumerate(lottery_selected):
            with ui.row():
                ui.label(f"{lot}")
                ui.button('❌', on_click=lambda i=idx: remove_lottery(i))

# --- Pages ---

@ui.page('/')
def sales_page():
    global total_label, money_received_label, change_label, right_drawer_frame

    # LEFT DRAWER (Summary)
    with ui.left_drawer().classes('bg-white p-4'):
        ui.label('Summary').classes('text-xl font-bold')
        total_label = ui.label(f"Total Due: ${total}")
        money_received_label = ui.label(f"Money Received: ${money_received}")
        change_label = ui.label(f"Change to Return: ${money_received - total}")

    # RIGHT DRAWER (Selections)
    with ui.right_drawer().classes('bg-white p-4'):
        right_drawer_frame = ui.column()
        refresh_right_drawer()

    # CENTER SCREEN
    with ui.row().classes('w-full p-4'):
        with ui.column().classes('w-2/3 p-4'):
            ui.label('Sales Screen').classes('text-2xl font-bold')

            ui.separator()

            # Winnings
            ui.label('Winnings')
            with ui.row().classes('flex-wrap'):
                for amount in [1, 2, 5, 10, 15, 20, 30, 100, 500]:
                    ui.button(f'${amount}', on_click=lambda a=amount: add_winning(a))

            ui.separator()

            # Lottery Tickets
            ui.label('Lottery Tickets')
            with ui.row().classes('flex-wrap'):
                for ticket in range(1, 109):
                    ui.button(f'{ticket}', on_click=lambda t=ticket: add_lottery(t))

            ui.separator()

            # Money Received
            ui.label('Money Received')
            with ui.row():
                for amount in [1, 5, 10, 20, 50, 100]:
                    ui.button(f'${amount}', on_click=lambda a=amount: add_money(a))

            with ui.row():
                ui.button('Exact Amount', on_click=pay_exact_amount, color='green')

            ui.separator()

            # Actions
            with ui.row():
                ui.button('Undo Last Selection', on_click=undo_last_selection)
                ui.button('Reset Session', on_click=reset_all)
                ui.button('Save Sale', on_click=save_sale, color='blue')

@ui.page('/tracker')
def ticket_tracker_page():
    with ui.column().classes('p-4'):
        ui.label('Ticket Book Tracker').classes('text-2xl font-bold')

        with ui.row().classes('flex-wrap'):
            for box_num in range(1, 109):
                tickets_left = ticket_books.get(box_num, 0)
                emoji = ""
                if tickets_left == 0:
                    emoji = "🔴"
                elif tickets_left <= 5:
                    emoji = "🟡"

                ui.button(f"Box {box_num}: {tickets_left} {emoji}")

# --- Run App ---
ui.run(title="Lottery POS System", port=8081, reload=True)
