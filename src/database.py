from pymongo import MongoClient
import pyotp
import pyqrcode
import cv2
from PIL import Image

def send(destination):
    pass

def get_balance(acc):
    pass

class BackEnd:
    def __init__(self, client = None):
        self.client = MongoClient()
        self.db = self.client.project_sms
        self.user_info = self.db.user_info


    def get_balance(self, **args):
        #return self.user_info.find_one({"_id" : id}).get('balance', 0.0) if id else self.user_info.find_one({"num" : num}).get('balance', 0.0)
        return 'yo balance is ', None

    def get_history(self, **args):
        return None, None

    def send(self, **args):
        '''
        s_balance = self.get_balance(num = sender_num, id = sender_id)
        assert s_balance >= amt
        r_balance = self.get_balance(num = reciever_num)
        sender = {'_id' : sender_id} if sender_id else {'num' : sender_num}
        reciever = {'num' : reciever_num}
        self.user_info.update_one(sender, { "$set": { "balance": s_balance - amt } })
        self.user_info.update_one(reciever, { "$set" : {"balance" : r_balance + amt}})
        return True
        '''
        return "sending %s from your wallet to %s" %(args.get('amt'), args.get('To')), None

    def verify(self, num, auth):
        user = self.user_info.find_one({'num' : num})
        user.get('seed')
        return pyotp.TOTP(user.get('seed')).verify(auth)

    def create(self, **args):
        #generate & store CRS
        From = args.get('From')
        seed = pyotp.random_base32()
        totp = pyotp.TOTP(seed).provisioning_uri("project_sms", issuer_name="eos_hackathon")
        qr = pyqrcode.create(totp)
        qr_location = 'qr_codes/%s.png' %From
        qr.png(qr_location, scale=5)
        self.user_info.insert({"num" : From,
                               "seed" : seed,
                               "qr" : qr_location})
        ret_string = "A new account has been created for %s.\nYour 2FA key is: %s" %(From, seed)
        print (ret_string)
        return ret_string, {'totp' : totp, 'seed' : seed, 'media' : qr_location}



'''
    data = {"_id" : None,
            "name" : None,
            "num" : None,
            "balance" : 0.0,
            "pub_key" : None
            }
'''
