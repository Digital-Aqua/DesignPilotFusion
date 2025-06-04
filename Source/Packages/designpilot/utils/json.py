JNull = None
JBool = bool
JNumber = float
JString = str
JArray = list['JValue']
JObject = dict[str, 'JValue']

JValue = JNull | JBool | JNumber | JString | JArray | JObject

