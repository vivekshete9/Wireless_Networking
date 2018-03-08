
import re

myNodes = { '10.1.1.1' : 0,
			'10.1.1.2' : 1,
			'10.1.1.3' : 2,
			'10.1.1.4' : 3,
			'10.1.1.5' : 4,
			'10.1.1.6' : 5,
			'10.1.1.7' : 6,
			'10.1.1.8' : 7,
			'10.1.1.9' : 8,
			'10.1.1.10' : 9,
			'10.1.1.11' : 10,
			'10.1.1.12' : 11,
			'10.1.1.13' : 12,
			'10.1.1.14' : 13,
			'10.1.1.15' : 14,
			'10.1.1.16' : 15,
			'10.1.1.17' : 16,
			'10.1.1.18' : 17,
			'10.1.1.19' : 18,
			'10.1.1.20' : 19,
			'10.1.1.21' : 20,
			'10.1.1.22' : 21,
			'10.1.1.23' : 22,
			'10.1.1.24' : 23,
			'10.1.1.25' : 24,
}

with open("IP_Trace_DSR10.tr","r") as fi:		#fi = file
    t = list()		#t= transmitter list
    r = list()		#r= receiver list
    for ln in fi:
        if ln.startswith("t "):
            t.append(ln[0:])		#all the transmitting nodes get appended here
        if ln.startswith("r "):
        	r.append(ln[0:])		#all the receiving nodes get appended here

myTransmissionList = list()			#initialize all the variables to be used in algo
myReceivingList = list()
tx0list = list()
maxDelay = 0
maxDelay2 = 0
totalDelay = 0
totalDelay2 = 0
# maxDelay = 0
totalPacketsTransmitted = 0
totalPacketsTransmitted2 = 0
# ============================================== Preprocessing =================================================
for x in t:							#filter nodes without receiving or transmitting payloads
	if "Payload" in x:
		myTransmissionList.append(x)	#final list containing transmitters
		# if "/Tx(0)" in
		# RetBuffer = re.search(t'/Tx(0)',i)
		# ipMatch = re.search(r'10.1.1.\d{1,2} > 10.1.1.\d{1,2}', transmission)
#print("appended all transmitters to myTransmissionList")
# i=0
for transmission in myTransmissionList:
	string = "/Tx(0)"
	if string in transmission:
		tx0list.append(transmission)
		myTransmissionList.remove(transmission)
								#no Tx(0) in myTransmissionList
		# print(transmission)
	# RetBuffer = re.search(myTransmissionList'/Tx(0)',i)
	# if RetBuffer:
	# 	tx0list.append(i)
	# 	print(myTransmissionList(i))
#print("Filter all the nodes with Tx(0) from myTransmissionList")

# print("the transmitters whose data is going back to buffer is (tx0list): ",tx0list)

for y in r:
	if "Payload" in y:
		myReceivingList.append(y)		#final list containing receivers
#print("myReceivingList is ready")


# ============================================== Preprocessing 2 =================================================
IPseq2 = ""
for transmission in myTransmissionList:
	ipMatch = re.search(r'10.1.1.\d{1,2} > 10.1.1.\d{1,2}', transmission)
	idMatch = re.search(r'id \d{1,}',transmission)
	nodeMatch = re.search(r'NodeList/\d{1,2}',transmission)
	if ipMatch and idMatch and nodeMatch:
		IPseq = ipMatch.group(0)
		Id = idMatch.group(0)
		node = nodeMatch.group(0).split('/')
		nodenum = node[1].strip()

		# IPseq = IP[0].strip()		#sourceIP in mytransmissionlist
		# if TxValue == 1:				#Tx(1)
		for transx0 in tx0list:
			ipmatchtx0 = re.search(r'10.1.1.\d{1,2} > 10.1.1.\d{1,2}', transx0)
			idMatchtx0 = re.search(r'id \d{1,}',transmission)
			nodeMatch0 = re.search(r'NodeList/\d{1,2}',transmission)
			if ipmatchtx0 and idMatchtx0 and nodeMatch0:
				# TxValue = ReadTx[1].strip()
				IPseq2 = ipmatchtx0.group(0)
				idMatchtx0 = idMatchtx0.group(0)
				node2 = nodeMatch0.group(0).split('/')
				nodenum2 = node2[1].strip()
				break
				# IPseq2 = IP2[0].strip()		#sourceIP in mytransmissionlist
		if IPseq == IPseq2 and idMatch == idMatchtx0 and nodenum == nodenum2:
			myTransmissionList.remove(transmission)	#no duplicate transmission in myTransmissionList

	#AT this stage myTransmissionList should not contain any Tx(0) nor any corresponding Tx(1) already present in Tx(0)

#print("filter all the nodes from mytransmissionlist with corresponding nodes in tx0list")


# ============================================== Algorithm to calculate delay in case Tx = 0 =================================================
if len(tx0list) > 0:
	for transmission in tx0list:
		ipMatch = re.search(r'10.1.1.\d{1,2} > 10.1.1.\d{1,2}', transmission)	 #find node with matching src and dest ip addresses in receivers
		# seqMatch = re.search(r'Retry=\d{1}',transmission)						 #Cannot find expression "Retry" in nodes
		portMatch = re.search(r'length: 1008 \d{1,}',transmission)
		idMatch = re.search(r'id \d{1,}',transmission)
		if ipMatch and idMatch and portMatch:		#and seqMatch
			transmissionTime = re.findall(r't(.*?)/',transmission)
			IP = ipMatch.group(0).split('>')
			sourceIP = IP[0].strip()
			string = "/NodeList/" + str(myNodes[sourceIP])
			if string in transmission:
				destinationIP = IP[1].strip()
				# seqNumber = seqMatch.group(0).split('=')
				# seqNumber = seqNumber[1]
				srcid = idMatch.group(0).split(' ')
				srcid = srcid[1]
				srcport = portMatch.group(0).split(' ')
				srcport = srcport[2]
				for recv in myReceivingList:
					string = "/NodeList/" + str(myNodes[destinationIP])
					if string in recv:
						ipMatch = re.search(r'10.1.1.\d{1,2} > 10.1.1.\d{1,2}', recv)
						# seqMatch = re.search(r'Retry=\d{1}',recv)
						idMatch = re.search(r'id \d{1,}',recv)
						portMatch = re.search(r'length: 1008 \d{1,}',recv)
						if ipMatch and idMatch:								#and seqMatch
							receivingTime = re.findall(r'r(.*?)/',recv)
							IP = ipMatch.group(0).split('>')
							recvsourceIP = IP[0].strip()
							recvdestinationIP = IP[1].strip()
							# recvseqNumber = seqMatch.group(0).split('=')
							# recvseqNumber = recvseqNumber[1]
							desid = idMatch.group(0).split(' ')
							desid = desid[1]
							desport = portMatch.group(0).split(' ')
							desport = desport[2]
							if sourceIP == recvsourceIP and destinationIP == recvdestinationIP and srcid == desid and srcport == desport:  #and seqNumber == recvseqNumber
								if float(transmissionTime[0]) < float(receivingTime[0]):
									delay = float(receivingTime[0]) - float(transmissionTime[0])
									totalDelay2 = totalDelay2 + delay
									TotalD2 = float(totalDelay2)
									totalPacketsTransmitted2 +=1
									if maxDelay2 < delay:
										maxDelay2 = delay
									myReceivingList.remove(recv)
									# print('The delay in a node in tx0list is {}'.format(delay))
									break

# ============================================== Algorithm to calculate delay in case Tx = 1 =================================================
for transmission in myTransmissionList:
	# ipmatchtx0 = re.search(tx0list"10.1.1.\d{1,2} > 10.1.1.\d{1,2}", transmission)

	# print("ip matched with tx0list:", ipmatchtx0)
	ipMatch = re.search(r'10.1.1.\d{1,2} > 10.1.1.\d{1,2}', transmission)	 #find node with matching src and dest ip addresses in receivers
	# seqMatch = re.search(r'Retry=\d{1}',transmission)						 #Cannot find expression "Retry" in nodes
	portMatch = re.search(r'length: 1008 \d{1,}',transmission)
	idMatch = re.search(r'id \d{1,}',transmission)
	if ipMatch and idMatch and portMatch:		#and seqMatch
		transmissionTime = re.findall(r't(.*?)/',transmission)
		IP = ipMatch.group(0).split('>')
		sourceIP = IP[0].strip()
		string = "/NodeList/" + str(myNodes[sourceIP])
		if string in transmission:
			destinationIP = IP[1].strip()
			# seqNumber = seqMatch.group(0).split('=')
			# seqNumber = seqNumber[1]
			srcid = idMatch.group(0).split(' ')
			srcid = srcid[1]
			srcport = portMatch.group(0).split(' ')
			srcport = srcport[2]
			for recv in myReceivingList:
				string = "/NodeList/" + str(myNodes[destinationIP])
				if string in recv:
					ipMatch = re.search(r'10.1.1.\d{1,2} > 10.1.1.\d{1,2}', recv)
					# seqMatch = re.search(r'Retry=\d{1}',recv)
					idMatch = re.search(r'id \d{1,}',recv)
					portMatch = re.search(r'length: 1008 \d{1,}',recv)
					if ipMatch and idMatch:								#and seqMatch
						receivingTime = re.findall(r'r(.*?)/',recv)
						IP = ipMatch.group(0).split('>')
						recvsourceIP = IP[0].strip()
						recvdestinationIP = IP[1].strip()
						# recvseqNumber = seqMatch.group(0).split('=')
						# recvseqNumber = recvseqNumber[1]
						desid = idMatch.group(0).split(' ')
						desid = desid[1]
						desport = portMatch.group(0).split(' ')
						desport = desport[2]
						if sourceIP == recvsourceIP and destinationIP == recvdestinationIP and srcid == desid and srcport == desport:  #and seqNumber == recvseqNumber
							if float(transmissionTime[0]) < float(receivingTime[0]):
								delay = float(receivingTime[0]) - float(transmissionTime[0])
								totalDelay = totalDelay + delay
								TotalD = float(totalDelay)
								totalPacketsTransmitted +=1
								if maxDelay < delay:
									maxDelay = delay
								myReceivingList.remove(recv)
								# print('The delay is {}'.format(delay))
								break
# ============================================== Calculate the results=================================================
averageTime2 = 0
averageTime = totalDelay / totalPacketsTransmitted
if len(tx0list) > 0:
	averageTime2 = totalDelay2/ totalPacketsTransmitted2
	print ("The average time for packets which were send to the buffer (Tx(0)): ", averageTime2)
print ("The average time for packets which were send (Tx(1)): ", averageTime)


averageDelay = (averageTime + averageTime2)/2
print('The average delay is {}'.format(averageDelay))

if maxDelay < maxDelay2:
	maxDelay = maxDelay2
print('The maximum delay is {}'.format(maxDelay))
