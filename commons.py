from faker import Faker
from datetime import datetime
from random import randint


def get_random_word_or_sentence_faker(option):
    fake = Faker()
    curr_yr = datetime.now().year
    year = randint(1950, curr_yr)
    if option == 'word':
        return f"What is the meaning of {fake.word()}"
    elif option == 'name':
        return fake.name() 
    elif option == 'country':
        return f"What is the current US GDP in {fake.country()}?"
    elif option == 'movie':
        return f"List of movies released in {year}"
    elif option == 'music':
        return f"List of songs released in {year}"
    elif option == 'sports':
        return f"Match score of {fake.country()} vs {fake.country()}"
    elif option == 'technology':
        return f"Techonlogy trends in {year}"
    elif option == 'News':
        return f"Latest new of {fake.city()}"
    else:
        return "Invalid option. Use 'word' or 'sentence'"

