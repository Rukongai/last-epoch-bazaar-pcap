import json
from datetime import datetime

# Function to convert hex string to integer
def hex_to_le(hex_string):
    reversed_hex = ''.join(reversed([hex_string[i:i+2] for i in range(0, len(hex_string), 2)]))
    return int(reversed_hex, 16)

def hex_to_be(hex_string):
    return int(hex_string, 16)

def hex_to_fixed_point(hex_string):
    integer_part_hex = hex_string[:8]  # First 8 characters
    fractional_part_hex = hex_string[8:]  # Remaining characters
    fractional_part_float = int(fractional_part_hex, 16) / 16**len(fractional_part_hex)
    fixed_point_float = hex_to_le(integer_part_hex) + fractional_part_float
    return fixed_point_float

# Function to convert hex string to boolean
def hex_to_bool(hex_string):
    return bool(int(hex_string, 16))

# Function to convert hex timestamp to datetime
def hex_to_datetime(hex_timestamp):
    timestamp = hex_to_fixed_point(hex_timestamp)
    dt_object = datetime.fromtimestamp(timestamp)
    return dt_object.strftime('%a, %d.%m.%Y %H:%M:%S')

def get_status(status_code):
    status_mapping = {
        1: "Unsold",
        8: "Cancelled",
        0: "None",
        4: "Redeemed",
        2: "Sold"
    }
    return status_mapping.get(status_code, "Unknown")

def get_label_for_basetype(type_id):
    with open('./baseTypeIDs.json', 'r') as f:
        data = json.load(f)
        
        for obj in data:
            if obj['value'] == type_id:
                label = obj['label']
                # Replace underscores with spaces
                label = label.replace('_', ' ')
                # Capitalize first letter
                label = label.capitalize()
                return label
                
    return None  # Return None if no match is found

def get_label_for_subtype(base_id, sub_id):
    with open('./MasterItemsList.json', 'r') as f:
        data = json.load(f)
        
        for obj in data['EquippableItems']:
            if obj['baseTypeID'] == base_id:
                for sub_obj in obj['subItems']:
                    if sub_obj['subTypeID'] == sub_id:
                      label = sub_obj['name']
                      return label
                
    return None  # Return None if no match is found

def get_affix_labels(affix_id):
    with open('./Affixs.json', 'r') as f:
        data = json.load(f)
        for obj in data['affix']:
            if obj['id'] == affix_id:
                label = obj['name']
                return label
    return

def get_affixes(input_string, integer):
    if integer is None:
        return None
    
    affixes = []
    i = 0
    while i < integer:
      start_pos = 78 + (6 * i)
      end_pos = 80 + (6 * i)
      affix = get_affix_labels(hex_to_le(input_string[start_pos:end_pos]))
      affixes.append(affix)
      i += 1
    
    return affixes

# Function to parse hex stream and create JSON objects
def parse_hex_stream(hex_stream):
    items = []

    #Sizes
    gold_size = 16
    favor_size = 16
    state_size = 2
    owned_size = 2
    trade_size = 2
    listed_size = 16
    version_size = 32

    stream_length = len(hex_stream)
    header = hex_stream[:56]
    current_page = hex_to_le(hex_stream[stream_length-26:stream_length-18])
    total_pages = hex_to_le(hex_stream[stream_length-18:stream_length-10])
    total_items = hex_to_le(hex_stream[stream_length-10:stream_length])
    hex_stream = hex_stream[56:]
    while len(hex_stream) > 36:
        data_length = hex_to_le(hex_stream[:8])*2
        data_offset = data_length-88
        gold_offset = data_offset+gold_size
        favor_offset = gold_offset+favor_size
        state_offset = favor_offset+state_size
        owned_offset = state_offset+owned_size
        trade_offset = owned_offset+trade_size
        listed_offset = trade_offset+listed_size
        version_offset = listed_offset+version_size
        item = {}
        item['DataLength'] = hex_to_le(hex_stream[:8])
        item['GUID'] = hex_stream[8:40]
        item['Data'] = hex_stream[40:data_offset]
        item['BaseType'] = get_label_for_basetype(hex_to_le(hex_stream[58:60]))
        item['SubType'] = get_label_for_subtype(hex_to_le(hex_stream[58:60]), hex_to_le(hex_stream[60:62]))
        item['AffixCount'] = hex_to_le(hex_stream[74:76])
        item['Affixes'] = get_affixes(hex_stream, item['AffixCount'])
        item['ForgingPotential'] = hex_to_le(hex_stream[72:74])
        item['GoldValue'] = hex_to_le(hex_stream[data_offset:gold_offset])  # Convert hex to integer
        item['FavorBuyCost'] = hex_to_le(hex_stream[gold_offset:favor_offset])  # Convert hex to integer
        item['State'] = get_status(hex_to_be(hex_stream[favor_offset:state_offset]))  # Convert hex to integer
        item['IsOwnedByRequestingUser'] = hex_to_bool(hex_stream[state_offset:owned_offset])  # Convert hex to boolean
        item['canBeTradedByRequestingUser'] = hex_to_bool(hex_stream[owned_offset:trade_offset])  # Convert hex to boolean
        item['ListedAtUnixSecond'] = hex_to_datetime(hex_stream[trade_offset:listed_offset])  # Convert hex to datetime
        item['Version'] = hex_stream[listed_offset:version_offset]
        hex_stream = hex_stream[data_length+8:]
        items.append(item)
    return items, header, current_page, total_pages, total_items

hex_stream = ""
json_data = parse_hex_stream(hex_stream)
print(f"Header: {json_data[1]}\n Current Page: {json_data[2]}\n Total Pages: {json_data[3]}\n Total Items: {json_data[4]}")
print(json.dumps(json_data[0], indent=4))
