from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
from database import BackEnd

app = Flask(__name__)
db = BackEnd()


def parse_sms(sms, From):
    sms = sms.lower().split()
    commands = {'create' : db.create, 'send' : db.send, 'get' : {'balance' : db.get_balance, 'history' : db.get_history}}
    assert sms[0] in commands
    success = True
    if sms[0] != 'create':
        success = db.verify(num = From, auth = sms[-1])
        if not success:
            return None, None, success
    cmd = commands.get(sms[0])
    params = {}
    if sms[0] == 'send':
        params['amt'] = sms[1]
        params['To'] = sms[3]
    elif sms[0] == 'get':
        assert sms[1] == 'balance' or 'history'
        cmd = cmd.get(sms[1])

    return cmd, params, success

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():

    resp = MessagingResponse()
    Body = request.values.get('Body', None)
    From = request.values.get('From', None)
    From = "".join([n for n in From if n.isnumeric()])

    cmd, params, success = parse_sms(Body, From)

    if not success:
        msg = resp.message('verification failed')
        return str(resp)

    params['From'] = From
    ret_string = misc = None

    print(params)
    print(cmd)
    try:
        response, misc = cmd(**params)
    except:
        response = "invalid command"
    print(response)
    msg = resp.message(response)
    media = misc.get('totp') if misc else None
    if media: msg.media('https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=' + media)

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)

    #https://demo.twilio.com/welcome/sms/reply/


'''
CombinedMultiDict([ImmutableMultiDict([]), ImmutableMultiDict([('ToCountry', 'US'), ('ToState', 'CA'), ('SmsMessageSid', 'SMa26e37aa9eebad6ae723eec2e7a360d3'), ('NumMedia', '0'), ('ToCity', 'LA HONDA'), ('FromZip', ''), ('SmsSid', 'SMa26e37aa9eebad6ae723eec2e7a360d3'), ('FromState', 'CA'), ('SmsStatus', 'received'), ('FromCity', ''), ('Body', 'Dn'), ('FromCountry', 'US'), ('To', '+16506625381'), ('ToZip', '94020'), ('NumSegments', '1'), ('MessageSid', 'SMa26e37aa9eebad6ae723eec2e7a360d3'), ('AccountSid', 'AC52a81e38ad7367da7a67858cb8cb0203'), ('From', '+18058646293'), ('ApiVersion', '2010-04-01')])])
127.0.0.1 - - [10/Nov/2018 17:01:36] "POST /sms HTTP/1.1" 200 -
'''
