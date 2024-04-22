import json
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User
from serpapi import GoogleSearch
import webbrowser

def welcome(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'New user':
            return render(request, 'myapp/newuser.html')

        elif action == 'Returning user':
            return render(request, 'myapp/oldUser.html')

        elif action == 'Quit':
            return HttpResponse("Thank you for using Brewmate. Goodbye!")  # Simple response for quitting

    # GET request or no valid POST action
    return render(request, 'myapp/welcome.html')


# Create your views here.
def newuser(request):
    if request.method == 'POST':
        # Extract data from POST request
        name = request.POST.get('name')
        password = request.POST.get('password')
        milkType = request.POST.get('milkType')
        recipes = []

        # Create a dictionary of the user data
        user_data = {
            'name': name,
            'password': password,
            'milkType': milkType,
            'recipes': recipes,
        }

        if User.objects.filter(name=name):
            return render(request, 'myapp/newuser.html', {'message': 'Please enter a unique username.'})
        
        newUser = User(name=name, password=password, milkType=milkType, recipes=recipes)
        newUser.save()

        user = User.objects.get(name=name, password=password)
        request.session['name'] = user.name
        request.session['password'] = user.password
    
        return render(request, 'myapp/userMenu.html', {'user': newUser, 'new_user': True})
    return render(request, 'myapp/newuser.html')

def olduser(request):
    if request.method == 'POST':
        # Extract data from POST request
        name = request.POST.get('name')
        password = request.POST.get('password')

        userExists = User.objects.filter(name=name, password=password)
        if not userExists:
            return render(request, 'myapp/oldUser.html', {'message': 'Incorrect username or password'})
        else:
            user = User.objects.get(name=name, password=password)
            request.session['name'] = user.name
            request.session['password'] = user.password
            return render(request, 'myapp/userMenu.html', {'user': user, 'new_user': False})
    return render(request, 'myapp/oldUser.html')

def usermenu(request):
    userName = request.session.get('name')
    password = request.session.get('password')
    user = User.objects.get(name=userName, password=password)
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'Change milk preference':
            return render(request, 'myapp/changePreferences.html')  # need to implement template

        elif action == 'Search recipes':
            params = {
                'temperature': ["hot", "iced"],
                'drink': ["drip coffee", "cold brew", "hot chocolate", "espresso", "americano", "cappuccino", 
                                "latte", "macchiato", "mocha", "flat white", "cortado", "affogato", "red eye",
                                "black eye", "long black", "doppio", "breve", "vienna", "chai", "matcha", "french press"],
                'syrup': ["none", "vanilla", "brown sugar cinanmon", "toasted marshmallow", "white chocolate", "salted caramel", 
                            "caramel", "butter pecan", "hazelnut", "french vanilla", "pepperint", "lavendar", "pumpkin spice"],
                'topping': ["none", "caramel", "chocolate", "whipped cream", "pepermint", "mocha syrup", "white mocha syrup"],
            }
            return render(request, 'myapp/searchRecipes.html', params)      # need to implement template

        elif action == 'Get saved recipes':
            return render(request, 'myapp/showRecipes.html', {'recipes': user.recipes})        # need to implement template
        
        elif action == 'Quit':
            return render(request, 'myapp/welcome.html')

    # GET request or no valid POST action
    return render(request, 'myapp/usermenu.html', {'user': user})

def changePreferences(request):
    userName = request.session.get('name')
    password = request.session.get('password')
    user = User.objects.get(name=userName, password=password)

    if request.method == 'POST':
        newMilk = request.POST.get('milkType')
        user.milkType = newMilk  # Update the user's milk type
        user.save()  # Save changes immediately
        return render(request, 'myapp/userMenu.html', {'user': user})
    return render(request, 'myapp/changePreferences.html')

"""def showRecipes(request):
    userName = request.session.get('name')
    password = request.session.get('password')
    user = User.objects.get(name=userName, password=password)
    recipes = user.recipes

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'Open a recipe':
            pass
        elif action == 'Delete a recipe':
            pass
        elif action == 'Return to main menu':
            return render(request, 'myapp/userMenu.html', {'user': user})
    return render(request, 'myapp/showRecipes.html', {'recipes': recipes})"""

def delete_recipe(request):
    userName = request.session.get('name')
    password = request.session.get('password')
    user = User.objects.get(name=userName, password=password)

    if request.method == 'POST':
        recipe_title = request.POST.get('recipe_title')
        updated_recipes = [recipe for recipe in user.recipes if recipe['title'] != recipe_title]
        user.recipes = updated_recipes
        user.save()  # Save the updated list to the user
        return render(request, 'myapp/showRecipes.html', {'recipes': user.recipes})
    
def open_recipe(request):
    userName = request.session.get('name')
    password = request.session.get('password')
    user = User.objects.get(name=userName, password=password)

    recipe_title = request.GET.get('recipe_title')
    recipe = [recipe for recipe in user.recipes if recipe['title'] == recipe_title][0]
    webbrowser.open(recipe['link'], new=1)
    # Assuming you have a template to display the recipe
    return render(request, 'myapp/showRecipes.html', {'recipes': user.recipes})

def searchRecipes(request):
    userName = request.session.get('name')
    password = request.session.get('password')
    user = User.objects.get(name=userName, password=password)

    if request.method == 'POST':
        items = [request.POST.get('temperature'), request.POST.get('drink'), request.POST.get('syrup'), request.POST.get('topping')]
        query = user.milkType + " milk"
        for item in items:
            if item != 'none':
                query += " " + item
        query += " recipe"
        temperature = request.POST.get('temperature')

        searchParams = {
            "api_key": "",
            "engine": "google",
            "q": query,
            "location": "Berkeley, California, United States",
            "google_domain": "google.com",
            "gl": "us",
            "hl": "en"
        }

        search = GoogleSearch(searchParams)
        results = search.get_dict()["organic_results"]
        # results = [{"title": "hey", "source": "me", "link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}]
        request.session['recipes'] = results
        return redirect('tinder')

    return render(request, 'myapp/searchRecipes.html')

def tinder(request):
    userName = request.session.get('name')
    password = request.session.get('password')
    user = User.objects.get(name=userName, password=password)

    if "current_index" not in request.session:
        request.session['current_index'] = 0
        request.session['saved_recipes'] = []

    results = request.session.get('recipes', [])
    current_index = request.session['current_index']

    if request.method == 'POST':
        if 'save' in request.POST:
            # Save the current recipe to the session's saved list
            request.session['saved_recipes'].append(results[current_index])
            request.session.modified = True

        if 'next' in request.POST or 'save' in request.POST:
            # Move to the next recipe
            if current_index + 1 < len(results):
                request.session['current_index'] += 1
            else:
                # Reset for safety
                request.session['current_index'] = 0
                return render(request, 'myapp/no_more_recipes.html')

        if 'return' in request.POST:
            # Optional: Save the session's saved recipes to user's database here
            # Reset session related to recipes
            for recipe in request.session.get('saved_recipes', []):
                if not (recipe in user.recipes):
                    user.recipes.append(recipe)
            user.save()

            del request.session['current_index']
            del request.session['saved_recipes']
            return render(request, 'myapp/userMenu.html', {'user': user})

    # Get the current recipe to display
    current_recipe = results[request.session['current_index']]
    return render(request, 'myapp/tinder.html', {'recipe': current_recipe})
