from subprocess import check_output
from time import time
from random import sample
import re
import json


signature_holder = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"


def create_wallet(name):
    check_output([
        "cleos", "wallet", "create", "--name", name, "--file",
        f"/tmp/{name}_password.txt"
    ])
    with open(f"/tmp/{name}_password.txt", "r") as f:
        password = f.read()
    return password.rstrip()


def create_keys(name):
    def create_a_key(name):
        filename = f"/tmp/{name}_keys.txt"
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
    return f"{name} *" in extract_all_wallets()


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


class Admin(object):
    def _upload_smartcontract(self):
        check_output(["cleos", "set", "contract", self.name, "./src/eosio.token",
                      "-p", self.name])

    def set_max_supply(self, amount="1000000000.0000"):
        a = (
            "cleos push action " +
            str(self.name) +
            """ create '{"issuer":"eosio", "maximum_supply":" """[:-1] + str(amount) + """ TMT"}' -p """ + str(self.name) + "@active"
        )
        check_output(a, shell=True)

    def __init__(self):
        self._id = Commands.Create("ldmin")
        self.name = self._id["name"]
        self._upload_smartcontract()
        self.set_max_supply()

    def issue_tokens(self, for_, amount):
        a = (
            f"cleos push action {self.name} issue " +
            f"""'[ "{for_}", "{amount} TMT", "memo" ]' -p eosio"""
        )
        print(a)
        check_output(a, shell=True)


class Commands(object):
    @staticmethod
    def Create(number):
        i = 1
        name = f"{number}{i}"
        while wallet_exists(name) or any(x in str(i) for x in "06789"):
            i += 1
            name = f"{number}{i}"
        print(name)
        keys = create_keys(name)
        print(keys)
        password = create_wallet(name)
        import_keys(name, keys)
        create_account(name, keys)
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
            f'{amount} TMT' +
            '", "m"]' +
            f"' -p {from_}@active"
        )
        try:
            check_output(a, shell=True)
            return True
        except Exception():
            return False

    def _GetBalance(admin_name, of):
        response = json.loads(check_output(["cleos", "get", "table", admin_name, of, "accounts"]).decode('utf-8'))
        return 0 if len(response['rows']) == 0 else response['rows'][0]["balance"]

    def _GetHistory(with_=None):
        if with_ is not None:
            raise NotImplementedError
        raise NotImplementedError

    @staticmethod
    def Get(topic, *args, **kwargs):
        getattr(Commands, f"_Get{topic.capitalize()}")(*args, **kwargs)

