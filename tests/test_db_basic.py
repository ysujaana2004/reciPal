"""Interactive CLI for testing recipe CRUD operations via FastAPI backend.

This is a command-line interface that allows you to:
- Login with your credentials
- Add dummy recipes to your account
- View all your recipes
- Delete recipes

Requires the FastAPI server to be running on http://localhost:8000
"""

import requests
from typing import Optional

BASE_URL = "http://localhost:8000"

# Dummy recipes to choose from
DUMMY_RECIPES = {
    1: {
        "title": "Classic Spaghetti Carbonara",
        "instructions": "Cook pasta. Fry bacon. Mix eggs and cheese. Combine everything hot.",
        "ingredients": ["spaghetti", "eggs", "bacon", "parmesan cheese", "black pepper"],
        "source_url": "https://example.com/carbonara"
    },
    2: {
        "title": "Chicken Stir Fry",
        "instructions": "Cut chicken. Heat wok. Stir fry with vegetables. Add sauce.",
        "ingredients": ["chicken breast", "soy sauce", "bell peppers", "broccoli", "garlic"],
        "source_url": "https://example.com/stirfry"
    },
    3: {
        "title": "Caesar Salad",
        "instructions": "Chop lettuce. Make dressing. Add croutons. Toss together.",
        "ingredients": ["romaine lettuce", "caesar dressing", "croutons", "parmesan", "lemon"],
        "source_url": "https://example.com/caesar"
    },
    4: {
        "title": "Margherita Pizza",
        "instructions": "Roll dough. Add sauce and cheese. Bake at 450F. Add basil.",
        "ingredients": ["pizza dough", "tomato sauce", "mozzarella", "fresh basil", "olive oil"],
        "source_url": "https://example.com/pizza"
    },
    5: {
        "title": "Beef Tacos",
        "instructions": "Brown beef. Add spices. Warm tortillas. Assemble with toppings.",
        "ingredients": ["ground beef", "taco seasoning", "tortillas", "lettuce", "cheese", "salsa"],
        "source_url": "https://example.com/tacos"
    },
    6: {
        "title": "Chocolate Chip Cookies",
        "instructions": "Mix butter and sugar. Add eggs. Mix dry ingredients. Fold in chips. Bake.",
        "ingredients": ["flour", "butter", "sugar", "eggs", "chocolate chips", "vanilla"],
        "source_url": "https://example.com/cookies"
    },
    7: {
        "title": "Greek Salad",
        "instructions": "Chop vegetables. Add olives and feta. Drizzle with olive oil.",
        "ingredients": ["tomatoes", "cucumber", "red onion", "feta cheese", "olives", "olive oil"],
        "source_url": "https://example.com/greek"
    },
    8: {
        "title": "Pancakes",
        "instructions": "Mix dry ingredients. Add wet ingredients. Cook on griddle. Serve warm.",
        "ingredients": ["flour", "milk", "eggs", "baking powder", "butter", "maple syrup"],
        "source_url": "https://example.com/pancakes"
    },
    9: {
        "title": "Tom Yum Soup",
        "instructions": "Boil broth. Add lemongrass and galangal. Add shrimp. Season with lime.",
        "ingredients": ["shrimp", "lemongrass", "galangal", "lime", "fish sauce", "chili"],
        "source_url": "https://example.com/tomyum"
    },
    10: {
        "title": "Avocado Toast",
        "instructions": "Toast bread. Mash avocado. Spread on toast. Season and top.",
        "ingredients": ["bread", "avocado", "salt", "pepper", "lemon juice", "red pepper flakes"],
        "source_url": "https://example.com/avocado"
    }
}


class RecipeClient:
    def __init__(self):
        self.access_token: Optional[str] = None
        self.user_email: Optional[str] = None

    def signup(self, email: str, password: str, username: str) -> bool:
        """Sign up a new user."""
        try:
            response = requests.post(
                f"{BASE_URL}/auth/signup",
                json={"email": email, "password": password, "username": username}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"\n✓ {data.get('message', 'Signup successful!')}")
                print(f"Username: {data.get('username', username)}")
                return True
            else:
                print(f"Signup failed: {response.json().get('detail', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return False

    def login(self, email: str, password: str) -> bool:
        """Login and store access token."""
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"email": email, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.user_email = email
                return True
            else:
                print(f"Login failed: {response.json().get('detail', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return False

    def get_headers(self) -> dict:
        """Get authorization headers."""
        if not self.access_token:
            raise Exception("Not logged in")
        return {"Authorization": f"Bearer {self.access_token}"}

    def add_recipe(self, recipe_data: dict) -> bool:
        """Add a recipe to the database."""
        try:
            response = requests.post(
                f"{BASE_URL}/recipes/",
                json=recipe_data,
                headers=self.get_headers()
            )
            if response.status_code == 200:
                recipe = response.json()
                print(f"\n✓ Recipe added successfully! ID: {recipe.get('id')}")
                return True
            else:
                print(f"Failed to add recipe: {response.json().get('detail', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False

    def list_recipes(self, ingredient: str = None) -> list:
        """Get all recipes for the logged-in user.
        
        Args:
            ingredient: Optional ingredient to filter by
        """
        try:
            url = f"{BASE_URL}/recipes/"
            if ingredient:
                url += f"?ingredient={ingredient}"
            
            response = requests.get(url, headers=self.get_headers())
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to fetch recipes: {response.json().get('detail', 'Unknown error')}")
                return []
        except Exception as e:
            print(f"Error: {e}")
            return []

    def delete_recipe(self, recipe_id: int) -> bool:
        """Delete a recipe by ID."""
        try:
            response = requests.delete(
                f"{BASE_URL}/recipes/{recipe_id}",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                print(f"\n✓ Recipe {recipe_id} deleted successfully!")
                return True
            else:
                print(f"Failed to delete recipe: {response.json().get('detail', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False

    # ==================== Pantry Methods ====================

    def add_pantry_item(self, ingredient_name: str, quantity: float, unit: str = "pieces") -> bool:
        """Add or update a pantry item."""
        try:
            response = requests.post(
                f"{BASE_URL}/pantry/",
                json={"ingredient_name": ingredient_name, "quantity": quantity, "unit": unit},
                headers=self.get_headers()
            )
            if response.status_code == 200:
                item = response.json()
                print(f"\n✓ Pantry item added/updated: {item.get('ingredient_name')} ({item.get('quantity')} {item.get('unit')})")
                return True
            else:
                print(f"Failed to add pantry item (Status {response.status_code}):")
                try:
                    print(f"  {response.json().get('detail', 'Unknown error')}")
                except:
                    print(f"  Response: {response.text[:200]}")
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False

    def list_pantry_items(self) -> list:
        """Get all pantry items."""
        try:
            response = requests.get(
                f"{BASE_URL}/pantry/",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to fetch pantry items (Status {response.status_code}):")
                try:
                    print(f"  {response.json().get('detail', 'Unknown error')}")
                except:
                    print(f"  Response: {response.text[:200]}")
                return []
        except Exception as e:
            print(f"Error: {e}")
            return []

    def update_pantry_item(self, item_id: int, quantity: float, unit: str = None) -> bool:
        """Update quantity of a pantry item."""
        try:
            payload = {"quantity": quantity}
            if unit:
                payload["unit"] = unit
            
            response = requests.put(
                f"{BASE_URL}/pantry/{item_id}",
                json=payload,
                headers=self.get_headers()
            )
            if response.status_code == 200:
                item = response.json()
                print(f"\n✓ Pantry item updated: {item.get('ingredient_name')} ({item.get('quantity')} {item.get('unit')})")
                return True
            else:
                print(f"Failed to update pantry item (Status {response.status_code}):")
                try:
                    print(f"  {response.json().get('detail', 'Unknown error')}")
                except:
                    print(f"  Response: {response.text[:200]}")
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False

    def delete_pantry_item(self, item_id: int) -> bool:
        """Delete a pantry item."""
        try:
            response = requests.delete(
                f"{BASE_URL}/pantry/{item_id}",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                print(f"\n✓ Pantry item deleted successfully!")
                return True
            else:
                print(f"Failed to delete pantry item (Status {response.status_code}):")
                try:
                    print(f"  {response.json().get('detail', 'Unknown error')}")
                except:
                    print(f"  Response: {response.text[:200]}")
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False

    def check_recipe_ingredients(self, recipe_id: int) -> dict:
        """Check if user can make a recipe based on pantry."""
        try:
            response = requests.get(
                f"{BASE_URL}/pantry/check/recipe/{recipe_id}",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to check recipe (Status {response.status_code}):")
                try:
                    print(f"  {response.json().get('detail', 'Unknown error')}")
                except:
                    print(f"  Response: {response.text[:200]}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def get_grocery_recommendations(self) -> list:
        """Get grocery recommendations based on pantry and recipes."""
        try:
            response = requests.get(
                f"{BASE_URL}/grocery/recommendations",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get recommendations (Status {response.status_code}):")
                try:
                    print(f"  {response.json().get('detail', 'Unknown error')}")
                except:
                    print(f"  Response: {response.text[:200]}")
                return []
        except Exception as e:
            print(f"Error: {e}")
            return []


def show_dummy_recipes():
    """Display available dummy recipes."""
    print("\n" + "="*60)
    print("Available Dummy Recipes:")
    print("="*60)
    for num, recipe in DUMMY_RECIPES.items():
        print(f"{num:2d}. {recipe['title']}")
    print("="*60)


def show_user_recipes(client: RecipeClient, ingredient: str = None):
    """Display all user's recipes, optionally filtered by ingredient."""
    recipes = client.list_recipes(ingredient=ingredient)
    
    if not recipes:
        if ingredient:
            print(f"\n📭 No recipes found with '{ingredient}'.")
        else:
            print("\n📭 You have no recipes yet.")
        return
    
    print("\n" + "="*60)
    if ingredient:
        print(f"Recipes containing '{ingredient}':")
    else:
        print("Your Recipes:")
    print("="*60)
    for recipe in recipes:
        print(f"ID: {recipe['id']:4d} | {recipe['title']}")
        print(f"           Ingredients: {', '.join(recipe.get('ingredients', []))}")
        print(f"           Source: {recipe.get('source_url', 'N/A')}")
        print("-" * 60)
    print(f"Total: {len(recipes)} recipe(s)")
    print("="*60)


def show_pantry_items(client: RecipeClient):
    """Display all pantry items."""
    items = client.list_pantry_items()
    
    if not items:
        print("\n📭 Your pantry is empty.")
        return
    
    print("\n" + "="*60)
    print("Your Pantry:")
    print("="*60)
    for item in items:
        print(f"ID: {item['id']:4d} | {item['ingredient_name']:20s} | {item['quantity']:6.1f} {item['unit']}")
    print("="*60)
    print(f"Total: {len(items)} item(s)")


def show_recipe_check_result(result: dict):
    """Display recipe ingredient check results."""
    if not result:
        return
    
    print("\n" + "="*60)
    print(f"Recipe: {result['recipe_title']}")
    print("="*60)
    
    if result['can_make']:
        print("✓ YOU CAN MAKE THIS RECIPE!")
    else:
        print(f"✗ Missing {result['need_count']}/{result['total_ingredients']} ingredients")
    
    print("\n--- AVAILABLE ({}) ---".format(result['have_count']))
    if result['available']:
        for item in result['available']:
            print(f"  ✓ {item['ingredient_name']:20s} ({item['quantity']} {item['unit']})")
    else:
        print("  (none)")
    
    print("\n--- MISSING ({}) ---".format(result['need_count']))
    if result['missing']:
        for ingredient in result['missing']:
            print(f"  ✗ {ingredient}")
    else:
        print("  (none)")
    
    print("="*60)


def show_grocery_recommendations(recommendations: list):
    """Display grocery recommendations."""
    if not recommendations:
        print("\n🎉 You have everything you need! No grocery recommendations.")
        return
    
    print("\n" + "="*60)
    print("🛒 Grocery Recommendations")
    print("="*60)
    print("Buy these ingredients to unlock more recipes:")
    print("-" * 60)
    
    for i, rec in enumerate(recommendations[:10], 1):  # Show top 10
        ingredient = rec['ingredient']
        unlocks = rec['unlocks']
        print(f"{i:2d}. {ingredient:25s} → unlocks {unlocks} recipe(s)")
    
    if len(recommendations) > 10:
        print(f"\n... and {len(recommendations) - 10} more")
    
    print("="*60)
    print(f"Total recommendations: {len(recommendations)}")


def main():
    """Main interactive CLI loop."""
    client = RecipeClient()
    
    print("\n" + "="*60)
    print("🍳 Recipe Manager - Interactive CLI")
    print("="*60)
    
    # Login or Signup
    while not client.access_token:
        print("\n1. Login")
        print("2. Sign Up")
        print("3. Exit")
        auth_choice = input("\nEnter your choice (1-3): ").strip()
        
        if auth_choice == "1":
            # Login
            print("\n--- Login ---")
            email = input("Email: ").strip()
            password = input("Password: ").strip()
            
            if client.login(email, password):
                print(f"\n✓ Logged in as {email}")
                break
            else:
                retry = input("\nTry again? (y/n): ").strip().lower()
                if retry != 'y':
                    continue
        
        elif auth_choice == "2":
            # Sign Up
            print("\n--- Sign Up ---")
            email = input("Email: ").strip()
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            confirm_password = input("Confirm Password: ").strip()
            
            if password != confirm_password:
                print("Passwords don't match!")
                continue
            
            if client.signup(email, password, username):
                # Auto-login after successful signup
                auto_login = input("\nWould you like to login now? (y/n): ").strip().lower()
                if auto_login == 'y':
                    if client.login(email, password):
                        print(f"\n✓ Logged in as {email}")
                        break
        
        elif auth_choice == "3":
            print("Goodbye!")
            return
        
        else:
            print("Invalid choice! Please enter 1-3.")
    
    # Main menu loop
    while True:
        print("\n" + "="*60)
        print("Main Menu:")
        print("="*60)
        print("RECIPES:")
        print("  1. Add a dummy recipe")
        print("  2. View all my recipes")
        print("  3. Search recipes by ingredient")
        print("  4. Delete a recipe")
        print("\nPANTRY:")
        print("  5. Add pantry item")
        print("  6. View my pantry")
        print("  7. Update pantry item")
        print("  8. Delete pantry item")
        print("\nCHECK:")
        print("  9. Check if I can make a recipe")
        print("\nGROCERY:")
        print(" 10. Get grocery recommendations")
        print("\n 11. Logout")
        print("="*60)
        
        choice = input("\nEnter your choice (1-11): ").strip()
        
        if choice == "1":
            # Add dummy recipe
            show_dummy_recipes()
            recipe_num = input("\nEnter recipe number (1-10) or 'c' to cancel: ").strip()
            
            if recipe_num.lower() == 'c':
                continue
            
            try:
                recipe_num = int(recipe_num)
                if recipe_num in DUMMY_RECIPES:
                    client.add_recipe(DUMMY_RECIPES[recipe_num])
                else:
                    print("Invalid recipe number!")
            except ValueError:
                print("Invalid input!")
        
        elif choice == "2":
            # View all recipes
            show_user_recipes(client)
        
        elif choice == "3":
            # Search recipes by ingredient
            ingredient = input("\nEnter ingredient to search for: ").strip()
            if ingredient:
                show_user_recipes(client, ingredient=ingredient)
        
        elif choice == "4":
            # Delete recipe
            show_user_recipes(client)
            if client.list_recipes():  # Only ask if there are recipes
                recipe_id = input("\nEnter recipe ID to delete or 'c' to cancel: ").strip()
                
                if recipe_id.lower() == 'c':
                    continue
                
                try:
                    recipe_id = int(recipe_id)
                    confirm = input(f"Are you sure you want to delete recipe {recipe_id}? (y/n): ").strip().lower()
                    if confirm == 'y':
                        client.delete_recipe(recipe_id)
                except ValueError:
                    print("Invalid recipe ID!")
        
        elif choice == "5":
            # Add pantry item
            print("\n--- Add Pantry Item ---")
            ingredient = input("Ingredient name: ").strip()
            try:
                quantity = float(input("Quantity: ").strip())
                unit = input("Unit (pieces/kg/cups/etc): ").strip() or "pieces"
                client.add_pantry_item(ingredient, quantity, unit)
            except ValueError:
                print("Invalid quantity!")
        
        elif choice == "6":
            # View pantry
            show_pantry_items(client)
        
        elif choice == "7":
            # Update pantry item
            show_pantry_items(client)
            if client.list_pantry_items():
                item_id = input("\nEnter item ID to update or 'c' to cancel: ").strip()
                
                if item_id.lower() == 'c':
                    continue
                
                try:
                    item_id = int(item_id)
                    quantity = float(input("New quantity: ").strip())
                    unit = input("New unit (leave empty to keep current): ").strip() or None
                    client.update_pantry_item(item_id, quantity, unit)
                except ValueError:
                    print("Invalid input!")
        
        elif choice == "8":
            # Delete pantry item
            show_pantry_items(client)
            if client.list_pantry_items():
                item_id = input("\nEnter item ID to delete or 'c' to cancel: ").strip()
                
                if item_id.lower() == 'c':
                    continue
                
                try:
                    item_id = int(item_id)
                    confirm = input(f"Are you sure you want to delete item {item_id}? (y/n): ").strip().lower()
                    if confirm == 'y':
                        client.delete_pantry_item(item_id)
                except ValueError:
                    print("Invalid item ID!")
        
        elif choice == "9":
            # Check recipe
            show_user_recipes(client)
            if client.list_recipes():
                recipe_id = input("\nEnter recipe ID to check or 'c' to cancel: ").strip()
                
                if recipe_id.lower() == 'c':
                    continue
                
                try:
                    recipe_id = int(recipe_id)
                    result = client.check_recipe_ingredients(recipe_id)
                    if result:
                        show_recipe_check_result(result)
                except ValueError:
                    print("Invalid recipe ID!")
        
        elif choice == "10":
            # Get grocery recommendations
            recommendations = client.get_grocery_recommendations()
            show_grocery_recommendations(recommendations)
        
        elif choice == "11":
            # Logout
            print(f"\nLogging out {client.user_email}...")
            print("Goodbye! 👋")
            break
        
        else:
            print("Invalid choice! Please enter 1-11.")


if __name__ == "__main__":
    main()
