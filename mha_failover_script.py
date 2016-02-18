#!/usr/bin/env python

"""
mha_failover_script

This is a dummy script, designed to use with mysql_master_ha by Yoshinori Matsunobu
(https://github.com/yoshinorim/mha4mysql-manager,
https://github.com/yoshinorim/mha4mysql-node) as master_ip_failover_script and/or
master_ip_online_change_script .

You still need to write code for your environment for stop, start, stopssh and status
functions, depending on your needs. All the argument parsing and is already
done for you.

Copyright (c) 2016, Pavel Gurkov (true.neu@gmail.com)

Distributed under MIT license, see LICENSE.txt for details
"""


import argparse
import sys
import subprocess
import shlex


class MHAFailoverException(Exception):
    def __init__(self, message):
        super(MHAFailoverException, self).__init__(message)


class MHAFailover(object):
    _exit_code_success = 0
    _exit_code_success2 = 10
    _exit_code_error = 20

    _mysql_client_path = '/usr/bin/mysql'

    _possible_str_args_list = ['command', 'ssh_user', 'orig_master_host', 'orig_master_ip', 'orig_master_port',
                               'new_master_host', 'new_master_port', 'new_master_user', 'new_master_password',
                               'ssh_options', 'new_master_ip', 'orig_master_user', 'orig_master_password',
                               'orig_master_ssh_user', 'new_master_ssh_user']
    _possible_bool_args_list = ['orig_master_is_new_slave']

    @staticmethod
    def split_by_equals(s):
        # mha uses weird arg format like --command=status, thus this function is needed
        return s.split('=', 1)

    def _set_vars_based_on_args(self, parsed_args):
        for arg in self._possible_str_args_list + self._possible_bool_args_list:
            if hasattr(parsed_args, arg):
                setattr(self, arg, getattr(parsed_args, arg))

    def _parse_args(self, arguments):
        parser = self._parser_init()
        parsed_args = parser.parse_args(arguments)
        self._set_vars_based_on_args(parsed_args)

    def _status(self):
        return self._exit_code_success

    def _stop(self):  # if server is not reachable via ssh, autofailover OR online switch (?!)
        if self.orig_master_user and self.orig_master_password:
            # in other words, if it's an online switch
            print("DEBUG: online switch detected")
            self._set_read_only(self.orig_master_host, self.orig_master_port, self.orig_master_user,
                                self.orig_master_password, read_only='ON')
        return self._exit_code_success

    def _stopssh(self):  # if server is reachable via ssh, autofailover
        return self._exit_code_success

    def _set_read_only(self, host, port, user, password, read_only='ON'):
        cmd = '{client_path} -h{host} -P{port} -u{user} -p{password} -e "set global read_only={read_only}"'.format(
            host=host, port=port, user=user, password=password, client_path=self._mysql_client_path,
            read_only=read_only)
        shlexed_cmd = shlex.split(cmd)
        try:
            subprocess.check_call(shlexed_cmd)
        except subprocess.CalledProcessError:
            raise MHAFailoverException("Failed to turn read_only {read_only} on {host}".format(host=host,
                                                                                               read_only=read_only))

    def _start(self):
        # first, try to get rid of read_only
        self._set_read_only(self.new_master_host, self.new_master_port,
                            self.new_master_user, self.new_master_password, read_only='OFF')

        # second, change the meta-db settings, VIP or whatever you use

        return self._exit_code_success

    def __init__(self, args):
        splat_args = list()
        for arg in args[1:]:  # we omit the first one which is script name
            splat_args.extend(self.split_by_equals(arg))
        self._parse_args(splat_args)
        try:
            if self.command == 'status':
                sys.exit(self._status())
            elif self.command == 'stop':
                sys.exit(self._stop())
            elif self.command == 'stopssh':
                sys.exit(self._stopssh())
            elif self.command == 'start':
                sys.exit(self._start())
        except MHAFailoverException as e:
            print("MHAFailoverException: {e}".format(e=str(e)))
            sys.exit(self._exit_code_error)

        print("Unknown command")
        sys.exit(self._exit_code_error)

    def _parser_init(self):
        parser = argparse.ArgumentParser()
        for arg in self._possible_str_args_list:
            parser.add_argument('--{0}'.format(arg), type=str)
        for arg in self._possible_bool_args_list:
            parser.add_argument('--{0}'.format(arg), action='store_true')

        return parser


def main(args):
    MHAFailover(args)

if __name__ == "__main__":
    main(sys.argv)
