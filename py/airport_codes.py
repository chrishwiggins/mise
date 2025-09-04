#!/usr/bin/env python3

# Dictionary of common airport codes
airport_codes = {
    'sfo': 'San Francisco International Airport',
    'ewr': 'Newark Liberty International Airport',
    'agp': 'Málaga-Costa del Sol Airport',
    'vie': 'Vienna International Airport',
    'ist': 'Istanbul Airport',
    'auh': 'Abu Dhabi International Airport',
    'cnx': 'Chiang Mai International Airport',
    'hkt': 'Phuket International Airport',
    'bkk': 'Suvarnabhumi Airport (Bangkok)',
    'lax': 'Los Angeles International Airport',
    'jfk': 'John F. Kennedy International Airport',
    'lhr': 'London Heathrow Airport',
    'cdg': 'Charles de Gaulle Airport (Paris)',
    'nrt': 'Narita International Airport (Tokyo)',
    'dxb': 'Dubai International Airport',
    'sin': 'Singapore Changi Airport',
    'hkg': 'Hong Kong International Airport',
    'ams': 'Amsterdam Airport Schiphol',
    'fra': 'Frankfurt Airport',
    'muc': 'Munich Airport',
}

def unlock_airport_codes(route_string):
    """Convert airport codes in a route string to full names."""
    # Split by arrow and strip whitespace
    codes = [code.strip() for code in route_string.split('->')]
    
    # Convert each code to full name
    full_names = []
    for code in codes:
        code_lower = code.lower()
        if code_lower in airport_codes:
            full_names.append(f"{code.upper()} ({airport_codes[code_lower]})")
        else:
            full_names.append(f"{code.upper()} (Unknown Airport)")
    
    return full_names

# Test with the provided string
route = "sfo -> ewr -> ist -> lax"
print("Original route:")
print(route)
print("\nExpanded route:")
expanded = unlock_airport_codes(route)
for i, airport in enumerate(expanded, 1):
    print(f"{i:2}. {airport}")

print("\nFull journey:")
print(" -> ".join([name.split('(')[1].rstrip(')') for name in expanded]))
