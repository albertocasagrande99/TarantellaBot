# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.types import DomainDict
import sqlite3
import pandas as pd
import phonenumbers
from collections import Counter


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
			conn = create_connection("data_db/pizzas.db")
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
		conn = create_connection("data_db/pizzas.db")
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
		conn = create_connection("data_db/pizzas.db")
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
		conn = create_connection("data_db/pizzas.db")
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
		return[SlotSet("toppings", None)]

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
				client_name = tracker.get_slot('client_name')
				conn = create_connection("data_db/orders.db")
				cur = conn.cursor()
				cur.execute("""
          			CREATE TABLE IF NOT EXISTS orders
          			([order_id] TEXT, [client_name] TEXT, [pizza_type] TEXT, [pizza_size] TEXT, [pizza_amount] INTEGER)
				""")
				cur.execute(f"""
					INSERT INTO orders (order_id, client_name, pizza_type, pizza_size, pizza_amount)
						VALUES
						('{tracker.sender_id}','{client_name.lower()}','{pizza_type}', '{pizza_size}', '{pizza_amount}')
				""")
				# cur.execute("""SELECT * FROM orders """)
				# df = pd.DataFrame(cur.fetchall(), columns=['order_id','client_name','pizza_type','pizza_size','pizza_amount','toppings'])
				# print (df)
				conn.commit()
				dispatcher.utter_message(response='utter_anything_else')
				return[SlotSet("pizza_type", None),SlotSet("pizza_size", None),SlotSet("pizza_amount", None),SlotSet("toppings", None)]
			elif(bot_event['metadata']['utter_action'] == 'utter_anything_else'):
				#dispatcher.utter_message(response='pizza_order_form')
				print("The user wants something else")
			elif(bot_event['metadata']['utter_action'] == 'utter_order_delete'):
				conn = create_connection("data_db/orders.db")
				cur = conn.cursor()
				rows = cur.execute(f"""SELECT * FROM orders WHERE order_id='{tracker.sender_id}'""")
				if(len(list(rows))<1):
					dispatcher.utter_message("Your order is already empty.")
				else:
					cur.execute(f"""
						DELETE FROM orders
						WHERE order_id='{tracker.sender_id}'
					""")
					dispatcher.utter_message("Ok, I have deleted your order")
				conn.commit()
				return[SlotSet("pizza_type", None),SlotSet("pizza_size", None),SlotSet("pizza_amount", None),SlotSet("toppings", None)]
			elif(bot_event['metadata']['utter_action'] == 'utter_suggested_pizza'):
				print("The user wants the usual pizza")
			else:
				dispatcher.utter_message("Sorry, can you repeat that?")
		except:
			dispatcher.utter_message("Sorry, can you repeat that?")
		return[]

class ActionResponseNegative(Action):
	def name(self):
		return 'action_response_negative'

	def run(self, dispatcher, tracker, domain):
		try:
			bot_event = next(e for e in reversed(tracker.events) if e["event"] == "bot")
			if (bot_event['metadata']['utter_action'] == 'utter_slots_values'):
				dispatcher.utter_message(response='utter_order_confirm_negative')
				# return[SlotSet("pizza_type", None),SlotSet("pizza_size", None),SlotSet("pizza_amount", None),SlotSet("toppings", None)]
			elif(bot_event['metadata']['utter_action'] == 'utter_anything_else'):
				dispatcher.utter_message("Let me check your order. Please wait a moment... ")
				conn = create_connection("data_db/orders.db")
				cur = conn.cursor()
				cur.execute(f"""SELECT * FROM orders WHERE order_id='{tracker.sender_id}'""")
				rows = cur.fetchall()
				if len(list(rows)) < 1:
					dispatcher.utter_message("There are no orders with your name.")
				else:
					order = ""
					for i in rows:
						order = order + str(i[4]) + " " + i[3] + " " + i[2] + ", "	
					order = order[:-2]
					conn.commit()
					conn.close()

					#connection to db pizzas
					total_cost = 0
					conn = create_connection("data_db/pizzas.db")
					cur = conn.cursor()
					for pizza in rows:
						cur.execute(f"""SELECT price FROM pizzas WHERE title='{pizza[2]}'""")
						row = cur.fetchone()
						total_cost = total_cost + float(row[0])*int(pizza[4])
					conn.commit()
					conn.close()
					dispatcher.utter_message("Ok, your total order includes: " + order + ".")
					dispatcher.utter_message(response='utter_total_cost', cost=total_cost)
			elif(bot_event['metadata']['utter_action'] == 'utter_order_delete'):
				dispatcher.utter_message("Ok, I don't delete your order.")
			elif(bot_event['metadata']['utter_action'] == 'utter_suggested_pizza'):
				return[SlotSet("pizza_type", None)]
			else:
				dispatcher.utter_message("Sorry, can you repeat that?")
		except:
			dispatcher.utter_message("Sorry, can you repeat that?")
		return[]

class ValidateClientForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_client_form"

    def validate_client_name(
        self,
        slot_value: Any,
		dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate client name value."""
        conn = create_connection("data_db/users.db")
        cur = conn.cursor()
        cur.execute(f"""SELECT * FROM users WHERE client_name='{slot_value.lower()}'""")
        rows = cur.fetchall()
        if(len(list(rows))<1):
            dispatcher.utter_message(f"Welcome {slot_value}, seems you are a new client")
            return {"client_name": slot_value, "new_client": True}
        else:
            dispatcher.utter_message(f"Welcome back {slot_value}! How can I help you?")
            return {"client_name": slot_value, "phone_number": rows[0][1], "address_street": rows[0][2], "address_number": rows[0][3], "address_city": rows[0][4], "new_client": False}
	
    def validate_phone_number(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate client phone number value."""
        string_phone_number = slot_value
        phone_number = phonenumbers.parse(string_phone_number, "IT")
        if(phonenumbers.is_valid_number(phone_number)):
        	return {"phone_number": slot_value}
        else:
            dispatcher.utter_message("Not a valid number.")
            return {"phone_number": None}

    def validate_address_street(
        self,
        slot_value: Any,
		dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {}

    def validate_address_number(
        self,
        slot_value: Any,
		dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        string_address_number = slot_value
        if(string_address_number.isnumeric()):
            return {"address_number": slot_value}
        else:
            return {"address_number": None}

    def validate_address_city(
        self,
        slot_value: Any,
		dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {}

class ActionSaveClient(Action):
	def name(self):
		return 'action_save_client'

	def run(self, dispatcher, tracker, domain):
		try:
			conn = create_connection("data_db/users.db")
			cur = conn.cursor()
			cur.execute("""
				CREATE TABLE IF NOT EXISTS users
				([client_name] TEXT, [phone_number] INTEGER, [address_street] TEXT, [address_number] INTEGER, [address_city] TEXT)
			""")
			cur.execute(f"""
				SELECT * FROM users WHERE client_name='{tracker.get_slot("client_name").lower()}'
			""")
			rows = cur.fetchall()
			if(len(list(rows))<1):
				cur.execute(f"""
					INSERT INTO users (client_name, phone_number, address_street, address_number, address_city)
						VALUES
						('{tracker.get_slot("client_name").lower()}','{tracker.get_slot("phone_number")}', '{tracker.get_slot("address_street")}', '{tracker.get_slot("address_number")}', '{tracker.get_slot("address_city")}')
				""")
				dispatcher.utter_message(f"Perfect {tracker.get_slot('client_name')}. How can I help you?")
			conn.commit()
			conn.close()
		except:
			dispatcher.utter_message("Problem while saving the information")
		return[SlotSet("pizza_type", None),SlotSet("pizza_size", None),SlotSet("pizza_amount", None)]

class ActionSuggestPizza(Action):
	def name(self):
		return 'action_suggest_pizza'

	def run(self, dispatcher, tracker, domain):
		try:
			conn = create_connection("data_db/orders.db")
			cur = conn.cursor()
			cur.execute(f"""
				SELECT * FROM orders WHERE client_name='{tracker.get_slot("client_name").lower()}'
			""")
			rows = cur.fetchall()
			pizzas = []
			if(len(list(rows))>1):
				for pizza in rows:
					pizzas.append(pizza[2])
				occurence_count = Counter(pizzas)
				most_ordered_pizza = occurence_count.most_common(1)[0][0]
			conn.commit()
			conn.close()
			dispatcher.utter_message(response='utter_suggested_pizza', pizza=most_ordered_pizza)
			return[SlotSet("pizza_type", most_ordered_pizza)]
		except:
			dispatcher.utter_message("Problem")
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