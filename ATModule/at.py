# Copyright (c) Quectel Wireless Solution, Co., Ltd.All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
@file      : at.py
@author    : Jack Sun (jack.sun@quectel.com)
@brief     : <Description>
@version   : v1.0.0
@date      : 2025-02-17 14:12:29
@copyright : Copyright (c) 2025
"""

import ure
import sys
import modem
import osTimer
import _thread
import log as logging
from machine import UART
try:
    import atcmd
except ImportError:
    atcmd = None

log = logging.getLogger(__name__)

CRLF = "\r\n"


class ATServer:
    pattern = r"^(AT|at)((\+|\*)?[a-zA-Z]+)(=?)((.+),?)?$"

    def __init__(self, UARTn, buadrate=115200, databits=8, parity=0, stopbits=1, flowctl=0, echo=True, stack_size=0x2000):
        self.__sem = _thread.allocate_semphore(0xFF)
        while self.__sem.getCnt()[1] > 0:
            self.__sem.acquire()
        self.__stop_sem = _thread.allocate_semphore(1)
        while self.__stop_sem.getCnt()[1] > 0:
            self.__stop_sem.acquire()
        self.__uart_args = (UARTn, buadrate, databits, parity, stopbits, flowctl)
        self.__uart = None
        self.__echo = echo
        self.cmd_table = {}
        self.__tid = None
        self.__stack_size = stack_size
        self._recv_data = ""
        self._recv_run = 0

    def __recv_thread_start(self):
        if not self.__tid or (self.__tid and not _thread.threadIsRunning(self.__tid)):
            self._recv_run = 1
            _thread.stack_size(self.__stack_size)
            self.__tid = _thread.start_new_thread(self.__recv_cmd, ())

    def __recv_thread_stop(self):
        if self.__tid and _thread.threadIsRunning(self.__tid):
            self._recv_run = 0
            if self.__sem.getCnt()[1] < self.__sem.getCnt()[0]:
                self.__sem.release()
            _timer = osTimer()
            _timer.start(5 * 1000, 0, self.__recv_stop_overtime)
            self.__stop_sem.acquire()
            _timer.stop()
        self.__tid = None

    def __recv_stop_overtime(self, *args):
        try:
            if self.__stop_sem.getCnt(1) < self.__stop_sem.getCnt(0):
                self.__stop_sem.release()
        except Exception:
            pass

    def __uart_callback(self, args):
        # log.debug("__uart_callback args %s" % str(args))
        if self.__sem.getCnt()[1] < self.__sem.getCnt()[0]:
            self.__sem.release()
        self.__recv_thread_start()

    def __recv_cmd(self):
        while self._recv_run:
            try:
                if self.__uart.any() <= 0:
                    self.__sem.acquire()

                while self.__uart.any() > 0:
                    self._recv_data += self.__uart.read(1024).decode()
                    pos = self._recv_data.find(CRLF)
                    if pos == -1:
                        continue
                    if self.__echo:
                        self.reply(self._recv_data[:pos + 2])
                    self.__parse(self._recv_data[:pos])
                    self._recv_data = self._recv_data[pos + 2:]
            except Exception as e:
                sys.print_exception(e)
                log.error(str(e))
        self.__stop_sem.release()

    def __cmd_resp(self, res):
        if res[1]:
            _msg_ = "%s%s" % ((CRLF if not self.__echo else ""), res[1])
            self.replyln(_msg_)
        if res[0] is True:
            self.replyln(("%sOK" % CRLF) if not res[1] and not self.__echo else "OK")
        elif not res[1]:
            self.replyln("ERROR" if self.__echo else "%sERROR" % CRLF)

    def __parse(self, cmd_line):
        log.debug("cmd_line %s" % cmd_line)
        m = ure.match(self.pattern, cmd_line)
        if m:
            log.debug(", ".join(["m.group(%s) %s" % (i, m.group(i)) for i in range(6)]))
            cmd = m.group(2)
            cmd_obj = self.cmd_table.get(str(cmd).upper())
            if cmd_obj:
                if m.group(4) == "=":
                    if cmd[0] in ("+", "*"):
                        if m.group(5) == "?":
                            log.debug("at cmd help")
                            res = cmd_obj.help()
                            self.__cmd_resp(res)
                        else:
                            log.debug("at cmd setup 1")
                            param = m.group(5).split(",")
                            res = cmd_obj.setup(*param)
                            self.__cmd_resp(res)
                    else:
                        self.replyln("ERROR")
                else:
                    if m.group(5) == "?":
                        log.debug("at cmd query")
                        res = cmd_obj.query()
                        self.__cmd_resp(res)
                    else:
                        if m.group(5):
                            log.debug("at cmd setup 2")
                            param = m.group(5).split(",")
                            res = cmd_obj.setup(*param)
                            self.__cmd_resp(res)
                        else:
                            log.debug("at cmd exec")
                            res = cmd_obj.exec()
                            self.__cmd_resp(res)
            else:
                if atcmd:
                    self.__iner_at_cmd(cmd_line)
                else:
                    self.__cmd_resp((False, "ERROR: NOT SUPPORT CMD."))
        else:
            if cmd_line.lower() == "at":
                cmd_obj = self.cmd_table.get("AT")
                if cmd_obj:
                    res = cmd_obj.query()
                    self.__cmd_resp(res)
                else:
                    if atcmd:
                        self.__iner_at_cmd(cmd_line)
                    else:
                        self.__cmd_resp((False, "ERROR: NOT SUPPORT CMD."))
            else:
                self.__cmd_resp((False, "ERROR: AT CMD NOT COMPARE."))

    def __iner_at_cmd(self, cmd_line):
        try:
            resp = bytearray(512)
            atcmd.sendSync(cmd_line + "\r\n", resp, "", 20)
            self.reply(resp.strip(b"\x00"))
        except Exception as e:
            sys.print_exception(e)

    def open(self):
        self.__uart = UART(*self.__uart_args)
        self.__uart.set_callback(self.__uart_callback)
        self.__recv_thread_start()

    def close(self):
        self.__uart.close()
        self.__recv_thread_stop()

    def register(self, cmd_obj):
        self.cmd_table[cmd_obj.CMD] = cmd_obj

    def reply(self, msg):
        self.__uart.write(msg)

    def replyln(self, msg):
        self.reply(msg + CRLF)

    def echo_enable(self, val):
        if isinstance(val, bool) or (isinstance(val, int) and val in (0, 1)):
            self.__echo = bool(val)
            return True
        return False


class ATCMDBase:

    def __init__(self):
        pass

    def set_module(self, module, name):
        setattr(self, ("__%s" % name), module)

    def help(self):
        return (False, "")

    def query(self):
        return (False, "")

    def setup(self, *args):
        return (False, "")

    def exec(self):
        return (False, "")


class ATIMEI(ATCMDBase):
    CMD = "+IMEI"

    def __init__(self):
        super().__init__()

    def query(self):
        try:
            return (True, "%s: %s%s" % (self.CMD, modem.getDevImei(), CRLF))
        except Exception as e:
            sys.print_exception(e)
            return (False, "")


def test():
    at_server_cfg = {
        "UARTn": UART.UART2,
        "buadrate": 115200,
        "databits": 8,
        "parity": 0,
        "stopbits": 1,
        "flowctl": 0,
        "echo": True,
        "stack_size": 0x2000
    }
    at_server = ATServer(**at_server_cfg)
    at_server.register(ATIMEI())  # Register yourself at cmd.
    at_server.open()


if __name__ == "__main__":
    test()
