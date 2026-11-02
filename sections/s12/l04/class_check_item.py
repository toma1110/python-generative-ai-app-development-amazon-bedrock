def format_check(status):
    return f'API応答: {status}'


class CheckItem:
    def __init__(self, status):
        self.status = status

    def format(self):
        return f'API応答: {self.status}'


function_message = format_check("ok")
print(function_message)

item = CheckItem("ok")
message = item.format()
print(message)
