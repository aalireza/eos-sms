from pymongo import MongoClient
import pyotp
import pyqrcode
import cv2
from PIL import Image
from eos import Admin, Commands

class BackEnd:
    def __init__(self, client = None):
        self.client = MongoClient()
        self.client.drop_database('project_sms')
        self.db = self.client.project_sms
        self.db.user_info.drop()
        self.db.user_info.delete_many({})
        self.user_info = self.db.user_info
        self.admin = Admin()
        
        #create admin
        self.user_info.insert({"_id" : 0,
                               "num" : 0000000000,
                               "seed" : None,
                               "wallet" : self.admin._id
                               })
                               
        
        
    def get_balance(self, **args):
        #return self.user_info.find_one({"_id" : id}).get('balance', 0.0) if id else self.user_info.find_one({"num" : num}).get('balance', 0.0)
        #return str('Balance: %f.4d' %(Commands.Get(topic = "balance", admin_name = self.admin.name, of = args.get('From')))), None
        return 'Balance: %s' %Commands._GetBalance(admin_name = self.admin.name, of = args.get('From')), None
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
        admin_name, amount, from_, to = self.admin.name, args.get('amt'), args.get('From'), args.get('To')
        success = Commands.Send(admin_name, amount, from_, to)
        
        if success:
            return "\nsent %s from your wallet to %s" %(args.get('amt'), args.get('To')), None
        else:
            return "transaction failed", None
    
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
        self.user_info.update_one({"num" : From}, 
                              {"$set": {"num" : From,
                               "seed" : seed,
                               "qr" : qr_location,
                               "wallet" : Commands.Create(From)
                               }}, upsert=True)
        '''
        self.user_info.insert({"num" : From,
                               "seed" : seed,
                               "qr" : qr_location,
                               "wallet" : Commands.Create(From)
                               })
                               '''
        
        ret_string = "\nA new account has been created for %s.\nYour 2FA key is: %s" %(From, seed)
        #ret_string = seed
        print(ret_string, {'totp' : totp, 'seed' : seed, 'media' : qr_location})
        return ret_string, {'totp' : totp, 'seed' : seed, 'media' : qr_location}
    
'''
{'name': 'user3111',
'keys': {
    'Owner': {'Private key': '5J7xUTwbuidUFdiHikfbf5Gs7NqfEfedHg8vGEbrgn16mi9ckZs',
              'Public key': 'EOS5s3xjXMr1LxvMBg8Jz8f5bToXW4MPdz9EhfuR7eNyAwM2JGmLv'},
    'Active': {'Private key': '5JfRi1hqHjembibW9YfHu1ApNM5t3uSr1aH6oqid49Pm78nVCtv',
               'Public key': 'EOS54JLSmt3SuwUxibtJPqJ9HAh2dtrm8rtgaWonijy2bxaiwQ4VP'}
    },
    'password': 'PW5HxxXHC4EnGwyuKyAyV4uofGyQWfmFcXXYRqDQZPnYZXHV1KpYi'}
'''
        
