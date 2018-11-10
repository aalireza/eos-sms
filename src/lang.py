def evaluate(text, my_number=3100000000):
    tokens = [token.lower() for token in text.split(' ')]
    command = tokens[0]
    if command == "create":
        return {
            "command": command,
            "number": my_number
        }
    elif command == "send":
        amount = tokens[1]
        target = tokens[2]
        return {
            "command": command,
            "amount": amount,
            "target": target
        }
    elif command == "get":
        topic = tokens[1]
        assert topic in {"balance", "address", "history"}
        assert tokens[2] == "of"
        target = tokens[3]
        assert target == "me" or (
            str(int(target)) == target and len(target) == 10
        )
        if target == "me":
            target = my_number
        response = {
            "command": command,
            "topic": topic,
            "target": target,
        }
        if len(tokens[4:]) != 0:
            if tokens[4] == "since":
                duration = tokens[5]
                unit = tokens[6]
                assert unit in ["day", "min", "week"]
                response["duration"] = duration
                response["unit"] = unit
        return response
