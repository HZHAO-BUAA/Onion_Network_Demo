import AES_128
class message(object):

    def __int__(self):
        pass
    def initFromString(self,msgInString):
        pass
    #create key initialization msg
    def create_KeyInit(self,destination,key_id,g,p,A):
        dest_split=destination.split('.')
        destIP='{:08b}'.format(int(dest_split[0]))+'{:08b}'.format(int(dest_split[1]))+'{:08b}'.format(int(dest_split[2]))+'{:08b}'.format(int(dest_split[3]))
        version = '{:04b}'.format(1)
        msg_type = '{:04b}'.format(0)
        msg_empty_space = '{:08b}'.format(0)
        key_id='{:032b}'.format(key_id)
        g = '{:01024b}'.format(g)
        p = '{:01024b}'.format(p)
        A = '{:01024b}'.format(A)
        body = destIP+key_id + g + p + A
        msg_length = '{:016b}'.format(len(body))
        header = version + msg_type + msg_empty_space + msg_length
        message = header + body
        return(message)
   #create key reply msg
    def create_KeyReply(self,destination,key_id,B):
        dest_split = destination.split('.')
        destIP = '{:08b}'.format(int(dest_split[0])) + '{:08b}'.format(int(dest_split[1])) + '{:08b}'.format(
            int(dest_split[2])) + '{:08b}'.format(int(dest_split[3]))
        version = '{:04b}'.format(1)
        msg_type = '{:04b}'.format(1)
        msg_empty_space = '{:08b}'.format(0)
        key_id = '{:032b}'.format(key_id)
        B = '{:01024b}'.format(B)
        body = destIP + key_id + B
        msg_length = '{:016b}'.format(len(body))
        header = version + msg_type + msg_empty_space + msg_length
        message = header + body
        return (message)

    # decode any kinds of msg to element tuple
    def decode_message(self,message):
        version=int(message[0:4],2)
        msg_type=int(message[4:8],2)
        if msg_type==0: #for key init message
            msg_length=int(message[16:32],2)
            dest = str(int(message[32:40], 2))+'.'+str(int(message[40:48], 2))+'.'+str(int(message[48:56], 2))+'.'+str(int(message[56:64], 2))
            key_id=int(message[64:96],2)
            g=int(message[96:1120],2)
            p = int(message[1120:2144],2)
            A = int(message[2144:3168],2)
            return (msg_type,dest,key_id,g,p,A)

        if msg_type==1: # for key reply msg
            msg_length = int(message[16:32], 2)
            dest = str(int(message[32:40], 2)) + '.' + str(int(message[40:48], 2)) + '.' + str(
                int(message[48:56], 2)) + '.' + str(int(message[56:64], 2))
            key_id = int(message[64:96], 2)
            B = int(message[96:1120], 2)
            return (msg_type,dest,key_id,B)
        if msg_type==2:
            seq_num=int(message[16:32],2)
            key_id=int(message[32:64],2)
            cipherText=message[64:]
            return (msg_type,seq_num,key_id,cipherText)
        if msg_type==3: # for error msg
            msg_length = int(message[16:32], 2)
            errorcode=int(message[32:48],2)
            errorID = int(message[48:64], 2)
            return (msg_type, errorcode,errorID)

    # create one layer of shallot
    def create_MessageRelay(self,key_id,next_hop,seq_num,payload,aesKey):
        dest_split=next_hop.split('.')
        next_hopIP='{:08b}'.format(int(dest_split[0]))+'{:08b}'.format(int(dest_split[1]))+'{:08b}'.format(int(dest_split[2]))+'{:08b}'.format(int(dest_split[3]))
        version = '{:04b}'.format(1)
        msg_type = '{:04b}'.format(2)
        msg_empty_space = '{:08b}'.format(0)
        key_id='{:032b}'.format(key_id)
        seq_num='{:016b}'.format(seq_num)
        header = version + msg_type + msg_empty_space + seq_num
        plaintext = header + key_id
        ciphered = next_hopIP + payload

        AESobj = AES_128.AES_128(aesKey)
        ciphered=AESobj.encrypt(ciphered)
        message = plaintext+ciphered
        return message

    # create error msg
    def create_Error(self,error_code,myID):
        version = '{:04b}'.format(1)
        msg_type = '{:04b}'.format(3)
        msg_empty_space = '{:08b}'.format(0)

        error_code = '{:016b}'.format(error_code)
        myID = '{:016b}'.format(myID)
        body=error_code+myID
        msg_length = '{:016b}'.format(len(body))
        header=version+msg_type+msg_empty_space+msg_length
        message = header + body
        return message



























