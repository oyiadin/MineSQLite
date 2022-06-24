# coding=utf-8
# Author: @hsiaoxychen
from minesqlite import MineSQLite
from minesqlite.repl import repl_loop

"""
Test data:

add id 222 name "name BBB" in_date 2022-07-05 department P6 position "SDE4"
add id 111 name "name HHH" in_date 2022-05-05 department P2 position "SDE7"
add id 777 name "name CCC" in_date 2022-06-05 department P1 position "SDE2"
add id 666 name "name GGG" in_date 2022-08-05 department P1 position "SDE6"
add id 555 name "name EEE" in_date 2022-04-05 department P1 position "SDE6"
add id 888 name "name DDD" in_date 2022-02-05 department P5 position "SDE5"
add id 333 name "name AAA" in_date 2022-07-05 department P1 position "SDE6"
add id 444 name "name FFF" in_date 2022-01-05 department P3 position "SDE1"

list
list department P1
list department P1 $sort_desc position
list department P1 $sort_desc position $sort_asc name
"""


def main():
    instance = MineSQLite(
        sysconf_kwargs={'conf_file': open(
            'etc/config.ini')})
    repl_loop(instance)


if __name__ == '__main__':
    main()
