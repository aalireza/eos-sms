from eos import Commands


class TextEvaluator(object):
    def __init__(self, my_number):
        self._number = my_number

    @property
    def my_number(self):
        return self._number

    def read(self, text):
        tokens = [token.lower() for token in text.split(' ')]
        command = tokens[0]
        if command == "create":
            return Commands.Create(self.my_number)
        elif command == "send":
            return Commands.Send(
                amount=tokens[1],
                from_=self.my_number,
                to=tokens[2]
            )
        elif command == "get":
            topic = tokens[1]
            if topic == "balance":
                return Commands.Get(topic)
            elif topic == "history":
                return Commands.Get(
                    topic,
                    with_=(
                        False
                        if len(tokens[2:]) == 0 or (tokens[2] != "with") else
                        tokens[3]
                    )
                )
