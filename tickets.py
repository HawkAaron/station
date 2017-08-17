# -*- coding: utf-8 -*-

"""
Train tickets query via command-line.

Usage:
    tickets [-gdtkz] <from> <to> <date>

Options:
    -h,--help   显示帮助菜单
    -g          高铁
    -d          动车
    -t          特快
    -k          快速
    -z          直达

Example:
    tickets beijing shanghai 2016-08-25
"""


from docopt import docopt
from stations import stations

from prettytable import PrettyTable


class TrainCollection(object):

    # 显示 预定信息 车次 始末站 出到站 出到时间 历时 余票 一等座 二等座 软卧 硬卧 硬座 无座
    header = '预定信息 车次 始末站 出到站 出到时间 历时 余票 一等座 二等座 软卧 硬卧 硬座 无座'.split()

    def __init__(self, rows, maps):
        self.rows = rows
        self.maps = maps

    @property
    def trains(self):
        _m = self.maps
        for row in self.rows:
            row = row.split('|')
            train = [
                # 预定
                row[1],
                # 车次
                row[3],
                # 始末车站
                '\n'.join([
                    colored('green', row[4]),
                    colored('red', row[5])
                    ]),
                # 出发、到达站
                '\n'.join([
                    colored('green', _m[row[6]]),
                    colored('red', _m[row[7]])
                    ]),
                # 出发、到达时间
                '\n'.join([
                    colored('green', row[8]),
                    colored('red', row[9])
                    ]),
                # 历时
                row[10],
                # 余票YN
                row[11],
                # 一等坐
                row[31],
                # 二等坐
                row[30],
                # 软卧
                row[23],
                # 硬卧
                row[28],
                # 硬坐
                row[29],
                # 无座
                row[26]
            ]
            # t1 = row.split('|')
            # t2 = t1[18:]
            # t2.append(t1[3])
            # yield t2
            yield train

    def pretty_print(self):
        """
        数据已经获取到了，剩下的就是提取我们要的信息并将它显示出来。
        `prettytable`这个库可以让我们它像MySQL数据库那样格式化显示数据。
        """
        pt = PrettyTable()
        # 设置每一列的标题
        pt._set_field_names(self.header)
        for train in self.trains:
            pt.add_row(train)
        print(pt)
        print(self.maps)


import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def cli():
    arguments = docopt(__doc__)
    from_staion = stations.get(arguments['<from>'])
    to_station = stations.get(arguments['<to>'])
    date = arguments['<date>']
    # 构建URL
    # https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=2017-07-19&leftTicketDTO.from_station=BJP&leftTicketDTO.to_station=SHH&purpose_codes=ADULT
    url = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(
        date, from_staion, to_station
    )

    # 添加verify=False参数不验证证书
    r = requests.get(url, verify=False)
    rows = r.json()['data']['result']
    maps = r.json()['data']['map']
    trains = TrainCollection(rows, maps)
    trains.pretty_print()


def colored(color, text):
    table = {
        'red': '\033[0;31;40m',
        'green': '\033[0;32;40m',
        # no color
        'nc': '\033[0m'
    }
    cv = table.get(color)
    nc = table.get('nc')
    return ''.join([cv, text, nc])

if __name__ == '__main__':
    cli()



"""终端颜色显示
格式：\033[显示方式;前景色;背景色m

说明：
前景色            背景色           颜色
---------------------------------------
30                40              黑色
31                41              红色
32                42              绿色
33                43              黃色
34                44              蓝色
35                45              紫红色
36                46              青蓝色
37                47              白色

显示方式           意义
-------------------------
0                终端默认设置
1                高亮显示
4                使用下划线
5                闪烁
7                反白显示
8                不可见

例子：
\033[1;31;40m    <!--1-高亮显示 31-前景色红色  40-背景色黑色-->
\033[0m          <!--采用终端默认设置，即取消颜色设置-->
"""
