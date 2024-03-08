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

hex_stream = "43bf04c82ba910f08101f10a00860000b700000004000210080000155c00000010000000c86bf127b13100432e2508dc3f086f53140000000203090300e463e7240361f689401f39200a2f00df93040000000000a00f000000000000010001aa96ea650000000010000000b6c882ad233fd64d95b5b7678fd120e8005c00000010000000a4a1ef4f90f1314c7e2508dc3f086270140000000203080300234fa92f030047a430010451f64f000a1a000000000000f00a000000000000010001a396ea6500000000100000009ac484d7022e5244bfa0682f7382ddfc005b00000010000000645c9fd2e02cc44ba8e708dc3f08700e130000000203020700f144fb01288bb570bb80d5cc80100000000000000000f004000000000000010001a396ea65000000001000000074f9b7e5eb7f3d49aebfac026398f4d1005f000000100000009595fb063df84847b3fe08dc3f086ad3170000000203060400a7caeb2e04501cbf01f6f2201fb012cba3000000000000000000f00a000000000000010001a296ea65000000001000000054365ebd54ee324ba4aaafc997b09f80005b00000010000000c0ac822ad3b1e3432c0608dc3f086cf31300000002030207002e5a2701282b94770ede1f41360e0000000000000000f0040000000000000100019f96ea6500000000100000003f62cdb251200943ad957eb22b6db168005b000000100000006d2a7755143c1f48609208dc3f086bf8130000000203090700f43b8b0073f48b0188669b404c00cc8d000000000000ac050000000000000100019d96ea6500000000100000008b4a35e1838fbf43b12084e2f82dccf8005f00000010000000931eb15825912147efb308dc3f08666e1700000002030a040020619a0004002dd6501b0a401cf641f7660020a1070000000000f00a0000000000000100019a96ea650000000010000000058a94ed6aa70d4aadeed3a930ff7fba005c00000010000000d1f235711d3a4f4b37c508dc3f08623e1400000002030b0300e36e612703106168001fd7501c9a00050d000000000000f00a0000000000000100019896ea650000000010000000efe09f7a9fe0ee4cb0437592db758680005c000000100000000ce7e7d07b428d49174b08dc3f087f161400000002030a0300a3814d2203002d8241f8665019f60007b2010000000000f00a0000000000000100019796ea65000000001000000065c35359595ed44b90b49ea496ae3c2e005f00000010000000bd328c1ae735834b623908dc3f0877701700000002030904006bb3282304601c8301f8ba2024c6100d60002a2c0a0000000000a00f0000000000000100019196ea650000000010000000da6dbeee92163144a463872d9e46b67c005f000000100000004720401449f7ba44195c08dc3f0865a21700000002030604005d89e1190420165d403b2a401ce112a74200803801000000000008040000000000000100019196ea65000000001000000008bf95833e05ad4ab912cd72f845a17a0062000000100000004c81e2c4827a96423f4b08dc3f086e011a00000002030604004a12200a85301cd760619a41f94a40071141f6740040420f0000000000a00f0000000000000100019196ea65000000001000000006906a88aac9b940939e5116e0288d8f005c00000010000000768ec720d1d2914a622508dc3f086c881400000002030a0300a7aa6f210321f96051f8002018da0007b2010000000000f00a0000000000000100019096ea65000000001000000045810ed3196e604ea2b202d06fbe23c6005b00000010000000e6bff9fac406614142ac08dc3f0862701300000002030907000e0573007309fae1dae7cb9bd101b822000000000000541f0000000000000100008f96ea65000000001000000021d67b082c86284baa5407ccf204c7f9005f00000010000000c72a805b9d0aa54d412d08dc3f087b8b170000000203090400ef67f82e04100dbc401b2a51f98832a7b400400d03000000000050140000000000000100018396ea6500000000100000005a7db4a9cc66f249bef3b55a69edf2ab005f000000100000004f168668a72c744cb43508dc3f08625b170000000203050400cc602b000461f50e40072940139d401c2200e093040000000000a00f0000000000000100018396ea65000000001000000049ac928be1d5094d9437d6650e05c49d005f000000100000008fd2109deeddb44a09ba08dc3f0878021700000002030b04007520ab2f04502d8b201bcd41f65842a5b100237a080000000000a8160000000000000100018296ea65000000001000000074a9d5e62c998c47882356fe45f85ddf005b0000001000000077ecb1469f5a2642ebbc08dc3f08670513000000020309070086b98f0073fe7ba037622e5eeb01983a000000000000541f0000000000000100007d96ea650000000010000000acf9f106fbee95458ba28136341571b0005f000000100000006d6d8cfceefd0c4842aa08dc3f0862701700000002030904001ef3700004500197402dc041f56441f9060020a1070000000000f00a0000000000000100017d96ea65000000001000000015f3bfc1f4be524d9bee34cd41c1fdda005f0000001000000005bff902f8faf94eacc608dc3f0870521700000002030b0400896b9c2e0430617721f5bd505aea52a5870080380100000000002c1a0000000000000100017c96ea65000000001000000011f9fe4d1512e0459e711fb1f88f4aa10001000000c24d0000e460060000"
json_data = parse_hex_stream(hex_stream)
print(f"Header: {json_data[1]}\n Current Page: {json_data[2]}\n Total Pages: {json_data[3]}\n Total Items: {json_data[4]}")
print(json.dumps(json_data[0], indent=4))
