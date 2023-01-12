# Tarantellabot :robot:

### About :man_technologist:
The 'TarantellaBot' project aims to create a conversational agent that is able to manage the table reservations of a pizzeria and at the same time allow customers who use the service to order pizzas. Starting from this assumption, our system is a **multitask-based model** since it assists users with completing the aforementioned tasks. The conversational agent is designed to understand the user, request additional input from a user if necessary and complete the tasks successfully in a minimum number of turns.

As mentioned before, the system is able to handle two tasks:
- ordering a pizza :pizza:
- reserving a table :plate_with_cutlery:

The first task consists of ordering a pizza by specifying the pizza type, the size and the amount. In addition, for the clients that have already ordered a pizza with the system in the past, the system will automatically recommend the most frequently ordered pizza. Moreover, the user can request information about the menu at any time. Finally, once the pizzas have been ordered, the user can specify the delivery and payment method.
The table reservation task instead, allows the user to reserve a table by specifying the day, the time slot and the number of people. The user can choose between two time slots (7 p.m. and 9 p.m.), and in case there are no tables available in the indicated time slot, the system notifies the user and proposes the other slot if available. As in pizza ordering task, also in this case the system suggests a specific table for those clients that have already booked a table before. 

The system is able to answer some general questions from users. In particular, the user can request information regarding the menu. Among these, the available pizzas ("What are the pizzas in today's menu?"), the available sizes ("What are the available sizes?"), the toppings, the price of a certain pizza ("How much is the vegetarian pizza?") and the pizzas without a specific topping ("Do you have pizza with no mushrooms?"). And of course, the user can start ordering a pizza either by directly specifying what he wants ("I would like to order three american pizzas") or by making a general request ("I want to order a pizza"). 
The answers relating to the user's questions are dynamically generated starting from queries to the knowledge base (database) which thus allow to adapt to changes in the menu and prices. 
Most of the responses of the system are questions, which serve to acquire the information necessary in order to complete the tasks successfully.

### Repo structure :card_index_dividers:
In the `data/` folder we can find the data used for training and testing the model (nlu data and stories). The `data_db/` folder contains the sqlite databases queried by the custom actions in order to store and retrieve domain information.
The `Evaluation/` folder consists of both the evaluation of the dialogue model and the NLU.
This chatbot was built using [Rasa](https://rasa.com/docs/getting-started/).

### Getting Started :white_check_mark:
> install first [Rasa](https://rasa.com/docs/rasa/installation/environment-set-up)

### Train the chatbot :runner:
```
rasa train --config config.yml
```
It is possible to try out three different NLU pipelines, by specifying the configuration file in the training command.
- Config 1: DIET classifier for both intent classification and entity recognition.
- Config 2: DIETClassifier for intent classification and CRFEntityExtractor for entity recognition.
- Config 3: SklearnIntentClassifier for intent classification and the CRFEntityExtractor for entity recognition.

### Test chatbot :mag:
#### Natural Language Understanding Model
The following command can be used to test and compare different NLU pipelines:
```
rasa test nlu --nlu data/nlu.yml --config config.yml config_2.yml config3.yml
```
#### Dialogue model
You can evaluate the trained dialogue model on a set of test stories by using the test script, where the test stories are located under `data/nlu/`:
```
rasa test core --stories data/nlu/test_stories.yml --out results
```

### Talk to chatbot :speaking_head:
```
rasa shell
```
---
### Authors :man_student: :man_student:
- Alberto Casagrande
- Alessio Belli

*University of Trento*
