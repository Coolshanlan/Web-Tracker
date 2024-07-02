import requests, json
def goods_detail(item_id, shop_id):
    url = 'https://shopee.tw/api/v2/item/get?itemid=' + str(item_id) + '&shopid=' + str(shop_id)
    r = requests.get(url,headers = my_headers)
    st= r.text.replace("\\n","^n")
    st=st.replace("\\t","^t")
    st=st.replace("\\r","^r")
    
    gj=json.loads(st)
    return gj

item_id='46413286'
shop_id='19379438985'
my_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "referer": "https://shopee.tw/",
            "X-Requested-With": "XMLHttpRequest",
            }
print(goods_detail(item_id,shop_id))
