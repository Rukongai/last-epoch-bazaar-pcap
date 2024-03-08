import pyshark

cap = pyshark.FileCapture('pcap\pcap.pcapng')

with open('output.txt', 'a') as output_file:
    for pkt in cap:
        try:
            if pkt.length == "1448" and pkt.ip.dst == 'YOUR LOCAL MACHINE IP' and pkt.transport_layer == "UDP":
                nextpk = (int(pkt.number))
                listingpt1 = (pkt.udp.payload).replace(':', '')
                listingpt2 = (cap[nextpk].udp.payload).replace(':', '')
                fullhex = f"{listingpt1}{listingpt2[26:]}"
                output_file.write(fullhex + "\n\n")
                print(fullhex)
                print("\n\n")
        except:
            print("Error")
            print("\n\n")
