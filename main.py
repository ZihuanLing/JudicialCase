# coding : utf-8
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import sqlite3

op = Options()
op.add_argument('--headless')
op.add_argument('--disablegpu')
path = 'C:/Users/Administrator/Desktop/JudicialCase/chromedriver.exe'
print("loading driver...")
driver = webdriver.Chrome(executable_path = path, options=op)
print("driver loaded...")
driver.set_page_load_timeout(70)

UNPARSELINK = []

def get_sp(link:str):
    '''返回一个beautifulSoup对象'''
    driver.get(link)
    page = driver.page_source
    sp = BeautifulSoup(page, 'html.parser')
    return sp

def get_folder_list():
    '''抓取主目录下的所有诉讼文件夹'''
    url = "https://legalref.judiciary.hk/lrs/common/ju/judgment.jsp"
    driver.get(url)
    # driver.set_page_load_timeout(30)
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    folders = soup.find_all('td', {'class': 'ThemeXPFolderText'})
    res = []
    for folder in folders:
        item = {}
        item['court'] = folder.a.string
        item['link'] = folder.a.attrs['href']
        res.append(item)
    return res

def parse_folder(folder_url:str, idx:int):
    '''爬取主目录下的二级目录'''
    soup = get_sp(folder_url)
    targetID = 'ctSubTreeID' + str(idx)
    div = soup.find('div', {'id': targetID})
    # div2 = div.find('div', {'class', 'ThemeXPTreeLevel1'})
    tables = div.find_all('table')
    ctItems = []
    for table in tables:
        item = {}
        item['case_type'] = table.a.string
        item['link'] = table.a.attrs['href']
        ctItems.append(item)
    return ctItems


def save_item(conn:sqlite3.Connection ,params):
    try:
        conn.cursor().execute("INSERT INTO Judicial (COURT, CASE_TYPE, CASE_YEAR, CASE_CODE, CASE_DATE, CASE_INFO, CASE_FILE) \
            VALUES (?,?,?,?,?,?,?)", params)
        conn.commit()
    except AttributeError as e:
        conn.close()
        conn = sqlite3.connect('./main.sqlite')
        save_item(conn, params)
        print("@@ sqlite Attribute error occured: ")
        print(e)
    except sqlite3.OperationalError as e:
        conn.execute("CREATE TABLE Judicial (ID INT PRIMARY KEY NULL ,COURT TEXT NULL, CASE_TYPE TEXT NULL, CASE_YEAR TEXT NULL, CASE_CODE TEXT NULL, \
         CASE_DATE TEXT NULL, CASE_INFO TEXT NULL, CASE_FILE TEXT NULL)")
        print("@@ sqlite Operation error occured: ")
        print(e)


def iter_subs(subs):
    """遍历所有的链接，提取数据"""
    # datas = []
    count = 0
    for i in range(len(subs)):
        court = subs[i]['court']
        print("### court: " + court)
        cases = subs[i]['cases']
        for j in range(len(cases)):
            case_type = cases[j]['case_type']
            print("### case type: " + case_type)
            years = cases[j]['years']
            for k in range(len(years)):
                year = years[k]['year']
                link = years[k]['link']
                #print("\t### link: " + years[k]['link'] + "  ==> " + str(i + j + k + 3))
                res = parse_year_item(link, i + j + k + 3)

                for tmp in res:
                    params = [court, case_type, year, tmp['code'], tmp['date'], tmp['result'], tmp['doc']['link']]
                    save_item(conn, params)
                    count += 1

        print("*** DONE ***")
    print("FINISHED")
    print("total: ", str(count))


def get_all_subs():
    '''获取所有子目录'''
    # 获取第一级主目录
    folder_list = get_folder_list()
    tree = []
    for idx1 in range(len(folder_list)):
        item = {}
        court = folder_list[idx1]['court']
        item['court'] = court
        print('court >> ' + court)
        # 获取主目录下的二级目录
        sub_folders = parse_folder(folder_list[idx1]['link'], idx1 + 1)
        cases = []
        for idx2 in range(len(sub_folders)):
            case_type = sub_folders[idx2]['case_type']
            # 获取二级目录下的三级目录：年份
            years = parse_years(sub_folders[idx2], idx1 + idx2 + 2)
            tmp = {'case_type': case_type, 'years': years}
            print("\t## case type: " + case_type)
            cases.append(tmp)
        print("---"*15)
        item['cases'] = cases
        tree.append(item)
    return tree


def parse_years(subItem:dict, idx:int):
    '''爬取一个子文件夹， 子文件夹里面有不同年的文件夹'''
    link = subItem['link']
    driver.get(link)
    page = driver.page_source
    sp = BeautifulSoup(page, 'html.parser')
    targetID = 'ctSubTreeID' + str(idx)
    div = sp.find('div', {'id': targetID})
    tds = div.find_all('td', {'class': 'ThemeXPFolderText'})
    years = []
    for td in tds:
        item = {'year': td.a.string}
        item['link'] = td.a.attrs['href']
        years.append(item)
    return years


def extract_data(tds):
    try:
        href = tds[1].a.attrs['href']
        doc_link = href.split('\'')[1]
        _font = tds[1].font
        date = "NULL"
        if _font != None:
            date = _font.string
        a = tds[1].a.string
        code = tds[1].a.get_text()
        result = tds[2].get_text()
        # result = tds[2].get_text().encode('gbk', 'ignore').decode('utf-8', 'ignore').replace('\xa0', '')
        return {'code': code, 'date': date, 'result': result, 'doc': {'name': a, 'link': doc_link}}
    except KeyError as e:
        pass


def parse_year_item(link, idx):
    """
    爬取每一年的数据, 输入该年份的url地址
    返回数据 - 数组，该年份下的所有案例
    """
    res = []
    targetID = 'ctSubTreeID' + str(idx)
    sp = get_sp(link)
    try:
        div = sp.find('div', {'id': targetID})
        tds = div.find_all('td', {'class': 'ThemeXPItemText'})
        for td in tds:
            tmp_tds = td.find('table').find('table').find_all('td')
            itemdata = extract_data(tmp_tds)
            res.append(itemdata)
    except AttributeError as e:
        print("*** Unparse link : " + link + " || with ID " + targetID)
        UNPARSELINK.append(link)
        print("@@@ Error infomation: ")
        print(e)

    return res


def update_subs(subs):
    datas = []
    for i in range(len(subs)):
        court = subs[i]['court']
        cases = subs[i]['cases']
        for j in range(len(cases)):
            case_type = cases[j]['case_type']
            years = cases[j]['years']
            k = len(years) - 1
            year = years[k]['year']
            link = years[k]['link']
            if year.find('Pre') != -1:
                new_years = parse_years(years[k], i + j + 2)
                cases[j]['years'] = new_years
    print("FINISHED")
    return subs


def main():
    conn = sqlite3.connect('./main.sqlite')
    subs = get_all_subs()
    update_subs(subs)
    iter_subs(subs)



conn = sqlite3.connect('main.sqlite')
if __name__ == '__main__':
    main()
    print(UNPARSELINK)


