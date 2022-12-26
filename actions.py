# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import sqlite3
import pandas as pd


def create_connection(db_file):
    """ create a database connection to the SQLite database specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

class ActionMenu(Action):
	def name(self):
		return 'action_menu'

	def run(self, dispatcher, tracker, domain):
		pizza = tracker.get_slot("pizza_type")
		if(pizza==None):
			conn = create_connection("pizzas.db")
			cur = conn.cursor()
			cur.execute("""SELECT title FROM pizzas """)
			rows = cur.fetchall()
			if len(list(rows)) < 1:
				dispatcher.utter_message("These are no available pizzas at the moment")
			else:
				pizzas = ""
				for i in rows:
					pizzas = pizzas + i[0] + ", "
				pizzas = pizzas[:-2]
				dispatcher.utter_message("The available pizzas are: " + pizzas)
		return[]

class ActionPrice(Action):
	def name(self):
		return 'action_price'

	def run(self, dispatcher, tracker, domain):
		pizza_type = tracker.get_slot("pizza_type")
		if(pizza_type!=None):
			pizza_type = pizza_type.lower()
		conn = create_connection("pizzas.db")
		cur = conn.cursor()
		cur.execute(f"""SELECT price FROM pizzas WHERE title='{pizza_type}'""")
		rows = cur.fetchall()
		if len(list(rows)) < 1:
			dispatcher.utter_message(f"The pizza '{pizza_type}' is not present in the menu")
		else:
			dispatcher.utter_message("The price of " + pizza_type + " is " + rows[0][0] + " euros")
		return[]

class ActionPizzaAvailability(Action):
	def name(self):
		return 'action_pizza_availability'

	def run(self, dispatcher, tracker, domain):
		pizza_type = tracker.get_slot("pizza_type")
		if(pizza_type!=None):
			pizza_type = pizza_type.lower()
		conn = create_connection("pizzas.db")
		cur = conn.cursor()
		cur.execute(f"""SELECT title FROM pizzas WHERE EXISTS (SELECT title FROM pizzas WHERE title='{pizza_type}')""")
		rows = cur.fetchall()
		if len(list(rows)) < 1:
			dispatcher.utter_message(f"The pizza '{pizza_type}' is not present in the menu")
		else:
			dispatcher.utter_message("Yes! The " + pizza_type + " pizza is available.")
		return[]

class ActionPizzaQuestionToppings(Action):
	def name(self):
		return 'action_pizza_question_toppings'

	def run(self, dispatcher, tracker, domain):
		topping = tracker.get_slot("toppings")
		conn = create_connection("pizzas.db")
		cur = conn.cursor()
		cur.execute("""SELECT * FROM pizzas """)
		rows = cur.fetchall()
		if len(list(rows)) < 1:
			dispatcher.utter_message("These are no available pizzas at the moment")
		else:
			pizzas = ""
			for pizza in rows:
				if(not pizza[2].__contains__(topping)):
					pizzas = pizzas + pizza[0] + ", "
			pizzas = pizzas[:-2]
			if(len(pizzas)!=0):
				dispatcher.utter_message("Our pizzas without " + topping + " are: " + pizzas)
			else:
				dispatcher.utter_message("There are no pizzas without " + topping + " in our menu")
		return[]

class ActionResponsePositive(Action):
	def name(self):
		return 'action_response_positive'

	def run(self, dispatcher, tracker, domain):
		try:
			bot_event = next(e for e in reversed(tracker.events) if e["event"] == "bot")
			if (bot_event['metadata']['utter_action'] == 'utter_slots_values'):
				# save order to database
				pizza_type = tracker.get_slot('pizza_type')
				pizza_size = tracker.get_slot('pizza_size')
				pizza_amount = tracker.get_slot('pizza_amount')
				
				conn = create_connection("orders.db")
				cur = conn.cursor()
				cur.execute("""
          			CREATE TABLE IF NOT EXISTS orders
          			([order_id] TEXT, [client_name] TEXT, [pizza_type] TEXT, [pizza_size] TEXT, [pizza_amount] INTEGER, [toppings] TEXT)
				""")
				cur.execute(f"""
					INSERT INTO orders (order_id, client_name, pizza_type, pizza_size, pizza_amount, toppings)
						VALUES
						('{tracker.sender_id}','Alberto','{pizza_type}', '{pizza_size}', '{pizza_amount}', '...')
				""")
				# cur.execute("""SELECT * FROM orders """)
				# df = pd.DataFrame(cur.fetchall(), columns=['order_id','client_name','pizza_type','pizza_size','pizza_amount','toppings'])
				# print (df)
				conn.commit()
				dispatcher.utter_message(response='utter_anything_else')
				return[SlotSet("pizza_type", None),SlotSet("pizza_size", None),SlotSet("pizza_amount", None)]
			else:
				dispatcher.utter_message("Sorry, can you repeat that?")
		except:
			dispatcher.utter_message("Sorry, can you repeat that?")
		return[]

class ActionChangeOrder(Action):
	def name(self):
		return 'action_change_order'

	def run(self, dispatcher, tracker, domain):
		pizza_size = tracker.get_slot("pizza_size")
		pizza_type = tracker.get_slot("pizza_type")
		pizza_amount = tracker.get_slot("pizza_amount")
		SlotSet("pizza_type", pizza_type)
		SlotSet("pizza_size", pizza_size)
		SlotSet("pizza_amount", pizza_amount)
		return[]

class ActionPizzaOrderAdd(Action):
	def name(self):
		return 'action_pizza_order_add'

	def run(self, dispatcher, tracker, domain):
		pizza_size = tracker.get_slot("pizza_size")
		pizza_type = tracker.get_slot("pizza_type")
		pizza_amount = tracker.get_slot("pizza_amount")
		if pizza_size is None:
			pizza_size = "standard"
		order_details =  str(pizza_amount + " "+pizza_type + " is of "+pizza_size )
		old_order = tracker.get_slot("total_order")
		return[SlotSet("total_order", [order_details]) if old_order is None else SlotSet("total_order", [old_order[0]+' and '+order_details])]

class ActionResetPizzaForm(Action):
	def name(self):
		return 'action_reset_pizza_form'

	def run(self, dispatcher, tracker, domain):

		return[SlotSet("pizza_type", None),SlotSet("pizza_size", None),SlotSet("pizza_amount", None)]

class ActionOrderNumber(Action):
	def name(self):
		return 'action_order_number'

	def run(self, dispatcher, tracker, domain):
		name_person = tracker.get_slot("client_name")
		number_person = tracker.get_slot("phone_number")
		order_number =  str(name_person + "_"+number_person)
		print(order_number)
		return[SlotSet("order_number", order_number)]


class ActionPizzaQuestions(Action):
	def name(self):
		return 'action_pizza_questions'

	def run(self, dispatcher, tracker, domain):
		return[]