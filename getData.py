import csv
import copy
from bs4 import BeautifulSoup
import requests

base_url = "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2019/"
result = []


# 获取省份
def getData():
    # 2019年最新的统计局最新的地域数据
    index_url = base_url + "index.html"
    response = requests.request("GET", index_url)
    html_first = response.content.decode("gbk", "ignore")

    # bs = BeautifulSoup(html_first, "html.parser")
    bs = BeautifulSoup(html_first, "lxml")  # 更快
    # provinces = bs.find_all('tr')
    ps = {}
    provinces = bs.select('tr[class="provincetr"]')
    for province in provinces:
        for item in province.contents:
            if (item.a != None):
                ps[item.a.text] = item.a['href']

    for (k, v) in ps.items():
        getData1(k, base_url + v)

        # 先测试一个
        # break


#  pcode pname, ccode cname,acode aname  获取城市
def getData1(provinceName, provinceUrl):
    print("===============:" + provinceName)

    pname = provinceName

    response = requests.request("GET", provinceUrl)
    html = response.content.decode("gbk", "ignore")

    bs = BeautifulSoup(html, "lxml")  # 更快
    citys = bs.select('tr[class="citytr"]')

    for city in citys:
        # 特殊城市处理
        cname = city.contents[1].a.text
        if ((cname == "市辖区") | (cname == "县")):
            cname = pname

        if (cname == "省直辖县级行政区划"):
            cname = ""

        code = city.contents[0].a.text
        pcode = code[0:2]
        url = base_url + city.contents[1].a["href"]
        ccode = "C" + code
        getData2(pcode, pname, ccode, cname, url)


# 保存到cvs文件中   == 获取区
def getData2(pcode, pname, ccode, cname, url):
    # 获取三级页面
    response = requests.request("GET", url)
    html = response.content.decode("gbk", "ignore")
    bs = BeautifulSoup(html, "lxml")  # 更快
    counties = bs.select('tr[class="countytr"]')
    for county in counties:
        if ("市辖区" == county.contents[1].text):
            # 不保存
            continue
        else:
            data = {}
            if (county.contents[0].a != None):
                acode = "A" + county.contents[0].a.text
                aname = county.contents[1].a.text
            else:
                acode = "A" + county.contents[0].text
                aname = county.contents[1].text
            # 保存
            data['pcode'] = pcode
            data['pname'] = pname
            if (cname == ""):
                data['cname'] = aname
            else:
                data['cname'] = cname
            data['ccode'] = ccode
            data['acode'] = acode
            data['aname'] = aname
            result.append(data)


# 只到省市区级别
if __name__ == '__main__':
    getData()
    with open('area.csv', 'w', newline='') as f:
        f_scv = csv.DictWriter(f, list(result[0].keys()))  # 获取头
        f_scv.writeheader()
        f_scv.writerows(result)
        f.close()

# python全局环境生成requirements.txt
# 安装 :  pip install pipreqs
# 在当前目录生成 :  pipreqs . --encoding=utf8 --force
# 使用requirements.txt安装依赖的方式: pip install -r requirements.txt
