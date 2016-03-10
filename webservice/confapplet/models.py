class Conf:
    def __init__(self, conf_id, call_id, create_time):
        self.conf_id = conf_id
        self.call_id = call_id
        self.create_time = create_time
        self.count = 0
        self.status = 0
        self.parts = {}


class Part:
    def __init__(self):
        pass
