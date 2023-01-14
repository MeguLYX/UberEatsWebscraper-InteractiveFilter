# UBEREATS WEBSCRAPER + INTERACTIVE FILTER 

# Importing Required Libraries 
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.error import HTTPError

import ssl

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'} # set the headers
ssl._create_default_https_context = ssl._create_unverified_context

# Creating Classes 
# Restaurant class
class Restaurant:
     def __init__(self, restaurant_name: str, rating: str, cuisine: list):
          self.name = restaurant_name
          self.rating = rating 
          self.cuisine = cuisine
     
     def __repr__(self):
          return self.name

# Category class, to implement
class Category:
     def __init__(self, category_name, category_group):
          self.name = category_name
          self.group = category_group


# Global variables/constants we need in other functions
# The way city and state are gathered and validated makes it hard to call without global variables
CITY = ""
STATE = ""
# US States dictionary that has full state names as keys, two-word abbreviations for values
us_states = {
          "alabama": "AL",
          "alaska": "AK",
          "arizona": "AZ",
          "arkansas": "AR",
          "california": "CA",
          "colorado": "CO",
          "connecticut": "CT",
          "delaware": "DE",
          "florida": "FL",
          "georgia": "GA",
          "hawaii": "HI",
          "idaho": "ID",
          "illinois": "IL",
          "indiana": "IN",
          "iowa": "IA",
          "kansas": "KS",
          "kentucky": "KY",
          "louisiana": "LA",
          "maine": "ME",
          "maryland": "MD",
          "massachusetts": "MA",
          "michigan": "MI",
          "minnesota": "MN",
          "mississippi": "MS",
          "missouri": "MO",
          "montana": "MT",
          "nebraska": "NE",
          "nevada": "NV",
          "new hampshire": "NH",
          "new jersey": "NJ",
          "new mexico": "NM",
          "new york": "NY",
          "north carolina": "NC",
          "north dakota": "ND",
          "ohio": "OH",
          "oklahoma": "OK",
          "oregon": "OR",
          "pennsylvania": "PA",
          "rhode island": "RI",
          "south carolina": "SC",
          "south dakota": "SD",
          "tennessee": "TN",
          "texas": "TX",
          "utah": "UT",
          "vermont": "VT",
          "virginia": "VA",
          "washington": "WA",
          "west virginia": "WV",
          "wisconsin": "WI",
          "wyoming": "WY",
          "district of columbia": "DC",
          "american samoa": "AS",
          "guam": "GU",
          "northern mariana islands": "MP",
          "puerto rico": "PR",
          }
     

def validate_state(state):
     """sig: string -> Boolean(T/F)
     takes the user input and returns T/F based on the dictionary given"""
     global us_states
     # Conditiional statements to determine whether the state input is valid
     if state.upper() in us_states.values(): # Checks whether the state abbreviation (ex. CT) is part of the dictionary
          return True
     elif state.lower() in us_states.keys(): # Checks whether the full state name (ex. Puerto Rico) is part of the dictionary
          return True
     return False # Otherwise, it is not valid as it does not match the dictionary


def get_city_and_state():
     """sig: input(string) -> string
     takes user input and returns the user input if True"""
     # Determining which city and state the user is in 
     city = input("Please enter the name of a city: ").replace(" ", "-")
     state = input("Enter the abbreviation/name of your state: ")
     
     # Check whether the state inputted is valid by calling validate_state
     while not validate_state(state):
          state = input("Please enter a valid US State: ")
     
     if len(state) > 2:
          state = us_states[state.lower()]

     return city, state



def scrape_ubereats():
     """sig: url -> html webpage
     sends a request to the website for webscraping"""
     global CITY, STATE
     while True:
          # Determining which city and state the user is in 
          city, state = get_city_and_state()

          # Creating the URL using the user's info  
          url = "https://www.ubereats.com/city/" + city.lower() + "-" + state.lower()
          # Sending a request to the page 
          req = Request(url, headers={'User-Agent' : 'Mozilla/5.0'})
          # Getting contents of the webpage 
          try:
               webpage = urlopen(req).read()

               # Overwrite our global variables to use in other functions
               CITY = city
               STATE = state

               # Exit the function
               return webpage
          except HTTPError:
               print("You might've entered some info wrongly! Please check again!")


# By using Inspect Element, we can see that UberEats uses <h3> tag to identify restaurant names
# Therefore, we can use the <h3> tag to get all the restaurants available
def populate_restaurants(webpage):
     """sig: html -> list
     scrapes the website for information and returns a list"""
     # use BeautifulSoup to parse the webpage
     soup = BeautifulSoup(webpage, 'html.parser')
     # Instantiate list of restaurants from Ubereats
     restaurant_list = []
     # Loop through all the restaurants on the page
     for x in soup.findAll("h3")[:80]: 
          # Create list of categories that a restaurant falls under
          cuisine = []

          restaurant_name = x.get_text()
          rating = soup.find("div", text = restaurant_name).findNext("div").text # Gets the rating of the restaurant by navigating to the next div
          if rating == restaurant_name: # If there is no rating, findNext will find the element it was called on
               rating = "No"
          if rating == "": # No text on element
               rating = "Top" #Top eats medal

          for child in x.parent.parent.find("span").parent: 
               content = child.text.replace('\xa0•\xa0',"") # Replace the category seperators with nothing, so we can easily skip it
               if content == "": 
                    continue # Skip empty text
               cuisine.append(content)

          restaurant_list.append(Restaurant(restaurant_name, rating, cuisine)) # Append a Restaurant object to our list
          
     return restaurant_list


def compile_all_categories(restaurant_list):
     """sig: list -> list
     compiles information of cuisines into a list"""
     categories = []
     for restaurant in restaurant_list:
          for cuisine in restaurant.cuisine:
               categories.append(cuisine)
     
     # Remove duplicates
     categories = list(set(categories))
     return categories


# Creating options for the user to choose from 
def options_text(categories):
     """sig: string -> string
     creates options for user to select"""
     print("What categories would you like to search for?")
     num_of_categories = len(categories)
     for i in range(num_of_categories):
          print(f"\t{i+1}. {categories[i]}")

     print("\td. Display all restaurants")
     print("\ts. Search restaurants")
     print("\tr. Reset search criteria")
     print("\tq. Exit")
     

# Validates the user's choice 
def validate_choice(choice, categories):
     """sig: string -> boolean (T/F)
     takes user input and returns T/F"""
     num_of_categories = len(categories)
     special_choices = ['d','s','r','q']

     if choice.lower() in special_choices: return True

     if not choice.isdigit(): return False
     if int(choice) < 1: return False
     if int(choice) > num_of_categories: return False

     return True
          


def get_search_input(categories, restaurants):
     """sig: str -> str
     takes user's search input and adds them to a list of choices"""
     selected_options = []

     while True:
          options_text(categories)
          print("Choose your options from above by typing the number or letter")
          display_selected_options = str(selected_options)[1:-1].replace("'", "")
          print("Currently selected options: " + display_selected_options)

          user_choice = input("Select your input: ")
          while not validate_choice(user_choice, categories):
               user_choice = input("Select your valid input: ")

          if user_choice.lower() == "d":
               print_restaurants(restaurants)
               input("Press enter to continue...")
          elif user_choice.lower() == "s":
               filtered_restaurants = search(selected_options, restaurants)
               print_restaurants(filtered_restaurants)
               input("Press enter to continue...")
          elif user_choice.lower() == "r":
               selected_options = []
               print("Search options reset!")
               input("Press enter to continue...")
          elif user_choice.lower() == "q":
               print("See you soon!")
               break
          else:
               selected_options.append(categories[int(user_choice) - 1])


def search(options, restaurants):
     """sig: str -> list
     takes the validated user input and returns a list of restaurants"""
     search_criteria = set(options)
     valid_restaurants = []
     for restaurant in restaurants:
          set_of_categories = set(restaurant.cuisine)
          if search_criteria.issubset(set_of_categories):
               valid_restaurants.append(restaurant)

     return valid_restaurants



# Print out all the restaurants we have scraped
def print_restaurants(restaurant_list):
     """str -> str or list
     returns a string or list depending on the user's search criteria"""
     global CITY, STATE
     print(f"Restaurants in {CITY.title()} {STATE.upper()}")
     if restaurant_list:
          for restaurant in restaurant_list:
               display_categories = str(restaurant.cuisine)[1:-1].replace("'", "")
               print(f"{restaurant.name}: {restaurant.rating} rating | {display_categories}")
     else:
          print("No restaurants match your search criteria.")


# Main is a function that runs all the other functions 
def main():
     """runs all the functions under a single function call"""
     webpage = scrape_ubereats()
     restaurants = populate_restaurants(webpage)
     categories = compile_all_categories(restaurants)
     get_search_input(categories, restaurants)



main()