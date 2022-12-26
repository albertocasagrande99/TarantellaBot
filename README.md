# Tarantellabot :robot:

### About
A conversational assistant that helps in:
- ordering a pizza :pizza:
- reserving a table :plate_with_cutlery:

This chatbot was built using [Rasa](https://rasa.com/docs/getting-started/).

### Getting Started
> install first [Rasa](https://rasa.com/docs/rasa/user-guide/installation/#installation)


### Train the chatbot
```
rasa train
```

### Test chatbot
```
rasa test
```

### Talk to chatbot
```
rasa shell
```
In case it doesn't predict any response please use specifying the model folder:
```commandline
rasa shell -m models/
```
