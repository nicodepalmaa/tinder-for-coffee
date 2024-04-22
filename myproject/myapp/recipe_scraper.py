import json
from serpapi import GoogleSearch
import webbrowser


def queryName():
    while True:
        userName = str(input("\nPlease enter your name: "))
        if userName.isalpha():
            break
        else:
            print("\nInvalid input. Please use only letters.")
    return userName

def queryMilk():
    milkTypes = ["Cow", "Oat", "Soy", "Almond", "Rice", "Coconut", "Cashew"]
    print("\nSelect milk preference from the following")
    for i, milk in enumerate(milkTypes, start=1):
        print(f"{i}.", milk)
    while True:
        try:
            milkChoice = int(input("\nType: ")) - 1
            if validSelection(milkChoice, milkTypes):
                break
            else:
                print("\nInvalid choice. Please try again.\n")
        except ValueError:
            print("\nInvalid choice. Please try again.")
    return milkTypes[milkChoice]

def validSelection(input, options: list): # input should be 0-indexed

    if input >= 0 and input < len(options) and type(input) == int:
        return True
    else:
        return False

def welcome():
    def welcomeScreen():
        welcomeOptions = ["New user", "Returning user", "Quit"]
        print("Welcome to Brewmate! What would you like to do today?")
        for i, action in enumerate(welcomeOptions, start=1):
            print(f"{i}.", action)
        while True:
            actionChoice = int(input("\nAction: ")) - 1
            if validSelection(actionChoice, welcomeOptions):
                break
            else:
                print("\nInvalid choice. Please try again.")
        return welcomeOptions[actionChoice]
    
    while True:
        welcomeAction = welcomeScreen()
        if welcomeAction == "New user":
            user = User()
            save_user_to_json(user)
            return user
        elif welcomeAction == "Returning user":
            userName = queryName()
            try:
                user = load_user_from_json(userName)
                print(f"\nWelcome back, {user.name}! In case you forgot, your milk type is {user.milkType}.")
                return user
            except FileNotFoundError:
                print(f"\nNo existing user data found for user: {userName}\n")
        else: # welcomeAction == "Quit"
            exit()

def save_user_to_json(user) -> None:
    """ Save a User object to a JSON file. """
    filename = user.name + "_data.json"
    with open(filename, 'w') as file:
        json.dump(user.to_dict(), file, indent=4)

def load_user_from_json(name: str):
    """ Load a User object from a JSON file. """
    filename = name + "_data.json"
    with open(filename, 'r') as file:
        data = json.load(file)
        return User.from_dict(data)
    
def open_url(url):
    # Attempt to open the URL in the default web browser
    try:
        webbrowser.open(url, new=1)
        print("\nBrowser launched successfully.")
    except Exception as e:
        print(f"\nFailed to open URL. Error: {e}")


class User():
    def __init__(self) -> None:
        self.name = queryName()
        self.milkType = queryMilk()
        self.recipes = []
        print(f"\nSuccessfully created new user! Welcome, {self.name}. Your milk type is: {self.milkType}.")

    def to_dict(self) -> dict:
        """ Convert the User object to a dictionary. """
        return {
            'name': self.name,
            'milkType': self.milkType,
            'recipes': self.recipes
        }
    
    @classmethod
    def from_dict(cls, data):
        """ Create a User instance from a dictionary. """
        user = cls.__new__(cls)  # Create an instance without calling __init__
        user.name = data['name']
        user.milkType = data['milkType']
        user.recipes = data.get('recipes', [])
        return user

    def queryAction(self) -> str:
        actionOptions = ["Change milk preference", "Search recipes", "Get saved recipes", "Quit"]
        print("\nWhat would you like to do today?")
        for i, action in enumerate(actionOptions, start=1):
            print(f"{i}.", action)
        while True:
            try:
                actionChoice = int(input("\nAction: ")) - 1
                if validSelection(actionChoice, actionOptions):
                    break
                else:
                    print("\nInvalid choice. Please try again.")
            except ValueError:
                print("\nInvalid choice. Please try again.")
        return actionOptions[actionChoice]
    
    def showRecipes(self):
        if len(self.recipes) <= 0:
            print("\nYou have no saved recipes! Use the 'Search recipes' option from the main menu to browse and save recipes.")
            return
        else:
            print("\nYour saved recipes: ")
            for i, recipe in enumerate(self.recipes, start=1):
                print(f"{i}. From {recipe["source"]}:", recipe["title"])
        
        recipeOptions = ["Open a recipe", "Delete a recipe", "Return to main menu", "Quit"]
        print("\nWhat would you like to do?")
        for i, choice in enumerate(recipeOptions, start=1):
            print(f"{i}.", choice)
        while True:
            try:
                recipeOptionChioce = int(input("\nChoice: ")) - 1
                if validSelection(recipeOptionChioce, recipeOptions):
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("\nInvalid choice. Please try again.")
        if recipeOptions[recipeOptionChioce] == "Open a recipe" or recipeOptions[recipeOptionChioce] == "Delete a recipe":
            print("")
            tempRecipes = self.recipes.copy()
            tempRecipes.append({"title": "Cancel"})
            for i, recipe in enumerate(tempRecipes, start=1):
                print(f"{i}. {recipe["title"]}")
            while True:
                try:
                    requestedRecipe = int(input("\nPlease select a recipe: ")) - 1
                    if validSelection(requestedRecipe, tempRecipes):
                        break
                    else:
                        print("\nInvalid choice. Please try again.")
                except ValueError:
                    print("\nInvalid choice. Please try again.")
            if tempRecipes[requestedRecipe]["title"] != "Cancel":
                if recipeOptions[recipeOptionChioce] == "Open a recipe":
                    open_url(self.recipes[requestedRecipe]["link"])
                else: # recipeOptions[recipeOptionChioce] == "Delete a recipe"
                    self.recipes.pop(requestedRecipe)
                    print("\nNew recipes list: ")
                    for i, recipe in enumerate(self.recipes, start=1):
                        print(f"{i}.", recipe["title"])
        elif recipeOptions[recipeOptionChioce] == "Return to main menu":
            return
        else: # action == "Quit"
            save_user_to_json(self)
            exit()
    
    def searchRecipes(self):
        params = {
        "api_key": "",
        "engine": "google",
        "q": self.queryParams(),
        "location": "Berkeley, California, United States",
        "google_domain": "google.com",
        "gl": "us",
        "hl": "en"
        }

        try:
            filename = params["q"] + ".json"
            with open(filename, 'r') as file:
                results = json.load(file)
        except FileNotFoundError:
            search = GoogleSearch(params)
            results = search.get_dict()["organic_results"]

            filename = params["q"] + ".json"
            with open(filename, 'w') as file:
                json.dump(results, file, indent=4)

        while True:
            for recipe in results:
                if recipe in self.recipes:
                    pass
                else:
                    actionOptions = ["Smash recipe", "Pass Recipe", "Return to main menu"]
                    print(f"\nFrom {recipe["source"]}: {recipe["title"]}")
                    for i, option in enumerate(actionOptions, start=1):
                        print(f"{i}.", option)
                    while True:
                        try:
                            choice = int(input("\nChoice: ")) - 1
                            if validSelection(choice, actionOptions):
                                break
                            else:
                                print("\nInvalid choice. Please try again.\n")
                        except ValueError:
                            print("\nInvalid choice. Please try again.")
                    if actionOptions[choice] == "Smash recipe":
                        self.recipes.append(recipe)
                    elif actionOptions[choice] == "Pass Recipe":
                        pass
                    else: # actionOptions[choice] == "Exit"
                        break
            print("\nNo more recipes! Please alter search options and try again.")
            break

    def queryParams(self):
        query = self.milkType + " milk "

        tempTypes = ["hot", "iced"]
        drinkTypes = ["drip coffee", "cold brew", "hot chocolate", "espresso", "americano", "cappuccino", 
                      "latte", "macchiato", "mocha", "flat white", "cortado", "affogato", "red eye",
                      "black eye", "long black", "doppio", "breve", "vienna", "chai", "matcha", "french press"]
        syrup = ["none", "vanilla", "brown sugar cinanmon", "toasted marshmallow", "white chocolate", "salted caramel", 
                 "caramel", "butter pecan", "hazelnut", "french vanilla", "pepperint", "lavendar", "pumpkin spice"]
        toppings = ["none", "caramel", "chocolate", "whipped cream", "pepermint", "mocha syrup", "white mocha syrup"]
        queryOptions = {"temperature": tempTypes, "drink option": drinkTypes, "flavoring": syrup, "toppings": toppings}

        for option in queryOptions:
            print(f"\nSelect coffee {option} from the following")
            for i, selection in enumerate(queryOptions[option], start=1):
                print(f"{i}.", selection)
            while True:
                try:
                    choice = int(input("\nChoice: ")) - 1
                    if validSelection(choice, queryOptions[option]):
                        break
                    else:
                        print("\nInvalid choice. Please try again.\n")
                except ValueError:
                    print("\nInvalid choice. Please try again.")
            if queryOptions[option][choice] != "none":
                query += queryOptions[option][choice] + " "
        return query + "recipe"


def main() -> None:
    user = welcome()
    while True:
        action = user.queryAction()
        if action == "Change milk preference":
            user.milkType = queryMilk()
            print(f"\nYour new milk preference is: {user.milkType}")
        elif action == "Search recipes":
            user.searchRecipes()
        elif action == "Get saved recipes":
            # user.recipes.append({"title": "iced latte", "link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
            user.showRecipes()
        else: # action == "Quit"
            save_user_to_json(user)
            exit()



main()
