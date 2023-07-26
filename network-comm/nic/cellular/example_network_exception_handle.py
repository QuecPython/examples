import net
import dataCall
import _thread
import osTimer
import utime
import sys_bus


CFUN_SWITCH_TOPIC = 'cfun_switch_timer'
NETWORK_EVENT_TOPIC = 'network_event'

network_monitor = None

class NetworkConnectState:
    DISCONNECT = 0
    CONNECT = 1


class NetworkExceptionService:
    def __init__(self):
        self.timer_period = 1000 * 60 * 2  # 2 * 60s
        self.__cfun_timer = osTimer()

        sys_bus.subscribe(CFUN_SWITCH_TOPIC, self.__cfun_switch_timer_handle)
        sys_bus.subscribe(NETWORK_EVENT_TOPIC, self.__network_event_handle)

    def enable(self):
        dataCall.setCallback(self.__network_event_callback)

    def __cfun_switch_timer_callback(self, args):
        print('cfun switch timer.')
        sys_bus.publish(CFUN_SWITCH_TOPIC, 0)

    def __cfun_switch_timer_handle(self, topic, msg):
        print('recv event form cfun_switch_timer.')
        net.setModemFun(0)
        utime.sleep(5)
        net.setModemFun(1)

    def __network_event_callback(self, args):
        print('The state of the network connection has changed.')
        sys_bus.publish(NETWORK_EVENT_TOPIC, args)

    def __network_event_handle(self, topic, msg):
        print('recv event form network_event_callback.')
        profile_id = msg[0]
        conn_state = msg[1]
        if conn_state == NetworkConnectState.DISCONNECT:
            print('The network connection has been disconnected.')
            print('start cfun_switch_timer.')
            self.__cfun_timer.start(self.timer_period, 1, self.__cfun_switch_timer_callback)
        elif conn_state == NetworkConnectState.CONNECT:
            print('The network connection has been connected.')
            self.__cfun_timer.stop()
        else:
            print('unknown state value:{}.'.format(conn_state))


def main():
    global network_monitor
    network_monitor = NetworkExceptionService()
    network_monitor.enable()


if __name__ == '__main__':
    main()