import http.client
import json

conn = http.client.HTTPSConnection("www.runninghub.cn")
payload = json.dumps({
   "apiKey": "c4dbb7471a1649219a6a3cbe7827df47",
   "workflowId": "1904136902449209346"
})
headers = {
   'Host': 'www.runninghub.cn',
   'Authorization': 'Bearer c4dbb7471a1649219a6a3cbe7827df47',
   'Content-Type': 'application/json'
}
conn.request("POST", "/api/openapi/getJsonApiFormat", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))

# 这里正常返回