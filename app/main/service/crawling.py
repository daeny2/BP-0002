from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote_plus, unquote
from lxml import etree
import xml.etree.ElementTree as ElementTree
from xml.sax import handler, parseString
import json
import xmltodict
from ..config import OPEN_API_URI, MY_API_KEY

def get_open_api_info(name):
  my_api_Key = unquote(MY_API_KEY)
  url = OPEN_API_URI
  queryParams = '?' + urlencode({ quote_plus('ServiceKey') : my_api_Key, quote_plus('item_name') : name })

  request = Request(url + queryParams)
  request.get_method = lambda: 'GET'
  response_body = urlopen(request).read()

  tree = etree.fromstring(response_body)
  json_string = json.dumps(xmltodict.parse(response_body))

  load_json_string = json.loads(json_string)

  open_api_data = load_json_string["response"]["body"]["items"]["item"]

  group_data = dict()

  group_data["ITEM_NAME"] = open_api_data["ITEM_NAME"]#약이름
  group_data["VALID_TERM"] = open_api_data["VALID_TERM"]#유효기간
  group_data["EE_DOC_DATA"] = open_api_data["EE_DOC_DATA"]["DOC"]["SECTION"]["ARTICLE"]#효능효과
  group_data["UD_DOC_DATA"] = open_api_data["UD_DOC_DATA"]["DOC"]["SECTION"]["ARTICLE"]#용법용량

  results = {}
  field_lists = ["ITEM_NAME", "VALID_TERM", "EE_DOC_DATA", "UD_DOC_DATA"]

  for field in field_lists:
    if field == "EE_DOC_DATA":
        effect = []
        if type(group_data["EE_DOC_DATA"])==list:
            for i in range(len(group_data["EE_DOC_DATA"])):
                effect.append(group_data["EE_DOC_DATA"][i]['@title'])
                try:
                    if type(group_data["EE_DOC_DATA"][i]['PARAGRAPH'])==list:
                        for y in group_data["EE_DOC_DATA"][i]['PARAGRAPH']:
                            value_ = list(y.values())
                            if value_[0] == 'p' and value_[3]!='&nbsp;':
                                del value_[0:3]
                                effect.append(''.join(value_))
                    else:
                        effect.append(group_data["EE_DOC_DATA"][i]['PARAGRAPH']['#text'])
                except KeyError:
                    if type(group_data['EE_DOC_DATA'][i])==list:
                        for y in group_data["EE_DOC_DATA"][i]['PARAGRAPH']:
                            value_ = list(y.values())
                            if value_[0] == 'p' and value_[3]!='&nbsp;':
                                del value_[0:3]
                                effect.append(''.join(value_))     
        else:
            if type(group_data["EE_DOC_DATA"]['PARAGRAPH'])==list:
                for y in group_data['EE_DOC_DATA']['PARAGRAPH']:
                    value_ = list(y.values())
                    if value_[0] == 'p' and value_[3]!='&nbsp;':
                        del value_[0:3]
                        effect.append(''.join(value_)) 
            else:
                effect.append(group_data['EE_DOC_DATA']['PARAGRAPH']['#text'])
        results['effect'] = effect
        
    elif field == "UD_DOC_DATA":
        capacity = []
        if type(group_data["UD_DOC_DATA"])==list:
            for i in range(len(group_data["UD_DOC_DATA"])):
                capacity.append(group_data["UD_DOC_DATA"][i]['@title'])
                try:
                    if type(group_data["UD_DOC_DATA"][i]['PARAGRAPH'])==list:
                        for y in group_data["UD_DOC_DATA"][i]['PARAGRAPH']:
                            value_ = list(y.values())
                            if value_[0] == 'p' and value_[3]!='&nbsp;':
                                del value_[0:3]
                                capacity.append(''.join(value_))
                    else:
                        capacity.append(group_data["UD_DOC_DATA"][i]['PARAGRAPH']['#text'])
                except KeyError:
                    if type(group_data['UD_DOC_DATA'][i])==list:
                        for y in group_data["UD_DOC_DATA"][i]['PARAGRAPH']:
                            value_ = list(y.values())
                            if value_[0] == 'p' and value_[3]!='&nbsp;':
                                del value_[0:3]
                                capacity.append(''.join(value_))     
        else:
            if type(group_data["UD_DOC_DATA"]['PARAGRAPH'])==list:
                for y in group_data['UD_DOC_DATA']['PARAGRAPH']:
                    value_ = list(y.values())
                    if value_[0] == 'p' and value_[3]!='&nbsp;':
                        del value_[0:3]
                        capacity.append(''.join(value_)) 
            else:
                capacity.append(group_data['UD_DOC_DATA']['PARAGRAPH']['#text'])
        results['capacity'] = capacity
        
    elif field == "ITEM_NAME":
        results['name'] = group_data["ITEM_NAME"]
        
    else: 
        results['validity'] = group_data["VALID_TERM"]

  return results
