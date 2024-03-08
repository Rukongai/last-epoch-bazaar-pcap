The code isn't clean. It's just for researching and validation. I will make an actual tool if I can figure the rest of the missing pieces out.


## Example Item from hex stream:

| Purpose           | Type/Size  | Value        |
| ------------- |-------------| -----|
| Length of listing | 128bit | 5f000000      |
| GUID  |  | 10000000fa20508099aeb84e713108dc |
| Item Data | Array of bytes | 3b9743e304b0159748f88101f10a0122b91700000002040b040051031b00044048cd41f83040610100195a00|
| Gold Value | 64bit Signed | 204e000000000000 |
| Favor Cost | 64bit Signed |9000000000000000 |
| BazaarItemState | 8bit | 01  |
| ownedByRequestingUser | bool | 00 | 
| canBeTradedByRequestingUser | bool | 01 | 
| listedAtUnixSecond | 64bit Signed | 6dede56500000000 |
| Version | 128bit |100000002386c0d0f3bf604888a1cb12 |
| No idea | | f2164cf200 |

I'm not sure what the last item is, or if it belongs to the beginning of the next listing or the end of this one

Packet starts with 28 characters of something. Not sure what yet. Maybe related to the search query?

## End of listings packet example

Packet ends with 3 32-bit Signed Ints for Current Page, Total Page, and Total Listings, and at the very end is a null hex byte

| Purpose           | Type/Size  | Value        |
| ------------- |-------------| -----|
| Current Page | 32bit Signed | 01000000 |
| Total Pages | 32bit Signed | f5000000 |
| Total Listings | 32bit Signed | 0b140000 |
| Null | Null | 00 |

## General Notes:

The packets come in 3s for each search
One packet out containing json with the search parameters
2 in return containing listing data
The first is max sized at 1448 length
The next one is whatever but immediately follows.

Packet 1 has 28 characters prefixing the beginning of the listings
Packet 2 has 26 characters prefixing the continuation of the listings


## Things I am still working on:
* I'd like to identify the full structure of the Item Data byte array
* I can't find out where the rolls are for any of the affixes or implicits. This is my number one issue atm and needs to be solved for this to continue.
* I don't think I have the right byte for affix count because it doesn't always work. 
* It seems to trip up with uniques and I don't know yet where item rarity is for certain. 
* I haven't implemented unique look ups as a result so assuming a unique doesn't break this, it'll report wrong


For the rolls, i'm concerned that they might be somehow tied to the id guid or version guid. I have nothing to support this, I just can't figure it out.

There are 2 bytes between each affix in the item data, but I don't know what they are for. If they're for tier and roll, I can't figure out how to convert them properly.
