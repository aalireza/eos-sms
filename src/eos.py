from subprocess import check_output
from time import time
from random import sample
import re
import json


signature_holder = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"


def create_wallet(name):
    check_output([
        "cleos", "wallet", "create", "--name", name, "--file",
        "/tmp/{}_password.txt".format(name)
    ])
    with open("/tmp/{}_password.txt".format(name), "r") as f:
        password = f.read()
    return password.rstrip()


def create_keys(name):
    def create_a_key(name):
        filename = "/tmp/{}_keys.txt".format(name)
        check_output(["cleos", "create", "key", "--file", filename])
        with open(filename, "r") as f:
            keys = f.readlines()
        return dict([tuple([y.strip() for y in x.split(':')]) for x in keys])
    return {
        "Owner": create_a_key(name),
        "Active": create_a_key(name)
    }


def extract_all_wallets():
    return re.findall(
        r'"([^"]*)"',
        check_output(["cleos", "wallet", "list"]).decode('utf-8')
    )


def wallet_exists(name):
    return any(name in wallet_name for wallet_name in extract_all_wallets())


def wallet_is_unlocked(name):
    return "{} *".format(name) in extract_all_wallets()


def import_keys(name, keys):
    for x in [signature_holder, *[keys[side]["Private key"]
                                  for side in ["Owner", "Active"]]]:
        check_output([
            "cleos", "wallet", "import", "--name", name, "--private-key", x
        ])


def create_account(name, keys):
    check_output(["cleos", "create", "account", "eosio", name,
                  keys["Owner"]["Public key"], keys["Active"]["Public key"]])


def give_money_to(account, amount):
    pass


def random_name():
    return ''.join(sample("12345abcdefghijklmnopqrstuvwxyz", 11))


class Admin(object):
    def _upload_smartcontract(self):
        check_output(["cleos", "set", "contract", self.name, "./eosio.token",
                      "-p", self.name])

    def set_max_supply(self, amount):
        a = (
            "cleos push action " +
            str(self.name) +
            """ create '{"issuer":"eosio", "maximum_supply":" """[:-1] + str(amount) + """ SMS"}' -p """ + str(self.name) + "@active"
        )
        check_output(a, shell=True)

    def __init__(self):
        self.total_supply = "1000000000.0000"
        name = random_name()
        self._id = Commands.Create()
        self.name = self._id["name"]
        self._upload_smartcontract()
        self.set_max_supply(self.total_supply)
        self.issue_tokens(self.name, "100000000.0000")

    def issue_tokens(self, for_, amount):
        a = (
            "cleos push action {} issue ".format(self.name) +
            """'[ "{}", "{} SMS", "memo" ]' -p eosio""".format(for_, amount)
        )
        print(a)
        check_output(a, shell=True)


class Commands(object):
    @staticmethod
    def Create(admin=None):
        name = random_name()
        print(name)
        keys = create_keys(name)
        print(keys)
        password = create_wallet(name)
        import_keys(name, keys)
        create_account(name, keys)
        if admin is not None:
            Commands.Send(admin.name, "50.0000", from_=admin.name, to=name)
        return {
            "name": name,
            "keys": keys,
            "password": password
        }

    @staticmethod
    def Send(admin_name, amount, from_, to):
        a = (
            "cleos push action " +
            str(admin_name) +
            """ transfer '[ " """[:-1] +
            str(from_) +
            '", "' +
            str(to) +
            '", "' +
            '{} SMS'.format(amount) +
            '", "m"]' +
            "' -p {}@active".format(from_)
        )
        check_output(a, shell=True)
        return True

    def _GetBalance(admin_name, of):
        response = json.loads(check_output(["cleos", "get", "table", admin_name, of, "accounts"]).decode('utf-8'))
        return response['rows'][0]['balance']

    def _GetHistory(with_=None):
        if with_ is not None:
            raise NotImplementedError
        raise NotImplementedError

    @staticmethod
    def Get(topic, *args, **kwargs):
        getattr(Commands, "_Get{}".format(topic.capitalize()))(*args, **kwargs)
