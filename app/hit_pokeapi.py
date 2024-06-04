import requests
import csv

def fetch_ability_details(ability_id):
    url = f"https://pokeapi.co/api/v2/ability/{ability_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def save_to_csv(abilities, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'pokemon_ability_id', 'effect', 'language', 'short_effect']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for ability in abilities:
            writer.writerow(ability)

def main():
    abilities = []
    for i in range(1, 1000):
        ability_data = fetch_ability_details(i)
        if ability_data:
            effect_entries = ability_data.get('effect_entries', [])
            if effect_entries:
                abilities.append({
                    'id': i,
                    'pokemon_ability_id': ability_data['id'],
                    'effect': effect_entries[0].get('effect', ''),
                    'language': effect_entries[0].get('language', {}).get('name', ''),
                    'short_effect': effect_entries[0].get('short_effect', '')
                })
        if i % 100 == 0:
            save_to_csv(abilities, f'result_{i-99}_{i}.csv')
            abilities = []

if __name__ == "__main__":
    main()
