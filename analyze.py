import sqlite3
from pylab import *
import operator


def update_dict(d, key):
    key = key.rstrip().strip()
    try:
        d[key] += 1
    except KeyError:
        d[key] = 1


def plot_most_case(datas):
    count = 0
    people_data = {}
    for data in datas:
        try:
            tmp = data[3].split('v.')
            if len(tmp) == 1:
                tmp = tmp[0].split('對')
            if len(tmp) == 1:
                tmp = tmp[0].split('訴')
            if len(tmp) == 1:
                tmp = tmp[0].split('V.')
            if len(tmp) == 1:
                tmp = tmp[0].split('v')

            if len(tmp) == 1 and (tmp[0][:3] == 'RE ' or tmp[0][:3] == 'Re'):
                tmp[0] = tmp[0].strip('RE ')
                update_dict(people_data, tmp[0])
            else:
                idx = tmp[1].find("Reported")
                if idx != -1:
                    tmp[1] = tmp[1][:idx]
                update_dict(people_data, tmp[0])
                update_dict(people_data, tmp[1])
        except IndexError as e:
            count += 1
    # print("total error:" + str(count))
    print(len(people_data))
    sorted_people = sorted(people_data.items(), key=operator.itemgetter(1), reverse=True)
    names = []
    counts = []
    for people in sorted_people[:9]:
        names.append(people[0])
        counts.append(people[1])

    plt.title("MOST CASES")
    explode = [0 for i in range(9)]
    explode[:2] = [0.1, 0.1]
    plt.pie(x=counts, explode=explode, startangle=45)
    tmp = sum(counts)
    for i in range(len(names)):
        names[i] += ' - ' + str(round(counts[i]/tmp * 100, 2)) + "%"
    plt.legend(loc='best', labels=names)
    plt.show()


def plot_court_map(datas):
    # 统计每个法院的案例数
    court_data = {}
    for i in range(len(datas)):
        update_dict(court_data, datas[i][2])

    print(len(court_data))
    explode = [0 for i in range(len(court_data))]
    explode[2] = 0.1
    plt.pie(list(court_data.values()), explode=explode, labels=list(court_data.keys()), autopct='%1.2f%%')
    plt.title("Court Case Map")
    plt.show()


def plot_tendency(datas):
    years_data = {}
    for i in range(len(datas)):
        update_dict(years_data, datas[i][0])

    ks, vs = list(years_data.keys()), list(years_data.values())
    ks.reverse()
    vs.reverse()
    start, end = int(ks[0]), int(ks[-1])
    tks = []
    for i in range(start, end, 10):
        tks.append(i)

    tks.append(2018)
    fg = plt.figure()
    ax = fg.add_subplot()
    ax.plot(vs)
    ax.set_xticklabels(tks, fontsize='small')
    ax.set_xlabel("YEAR")
    ax.set_ylabel("CASE COUNTS")
    ax.set_title("Legal Case Tendency 1945-2018")
    fg.show()


if __name__ == '__main__':
    plt.rcParams['font.sans-serif'] = ['SimHei']
    conn = sqlite3.connect('main.sqlite')
    datas = conn.cursor().execute("SELECT CASE_YEAR,CASE_TYPE,COURT,CASE_INFO FROM Judicial").fetchall()

    plot_tendency(datas)
    plot_most_case(datas)
    plot_court_map(datas)
    conn.close()
