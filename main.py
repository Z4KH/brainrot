"""
This file is the main file for the project.
It is used to run the project.
"""
import json

def main():
    # open categories.json and print the dictionary
    with open('categories.json', 'r') as f:
        categories = json.load(f)
        for category, data in categories.items():
            print(category)
            print(data)
            print("-"*100)

if __name__ == "__main__":
    main()
