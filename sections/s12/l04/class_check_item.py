def format_check(name, status):
    return f"{name}: {status}"


class CheckItem:
    def __init__(self, name, status):
        self.name = name
        self.status = status

    def format(self):
        return f"{self.name}: {self.status}"


function_message = format_check("API応答", "ok")
print(function_message)

item = CheckItem("API応答", "ok")
message = item.format()
print(message)
