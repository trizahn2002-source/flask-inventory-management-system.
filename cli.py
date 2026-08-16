import requests

BASE_URL = "http://127.0.0.1:5001"


def safe_request(method, url, **kwargs):
    try:
        return method(url, **kwargs)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Is it running?")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def parse_float(prompt):
    value = input(prompt)
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        print("Invalid number, ignoring this field.")
        return None


def parse_int(prompt):
    value = input(prompt)
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        print("Invalid number, ignoring this field.")
        return None


def view_all_items():
    response = safe_request(requests.get, f"{BASE_URL}/inventory")
    if response is None:
        return

    items = response.json()
    for item in items:
        print(f"ID: {item['id']} | {item['name']} | {item['brand']} | ${item['price']} | Stock: {item['stock']}")


def view_item():
    item_id = input("Enter item ID: ")
    response = safe_request(requests.get, f"{BASE_URL}/inventory/{item_id}")
    if response is None:
        return

    if response.status_code == 200:
        print(response.json())
    else:
        print("Item not found.")


def add_item():
    name = input("Item name: ")
    brand = input("Brand: ")
    price = parse_float("Price: ") or 0
    stock = parse_int("Stock: ") or 0

    payload = {
        "name": name,
        "brand": brand,
        "price": price,
        "stock": stock,
    }
    response = safe_request(requests.post, f"{BASE_URL}/inventory", json=payload)
    if response is None:
        return
    print(response.json())


def update_item():
    item_id = input("Enter item ID to update: ")
    print("Leave blank to skip a field.")
    name = input("New name: ")
    price = parse_float("New price: ")
    stock = parse_int("New stock: ")

    payload = {}
    if name:
        payload["name"] = name
    if price is not None:
        payload["price"] = price
    if stock is not None:
        payload["stock"] = stock

    response = safe_request(requests.patch, f"{BASE_URL}/inventory/{item_id}", json=payload)
    if response is None:
        return
    print(response.json())


def delete_item():
    item_id = input("Enter item ID to delete: ")
    response = safe_request(requests.delete, f"{BASE_URL}/inventory/{item_id}")
    if response is None:
        return
    print(response.json())


def fetch_from_api():
    query = input("Enter product name to search on OpenFoodFacts: ")
    response = safe_request(requests.post, f"{BASE_URL}/inventory/fetch", json={"query": query})
    if response is None:
        return

    if response.status_code == 201:
        print("Added:", response.json())
    else:
        print("Error:", response.json())


def main():
    while True:
        print("\n--- Inventory CLI ---")
        print("1. View all items")
        print("2. View one item")
        print("3. Add item")
        print("4. Update item")
        print("5. Delete item")
        print("6. Fetch item from OpenFoodFacts")
        print("7. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            view_all_items()
        elif choice == "2":
            view_item()
        elif choice == "3":
            add_item()
        elif choice == "4":
            update_item()
        elif choice == "5":
            delete_item()
        elif choice == "6":
            fetch_from_api()
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    main()