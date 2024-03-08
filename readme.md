Notes:

The code isn't clean. It's just for researching and validation. I will make an actual tool if I can figure the rest of the missing pieces out.

Example Item from hex stream:
5f000000 - Length of listing (this one is 92 bytes)
10000000fa20508099aeb84e713108dc - GUID (128bit)
3b9743e304b0159748f88101f10a0122b91700000002040b040051031b00044048cd41f83040610100195a00 - Item Data (Array of bytes, variable length)
204e000000000000 - Gold Value (64bit Signed)
9000000000000000 - Favor Cost (64bit Signed)
01 - BazaarItemState (8bit unsigned)
00 - ownedByRequestingUser (bool)
01 - canBeTradedByRequestingUser (bool)
6dede56500000000 - listedAtUnixSecond (64bit Signed)
100000002386c0d0f3bf604888a1cb12 - Version (128bit)
f2164cf200 - I'm not sure what this, or if it belongs to the beginning of the next listing or the end of this one

Packet starts with 28 characters of something. Not sure what yet. Maybe related to the search query?
Packet ends with 3 32-bit Signed Ints for Current Page, Total Page, and Total Listings, and at the very end is a null hex byte

End of listings packet example
01000000 - Current Page (32bit Signed)
f5000000 - Total Pages (32bit Signed)
0b140000 - Total Listings (32bit Signed)
00

General Notes:
The packets come in 3s for each search
One packet out containing json with the search parameters
2 in return containing listing data
The first is max sized at 1448 length
The next one is whatever but immediately follows.

Packet 1 has 28 characters prefixing the beginning of the listings
Packet 2 has 26 characters prefixing the continuation of the listings

Things I am still working on:
I'd like to identify the full structure of the Item Data byte array
I can't find out where the rolls are for any of the affixes or implicits. This is my number one issue atm and needs to be solved for this to continue.
I don't think I have the right byte for affix count because it doesn't always work. 
It seems to trip up with uniques and I don't know yet where item rarity is for certain. 
I haven't implemented unique look ups as a result so assuming a unique doesn't break this, it'll report wrong

For the rolls, i'm concerned that they might be somehow tied to the id guid or version guid. I have nothing to support this, I just can't figure it out.
There are 2 bytes between each affix in the item data, but I don't know what they are for. If they're for tier and roll, I can't figure out how to convert them properly.
