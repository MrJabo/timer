import json
import functools
import re

class Activity:
    #__attributes__ = ["name", "duration", "flags", "color"]
    __attributes__ = ["name"]

    def __init__(self, name, duration, description, flags, color):
        self.name = name
        self.duration = duration
        self.description = description
        self.flags = flags
        self.color = color

    @classmethod
    def __as_activity__(cls, obj):
        has_attributes = functools.reduce(lambda x,y: x and y, \
                                          [attr in obj for attr \
                                           in cls.__attributes__], True)
        if has_attributes:
            name = obj["name"]
            duration = 0
            if "duration" in obj:
                duration = obj["duration"]
            description = ""
            if "description" in obj:
                description = obj["description"]
            flags = []
            if "flags" in obj:
                flags = obj["flags"]
            col = "yellow"
            if "color" in obj:
                col = obj["color"]
            color = "\033[0m"
            if col == "blue":
                color = "\033[1;34m"
            elif col == "cyan":
                color = "\033[1;36m"
            elif col == "red":
                color = "\033[1;31m"
            elif col == "yellow":
                color = "\033[1;33m"
            elif col == "green":
                color = "\033[1;32m"

            return cls(name, duration, description, flags, color)
        return obj

    @classmethod
    def from_json(cls, json_string):
        obj = json.loads(json_string, object_hook=cls.__as_comment__)
        return obj

    def __repr__(self):
        return str(self.__dict__)

class DataEncoder(json.JSONEncoder):
    def default(self, object):
        return object.__dict__

class Config:
    __attributes__ = ["activities"]

    def __init__(self, activities):
        self.activities = activities
        self.breaks = 0
        for activity in activities:
            if "break" in activity.flags:
                self.breaks += 1
    
    def __eq__(self, other):
        return self.to_json() == other.to_json()

    def __hash__(self):
        return self.to_json().__hash__()

    def __repr__(self):
        return str(self.__dict__)

    @classmethod
    def to_json(cls, obj):
        json_string = DataEncoder().encode(obj)
        return json_string

    def to_json(self):
        #json_string = json.dumps(self.__dict__)
        json_string = DataEncoder().encode(self)
        return json_string

    @classmethod
    def __as_config__(cls, obj):
        has_attributes = functools.reduce(lambda x,y: x and y, \
                                          [attr in obj for attr \
                                           in cls.__attributes__], True)
        if has_attributes:
            config = Config(obj["activities"])
            return config
        else:
            return Activity.__as_activity__(obj)

    @classmethod
    def from_json(cls, json_string):
        obj = json.loads(json_string, object_hook=cls.__as_config__)
        return obj

    @classmethod
    def load(cls, path):
        config = None
        metadata = []
        content = ""
        comment_re = re.compile("^[ \t]*#")
        with open(path, 'r') as fd:
            for line in fd:
                if comment_re.match(line) != None:
                    metadata.append(line)
                else:
                    content += line
                    
        config = cls.from_json(content)
        return metadata, config

