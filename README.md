# mha_external_scripts_py
A small collection of dummy scripts to use with mysql-master-ha written in Python

#### mha_failover_script

This is a dummy script, designed to use with mysql_master_ha by Yoshinori Matsunobu
(https://github.com/yoshinorim/mha4mysql-manager,
https://github.com/yoshinorim/mha4mysql-node) as master_ip_failover_script and/or
master_ip_online_change_script .


You still need to write code for your environment for stop, start, stopssh and status
functions, depending on your needs. All the argument parsing and is already
done for you.

Distributed under MIT License (see LICENSE.txt)

Copyright (c) 2016, Pavel Gurkov (true.neu@gmail.com)
