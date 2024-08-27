#BLE Client

import ble
import utime
import osTimer
import _thread
import checkNet
from queue import Queue


event_dict = {
    'BLE_START_STATUS_IND': 0,  # ble start
    'BLE_STOP_STATUS_IND': 1,   # ble stop
    'BLE_CONNECT_IND': 16,  # ble connect
    'BLE_DISCONNECT_IND': 17,   # ble disconnect
    'BLE_UPDATE_CONN_PARAM_IND': 18,    # ble update connection parameter
    'BLE_SCAN_REPORT_IND': 19,  # ble gatt client scan and report other devices
    'BLE_GATT_MTU': 20, # ble connection mtu
    'BLE_GATT_RECV_NOTIFICATION_IND': 23,   # client receive notification
    'BLE_GATT_RECV_INDICATION_IND': 24, # client receive indication
    'BLE_GATT_START_DISCOVER_SERVICE_IND': 26,  # start discover service
    'BLE_GATT_DISCOVER_SERVICE_IND': 27,    # discover service
    'BLE_GATT_DISCOVER_CHARACTERISTIC_DATA_IND': 28,    # discover characteristic
    'BLE_GATT_DISCOVER_CHARA_DESC_IND': 29, # discover characteristic descriptor
    'BLE_GATT_CHARA_WRITE_WITH_RSP_IND': 30,    # write characteristic value with response
    'BLE_GATT_CHARA_WRITE_WITHOUT_RSP_IND': 31, # write characteristic value without response
    'BLE_GATT_CHARA_READ_IND': 32,  # read characteristic value by handle
    'BLE_GATT_CHARA_READ_BY_UUID_IND': 33,  # read characteristic value by uuid
    'BLE_GATT_CHARA_MULTI_READ_IND': 34,    # read multiple characteristic value
    'BLE_GATT_DESC_WRITE_WITH_RSP_IND': 35, # write characteristic descriptor
    'BLE_GATT_DESC_READ_IND': 36,   # read characteristic descriptor
    'BLE_GATT_ATT_ERROR_IND': 37,   # attribute error
    'BLE_GATT_SMP_COMPLETE_IND': 63, # BLE smp complete
    'BLE_GATT_SMP_USER_CONFIRM_IND': 64, # BLE SMP confirm user passkey
}

gatt_status_dict = {
    'BLE_GATT_IDLE' : 0,
    'BLE_GATT_DISCOVER_SERVICE': 1,
    'BLE_GATT_DISCOVER_INCLUDES': 2,
    'BLE_GATT_DISCOVER_CHARACTERISTIC': 3,
    'BLE_GATT_WRITE_CHARA_VALUE': 4,
    'BLE_GATT_WRITE_CHARA_DESC': 5,
    'BLE_GATT_READ_CHARA_VALUE': 6,
    'BLE_GATT_READ_CHARA_DESC': 7,
}

pair_mode_dict = {
    'BLE_SMP_PAIR_FAIL': 0,  # pair fail
    'BLE_SMP_LEGACY_JUST_WORK': 1,   # No PIN code is required
    'BLE_SMP_LEGACY_PASSKEY_OUTPUT': 2,  # The PIN code is displayed, No PIN code is required
    'BLE_SMP_LEGACY_PASSKEY_INPUT': 3,   # A PIN code is required
    'BLE_SMP_LEGACY_OOB': 4,    # Using OOB
    'BLE_SMP_SECURE_JUST_WORK': 5,  # No PIN code is required
    'BLE_SMP_SECURE_NUMBER_COMPARISON': 6, # The PIN code is displayed, No PIN code is required
    'BLE_SMP_SECURE_PASSKEY_OUTPUT': 7, # The PIN code is displayed, No PIN code is required
    'BLE_SMP_SECURE_PASSKEY_INPUT': 8, # A PIN code is required
    'BLE_SMP_SECURE_OOB': 9,   # Using OOB
}

class EVENT(dict):
    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        raise ValueError("{} is read-only.".format(key))


class BleClient(object):
    def __init__(self):
        self.ble_server_name = 'QUEC HID'  # ble server name
        self.connect_id = 0
        self.connect_addr = 0
        self.gatt_statue = 0
        self.discover_service_mode = 0  # 0-discover all service, 1-discover service by uuid

        self.scan_param = {
            'scan_mode' : 1,
            'interval' : 0x100,
            'scan_window' : 0x50,
            'filter_policy' : 0,
            'local_addr_type' : 0,
        }

        self.scan_report_info = {
            'event_type' : 0,
            'name' : '',
            'addr_type' : 0,
            'addr' : 0,
            'rssi' : 0,
            'data_len' : 0,
            'raw_data' : 0,
        }

        self.target_service = {
            'start_handle' : 0,
            'end_handle' : 0,
            'uuid_type' : 1, # short uuid
            'short_uuid' : 0x180F, # Battery Service
            'long_uuid' : bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        }

        self.characteristic_list = []
        self.descriptor_list = []
        self.characteristic_count = 0
        self.chara_descriptor_count = 0
        self.characteristic_index = 0
        self.current_chara_index = 0
        self.current_desc_index = 0
        self.ble_short_uuid_pair_len = 7
        self.ble_long_uuid_pair_len = 21

        ret = ble.clientInit(self.ble_client_callback)
        if ret != 0:
            print('ble client initialize failed.')
            raise ValueError("BLE Client Init failed.")
        else:
            print('ble client initialize successful.')
        print('')

    @staticmethod
    def gatt_open():
        ret = ble.gattStart()
        if ret != 0:
            print('ble open failed.')
        else:
            print('ble open successful.')
        print('')
        return ret

    @staticmethod
    def gatt_close():
        print('ble close.')
        ret = ble.gattStop()
        if ret != 0:
            print('ble close failed.')
        else:
            print('ble close successful.')
        print('')
        ble.clientRelease()
        return ret

    @staticmethod
    def gatt_get_status():
        return ble.getStatus()

    @staticmethod
    def release():
        ret = ble.clientRelease()
        if ret != 0:
            print('ble client release failed.')
        else:
            print('ble client release successful.')
        print('')
        return ret

    def set_scan_param(self):
        scan_mode = self.scan_param['scan_mode']
        interval = self.scan_param['interval']
        scan_time = self.scan_param['scan_window']
        filter_policy = self.scan_param['filter_policy']
        local_addr_type = self.scan_param['local_addr_type']
        ret = ble.setScanParam(scan_mode, interval, scan_time, filter_policy, local_addr_type)
        if ret != 0:
            print('ble client set scan-parameters failed.')
        else:
            print('ble client set scan-parameters successful.')
        print('')
        return ret

    @staticmethod
    def start_scan():
        ret = ble.scanStart()
        if ret != 0:
            print('ble client scan failed.')
        else:
            print('ble client scan successful.')
        print('')
        return ret

    @staticmethod
    def stop_scan():
        ret = ble.scanStop()
        if ret != 0:
            print('ble client failed to stop scanning.')
        else:
            print('ble client scan stopped successfully.')
        print('')
        return ret

    def connect(self):
        print('start to connect.....')
        addr_type = self.scan_report_info['addr_type']
        addr = self.scan_report_info['addr']
        if addr != 0 and len(addr) == 6:
            addr_str = '{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}'.format(addr[0], addr[1], addr[2], addr[3], addr[4], addr[5])
            print('addr_type : {}, addr : {}'.format(addr_type, addr_str))
            ret = ble.connect(addr_type, addr)
            if ret != 0:
                print('ble client connect failed.')
            else:
                print('ble client connect successful.')
            print('')
            return ret

    def cancel_connect(self):
        ret = ble.cancelConnect(self.scan_report_info['addr'])
        if ret != 0:
            print('ble client cancel connect failed.')
        else:
            print('ble client cancel connect successful.')
        print('')
        return ret

    def disconnect(self):
        ret = ble.disconnect(self.connect_id)
        if ret != 0:
            print('ble client disconnect failed.')
        else:
            print('ble client disconnect successful.')
        print('')
        return ret

    def discover_all_service(self):
        # return 0
        ret = ble.discoverAllService(self.connect_id)
        if ret != 0:
            print('ble client discover all service failed.')
        else:
            print('ble client discover all service successful.')
        print('')
        return ret

    def discover_service_by_uuid(self):
        connect_id = self.connect_id
        uuid_type = self.target_service['uuid_type']
        short_uuid = self.target_service['short_uuid']
        long_uuid = self.target_service['long_uuid']
        ret = ble.discoverByUUID(connect_id, uuid_type, short_uuid, long_uuid)
        if ret != 0:
            print('ble client discover service by uuid failed.')
        else:
            print('ble client discover service by uuid successful.')
        print('')
        return ret

    def discover_all_includes(self):
        connect_id = self.connect_id
        start_handle = self.target_service['start_handle']
        end_handle = self.target_service['end_handle']
        ret = ble.discoverAllIncludes(connect_id, start_handle, end_handle)
        if ret != 0:
            print('ble client discover all includes failed.')
        else:
            print('ble client discover all includes successful.')
        print('')
        return ret

    def discover_all_characteristic(self):
        connect_id = self.connect_id
        start_handle = self.target_service['start_handle']
        end_handle = self.target_service['end_handle']
        ret = ble.discoverAllChara(connect_id, start_handle, end_handle)
        if ret != 0:
            print('ble client discover all characteristic failed.')
        else:
            print('ble client discover all characteristic successful.')
        print('')
        return ret

    def discover_all_characteristic_descriptor(self):
        connect_id = self.connect_id
        index = self.characteristic_index
        start_handle = self.characteristic_list[index]['value_handle'] + 1

        if self.characteristic_index == (self.characteristic_count - 1):
            end_handle = self.target_service['end_handle']
            print('[1]start_handle = {:#06x}, end_handle = {:#06x}'.format(start_handle - 1, end_handle))
            ret = ble.discoverAllCharaDesc(connect_id, start_handle, end_handle)
        else:
            end_handle = self.characteristic_list[index+1]['handle'] - 1
            print('[2]start_handle = {:#06x}, end_handle = {:#06x}'.format(start_handle - 1, end_handle))
            ret = ble.discoverAllCharaDesc(connect_id, start_handle, end_handle)
        self.characteristic_index += 1
        if ret != 0:
            print('ble client discover all characteristic descriptor failed.')
        else:
            print('ble client discover all characteristic descriptor successful.')
        print('')
        return ret

    def read_characteristic_by_uuid(self):
        connect_id = self.connect_id
        index = self.current_chara_index
        start_handle = self.characteristic_list[index]['handle']
        end_handle = self.characteristic_list[index]['value_handle']
        uuid_type = 1
        short_uuid = self.characteristic_list[index]['short_uuid']
        long_uuid = bytearray([0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])

        ret = ble.readCharaByUUID(connect_id, start_handle, end_handle, uuid_type, short_uuid, long_uuid)
        if ret != 0:
            print('ble client read characteristic by uuid failed.')
        else:
            print('ble client read characteristic by uuid successful.')
        print('')
        return ret

    def read_characteristic_by_handle(self):
        connect_id = self.connect_id
        index = self.current_chara_index
        handle = self.characteristic_list[index]['value_handle']
        offset = 0
        is_long = 0

        ret = ble.readCharaByHandle(connect_id, handle, offset, is_long)
        if ret != 0:
            print('ble client read characteristic by handle failed.')
        else:
            print('ble client read characteristic by handle successful.')
        print('')
        return ret

    def read_characteristic_descriptor(self):
        connect_id = self.connect_id
        index = self.current_desc_index
        handle = self.descriptor_list[index]['handle']
        print('handle = {:#06x}'.format(handle))
        is_long = 0
        ret = ble.readCharaDesc(connect_id, handle, is_long)
        if ret != 0:
            print('ble client read characteristic descriptor failed.')
        else:
            print('ble client read characteristic descriptor successful.')
        print('')
        return ret

    def write_characteristic(self):
        connect_id = self.connect_id
        index = self.current_chara_index
        handle = self.characteristic_list[index]['value_handle']
        offset = 0
        is_long = 0
        data = bytearray([0x40, 0x00])
        print('value_handle = {:#06x}, uuid = {:#06x}'.format(handle, self.characteristic_list[index]['short_uuid']))
        ret = ble.writeChara(connect_id, handle, offset, is_long, data)
        if ret != 0:
            print('ble client write characteristic failed.')
        else:
            print('ble client read characteristic successful.')
        print('')
        return ret

    def write_characteristic_no_rsp(self):
        connect_id = self.connect_id
        index = self.current_chara_index
        handle = self.characteristic_list[index]['value_handle']
        data = bytearray([0x20, 0x00])
        print('value_handle = {:#06x}, uuid = {:#06x}'.format(handle, self.characteristic_list[index]['short_uuid']))
        ret = ble.writeCharaNoRsp(connect_id, handle, data)
        if ret != 0:
            print('ble client write characteristic no rsp failed.')
        else:
            print('ble client read characteristic no rsp successful.')
        print('')
        return ret

    def write_characteristic_descriptor(self):
        connect_id = self.connect_id
        index = self.current_desc_index
        handle = self.descriptor_list[index]['handle']
        data = bytearray([0x01, 0x02])
        print('handle = {:#06x}'.format(handle))

        ret = ble.writeCharaDesc(connect_id, handle, data)
        if ret != 0:
            print('ble client write characteristic descriptor failed.')
        else:
            print('ble client read characteristic descriptor successful.')
        print('')
        return ret

    @staticmethod
    def ble_client_callback(args):
        global msg_queue
        msg_queue.put(args)


pair_timer = osTimer()
pair_timer_status = 0  # 0-not running, 1-running


def pair_timer_callback(args):
    global pair_timer_status
    print('[pair timer cb]ble smp start pair...')
    pair_timer_status = 0
    ret = ble.smpStartPair(ble_client.connect_id)
    if ret != 0:
        print('smpStartPair execution failed.')


def ble_gatt_client_event_handler():
    global msg_queue
    global pair_timer
    global pair_timer_status
    old_time = 0

    while True:
        cur_time = utime.localtime()
        timestamp = "{:02d}:{:02d}:{:02d}".format(cur_time[3], cur_time[4], cur_time[5])
        if cur_time[5] != old_time and cur_time[5] % 5 == 0:
            old_time = cur_time[5]
            print('[{}]event handler running.....'.format(timestamp))
            print('')
        msg = msg_queue.get()
        # print('msg : {}'.format(msg))
        event_id = msg[0]
        status = msg[1]

        if event_id == event.BLE_START_STATUS_IND:
            print('')
            print('event_id : BLE_START_STATUS_IND, status = {}'.format(status))
            if status == 0:
                print('BLE start successful.')
                ble_status = ble_client.gatt_get_status()
                if ble_status == 0:
                    print('BLE Status : stopped.')
                    break
                elif ble_status == 1:
                    print('BLE Status : started.')
                else:
                    print('get ble status error.')
                    ble_client.gatt_close()
                    break

                print('ble smp set config: I/O capability input and output, MITM, Secure Connections Pairing')
                ret = ble.smpSetConfig(4, 13, 123456, 600)
                if ret != 0:
                    print('[callback] ble smp set config failed!')
                print('')
                current_smp_config = ble.smpGetConfig()
                if current_smp_config != -1:
                    print('=====================================')
                    print('ble client current smp config:{}'.format(current_smp_config))
                    print('i/o capability: {}'.format(current_smp_config[0]))
                    print('authentication requirements: {}'.format(current_smp_config[1]))
                    print('passkey: {}'.format(current_smp_config[2]))
                    print('timeout: {}'.format(current_smp_config[3]))
                    print('=====================================')
                else:
                    print('get current smp configuration failed.')

                ret = ble_client.set_scan_param()
                if ret != 0:
                    ble_client.gatt_close()
                    break
                ret = ble_client.start_scan()
                if ret != 0:
                    ble_client.gatt_close()
                    break
            else:
                print('BLE start failed.')
                break
        elif event_id == event.BLE_STOP_STATUS_IND:
            print('')
            print('event_id : BLE_STOP_STATUS_IND, status = {}'.format(status))
            if status == 0:
                print('ble stop successful.')
            else:
                print('ble stop failed.')
                break
        elif event_id == event.BLE_CONNECT_IND:
            print('')
            print('event_id : BLE_CONNECT_IND, status = {}'.format(status))
            if status == 0:
                ble_client.connect_id = msg[2]
                ble_client.connect_addr = msg[3]
                addr = ble_client.connect_addr
                addr_str = '{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}'.format(addr[0], addr[1], addr[2], addr[3], addr[4], addr[5])
                print('connect_id : {:#x}, connect_addr : {}'.format(ble_client.connect_id, addr_str))

                pair_device_infos = ble.smpGetPairedDevInfo()
                pair_device_nums = 0
                if pair_device_infos != -1:
                    pair_device_nums = len(pair_device_infos)
                if pair_device_nums == 0:
                    print('[1]First pairing, ble smp start pair...')
                    ret = ble.smpStartPair(ble_client.connect_id)
                    if ret != 0:
                        print('smpStartPair execution failed.')
                else:
                    print('paired list({}):'.format(pair_device_nums))
                    i = 0
                    for dev_addr in pair_device_infos:
                        i += 1
                        dev_addr_str = '{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}'.format(dev_addr[0], dev_addr[1], dev_addr[2], dev_addr[3], dev_addr[4], dev_addr[5])
                        print("device{} mac:{}".format(i, dev_addr_str))

                    if addr in pair_device_infos:
                        print('Wait for automatic pairing, timeout is 1200ms.')
                        pair_timer.start(1200, 0, pair_timer_callback)
                        pair_timer_status = 1
                    else:
                        print('[2]First pairing, ble smp start pair...')
                        ret = ble.smpStartPair(ble_client.connect_id)
                        if ret != 0:
                            print('smpStartPair execution failed.')

            else:
                print('ble connect failed.')
                break
        elif event_id == event.BLE_DISCONNECT_IND:
            print('')
            print('event_id : BLE_DISCONNECT_IND, status = {}'.format(status))
            if status == 0:
                ble_client.connect_id = msg[2]
                ble_client.connect_addr = msg[3]
                addr = ble_client.connect_addr
                addr_str = '{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}'.format(addr[0], addr[1], addr[2], addr[3], addr[4], addr[5])
                print('connect_id : {:#x}, connect_addr : {}'.format(ble_client.connect_id, addr_str))
            else:
                print('ble disconnect failed.')
            ble_client.gatt_close()
            break
        elif event_id == event.BLE_UPDATE_CONN_PARAM_IND:
            print('')
            print('event_id : BLE_UPDATE_CONN_PARAM_IND, status = {}'.format(status))
            if status == 0:
                connect_id = msg[2]
                max_interval = msg[3]
                min_interval = msg[4]
                latency = msg[5]
                timeout = msg[6]
                print('connect_id={},max_interval={},min_interval={},latency={},timeout={}'.format(connect_id,max_interval,min_interval,latency,timeout))
            else:
                print('ble update parameter failed.')
                ble_client.gatt_close()
                break
        elif event_id == event.BLE_SCAN_REPORT_IND:
            if status == 0:
                # print(' ble scan successful.')

                ble_client.scan_report_info['event_type'] = msg[2]
                ble_client.scan_report_info['name'] = msg[3]
                ble_client.scan_report_info['addr_type'] = msg[4]
                ble_client.scan_report_info['addr'] = msg[5]
                ble_client.scan_report_info['rssi'] = msg[6]
                ble_client.scan_report_info['data_len'] = msg[7]
                ble_client.scan_report_info['raw_data'] = msg[8]

                device_name = ble_client.scan_report_info['name']
                addr = ble_client.scan_report_info['addr']
                rssi = ble_client.scan_report_info['rssi']
                addr_type = ble_client.scan_report_info['addr_type']
                addr_str = '{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}'.format(addr[0], addr[1], addr[2], addr[3], addr[4], addr[5])
                if device_name != '' and rssi != 0:
                    print('name: {}, addr: {}, rssi: {}, addr_type: {}'.format(device_name, addr_str, rssi, addr_type))
                    print('raw_data: {}'.format(ble_client.scan_report_info['raw_data']))

                if device_name == ble_client.ble_server_name:  # Stop scanning once the target device is scanned
                    print('Discover target device:{}'.format(ble_client.ble_server_name))
                    print('ready to stop scan.')
                    ret = ble_client.stop_scan()
                    if ret != 0:
                        ble_client.gatt_close()
                        break

                    ret = ble_client.connect()
                    if ret != 0:
                        ble_client.gatt_close()
                        break
            else:
                print('ble scan failed.')
                ret = ble_client.stop_scan()
                if ret != 0:
                    ble_client.gatt_close()
                    break
        elif event_id == event.BLE_GATT_MTU:
            print('')
            print('event_id : BLE_GATT_MTU, status = {}'.format(status))
            if status == 0:
                handle = msg[2]
                ble_mtu = msg[3]
                print('handle = {:#06x}, ble_mtu = {}'.format(handle, ble_mtu))
            else:
                print('ble connect mtu failed.')
                ble_client.gatt_close()
                break
        elif event_id == event.BLE_GATT_RECV_NOTIFICATION_IND:
            print('')
            print('event_id : BLE_GATT_RECV_NOTIFICATION_IND, status = {}'.format(status))
            if status == 0:
                data_len = msg[2]
                data = msg[3]
                print('len={}, data:{}'.format(data_len, data))
                handle = (data[1] << 8) | data[0]
                print('handle = {:#06x}'.format(handle))
            else:
                print('ble receive notification failed.')
                break
        elif event_id == event.BLE_GATT_RECV_INDICATION_IND:
            print('')
            print('event_id : BLE_GATT_RECV_INDICATION_IND, status = {}'.format(status))
            if status == 0:
                data_len = msg[2]
                data = msg[3]
                print('len={}, data:{}'.format(data_len, data))
            else:
                print('ble receive indication failed.')
                break
        elif event_id == event.BLE_GATT_START_DISCOVER_SERVICE_IND:
            print('')
            print('event_id : BLE_GATT_START_DISCOVER_SERVICE_IND, status = {}'.format(status))
            if status == 0:
                ble_client.characteristic_count = 0
                ble_client.chara_descriptor_count = 0
                ble_client.characteristic_index = 0
                ble_client.gatt_statue = gatt_status.BLE_GATT_DISCOVER_SERVICE
                '''
                For scenarios that do not require pairing function (or do not support pairing), 
				after receiving the BLE_GATT_START_DISCOVER_SERVICE_IND event, you can perform 
				operations such as discovering services; for scenarios that support pairing and 
				require pairing, since the pairing process needs to be performed first after 
				establishing a connection, you need Wait for the pairing process to end before 
				performing operations such as discovering the service. When the pairing is completed, 
				the BLE_GATT_SMP_COMPLETE_IND event will be received.
                '''
                # if ble_client.discover_service_mode == 0:
                #     print('execute the function discover_all_service.')
                #     ret = ble_client.discover_all_service()
                # else:
                #     print('execute the function discover_service_by_uuid.')
                #     ret = ble_client.discover_service_by_uuid()
                # if ret != 0:
                #     print('Execution result: Failed.')
                #     ble_client.gatt_close()
                #     break
        elif event_id == event.BLE_GATT_DISCOVER_SERVICE_IND:
            print('')
            print('event_id : BLE_GATT_DISCOVER_SERVICE_IND, status = {}'.format(status))
            if status == 0:
                start_handle = msg[2]
                end_handle = msg[3]
                short_uuid = msg[4]
                print('start_handle = {:#06x}, end_handle = {:#06x}, short_uuid = {:#06x}'.format(start_handle, end_handle, short_uuid))
                if ble_client.discover_service_mode == 0: # discover service all
                    if ble_client.target_service['short_uuid'] == short_uuid: 
                        ble_client.target_service['start_handle'] = start_handle
                        ble_client.target_service['end_handle'] = end_handle
                        ble_client.gatt_statue = gatt_status.BLE_GATT_DISCOVER_CHARACTERISTIC
                        print('execute the function discover_all_characteristic.')
                        ret = ble_client.discover_all_characteristic()
                        if ret != 0:
                            print('Execution result: Failed.')
                            ble_client.gatt_close()
                            break
                else:
                    ble_client.target_service['start_handle'] = start_handle
                    ble_client.target_service['end_handle'] = end_handle
                    ble_client.gatt_statue = gatt_status.BLE_GATT_DISCOVER_CHARACTERISTIC
                    print('execute the function discover_all_characteristic.')
                    ret = ble_client.discover_all_characteristic()
                    if ret != 0:
                        print('Execution result: Failed.')
                        ble_client.gatt_close()
                        break
            else:
                print('ble discover service failed.')
                ble_client.gatt_close()
                break
        elif event_id == event.BLE_GATT_DISCOVER_CHARACTERISTIC_DATA_IND:
            print('')
            print('event_id : BLE_GATT_DISCOVER_CHARACTERISTIC_DATA_IND, status = {}'.format(status))
            if status == 0:
                data_len = msg[2]
                data = msg[3]
                pair_len = data[0]
                print('pair_len={}, len={}, data:{}'.format(pair_len, data_len, data))
                if data_len > 0:
                    if ble_client.gatt_statue == gatt_status.BLE_GATT_DISCOVER_CHARACTERISTIC:
                        i = 0
                        while i < (data_len - 1) / pair_len:
                            chara_dict = {
                                'handle': (data[i * pair_len + 2] << 8) | data[i * pair_len + 1],
                                'properties': data[i * pair_len + 3],
                                'value_handle': (data[i * pair_len + 5] << 8) | data[i * pair_len + 4],
                                'uuid_type': 0,
                                'short_uuid': 0x0000,
                                'long_uuid': bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
                            }
                            print('handle={:#06x}, properties={:#x}, value_handle={:#06x}'.format(chara_dict['handle'], chara_dict['properties'], chara_dict['value_handle']))
                            if pair_len == ble_client.ble_short_uuid_pair_len:
                                chara_dict['uuid_type'] = 1
                                chara_dict['short_uuid'] = (data[i * pair_len + 7] << 8) | data[i * pair_len + 6]
                                print('short_uuid:{:#06x}'.format(chara_dict['short_uuid']))
                            elif pair_len == ble_client.ble_long_uuid_pair_len:
                                start_index = i * pair_len + 6
                                end_index = start_index + 16
                                chara_dict['uuid_type'] = 0
                                chara_dict['long_uuid'] = data[start_index : end_index]
                                print('long_uuid:{}'.format(chara_dict['long_uuid']))
                            i += 1
                            if ble_client.characteristic_count < 5:
                                ble_client.characteristic_list.append(chara_dict)
                                ble_client.characteristic_count = len(ble_client.characteristic_list)
                            print('characteristic_list len = {}'.format(ble_client.characteristic_count))
                    elif ble_client.gatt_statue == gatt_status.BLE_GATT_READ_CHARA_VALUE:
                        print('data_len = {}'.format(data_len))
                        print('pay_load = {:02x},{:02x},{:02x},{:02x}'.format(data[0], data[1], data[2], data[3]))
            else:
                print('ble discover characteristic failed.')
                ble_client.gatt_close()
                break
        elif event_id == event.BLE_GATT_DISCOVER_CHARA_DESC_IND:
            print('')
            print('event_id : BLE_GATT_DISCOVER_CHARA_DESC_IND, status = {}'.format(status))
            if status == 0:
                data_len = msg[2]
                data = msg[3]
                fmt = data[0]
                print('fmt={}, len={}, data:{}'.format(fmt, data_len, data))
                if data_len > 0:
                    i = 0
                    if fmt == 1:  # 16 bit uuid
                        while i < (data_len - 1) / 4:
                            descriptor_dict = {
                                'handle': (data[i * 4 + 2] << 8) | data[i * 4 + 1],
                                'short_uuid': (data[i * 4 + 4] << 8) | data[i * 4 + 3],
                            }
                            print('handle={:#06x}, uuid={:#06x}'.format(descriptor_dict['handle'], descriptor_dict['short_uuid']))
                            i += 1
                            if ble_client.chara_descriptor_count < 5:
                                ble_client.descriptor_list.append(descriptor_dict)
                                ble_client.chara_descriptor_count = len(ble_client.descriptor_list)
                            print('descriptor_list len = {}'.format(ble_client.chara_descriptor_count))
                if ble_client.characteristic_index == ble_client.characteristic_count:
                    print('execute the function read_characteristic_by_uuid.')
                    # ble_client.gatt_statue = gatt_status.BLE_GATT_WRITE_CHARA_VALUE
                    # ret = ble_client.write_characteristic()
                    # ret = ble_client.write_characteristic_no_rsp()

                    ble_client.gatt_statue = gatt_status.BLE_GATT_READ_CHARA_VALUE
                    ret = ble_client.read_characteristic_by_uuid()
                    # ret = ble_client.read_characteristic_by_handle()

                    # ble_client.gatt_statue = gatt_status.BLE_GATT_READ_CHARA_DESC
                    # ret = ble_client.read_characteristic_descriptor()

                    # ble_client.gatt_statue = gatt_status.BLE_GATT_WRITE_CHARA_DESC
                    # ret = ble_client.write_characteristic_descriptor()
                else:
                    print('execute the function discover_all_characteristic_descriptor.')
                    ret = ble_client.discover_all_characteristic_descriptor()
                if ret != 0:
                    print('Execution result: Failed.')
                    ble_client.gatt_close()
                    break
            else:
                print('ble discover characteristic descriptor failed.')
                ble_client.gatt_close()
                break
        elif event_id == event.BLE_GATT_CHARA_WRITE_WITH_RSP_IND:
            print('')
            print('event_id : BLE_GATT_CHARA_WRITE_WITH_RSP_IND, status = {}'.format(status))
            if status == 0:
                if ble_client.gatt_statue == gatt_status.BLE_GATT_WRITE_CHARA_VALUE:
                    pass
                elif ble_client.gatt_statue == gatt_status.BLE_GATT_WRITE_CHARA_DESC:
                    pass
            else:
                print('ble write characteristic with response failed.')
                break
        elif event_id == event.BLE_GATT_CHARA_WRITE_WITHOUT_RSP_IND:
            print('')
            print('event_id : BLE_GATT_CHARA_WRITE_WITHOUT_RSP_IND, status = {}'.format(status))
            if status == 0:
                print('write characteristic value without response successful.')
            else:
                print('write characteristic value without response failed.')
                break
        elif event_id == event.BLE_GATT_CHARA_READ_IND:
            print('')
            # read characteristic value by handle
            print('event_id : BLE_GATT_CHARA_READ_IND, status = {}'.format(status))
            if status == 0:
                data_len = msg[2]
                data = msg[3]
                print('data_len = {}, data : {}'.format(data_len, data))
                if ble_client.gatt_statue == gatt_status.BLE_GATT_READ_CHARA_VALUE:
                    # print('read characteristic value by handle.')
                    pass
            else:
                print('ble read characteristic failed.')
                break
        elif event_id == event.BLE_GATT_CHARA_READ_BY_UUID_IND:
            print('')
            # read characteristic value by uuid
            print('event_id : BLE_GATT_CHARA_READ_BY_UUID_IND, status = {}'.format(status))
            if status == 0:
                data_len = msg[2]
                data = msg[3]
                print('data_len = {}, data : {}'.format(data_len, data))
                handle = (data[2] << 8) | data[1]
                print('handle = {:#06x}'.format(handle))
            else:
                print('ble read characteristic by uuid failed.')
                break
        elif event_id == event.BLE_GATT_CHARA_MULTI_READ_IND:
            print('')
            # read multiple characteristic value
            print('event_id : BLE_GATT_CHARA_MULTI_READ_IND, status = {}'.format(status))
            if status == 0:
                data_len = msg[2]
                data = msg[3]
                print('data_len = {}, data : {}'.format(data_len, data))
            else:
                print('ble read multiple characteristic by uuid failed.')
                break
        elif event_id == event.BLE_GATT_DESC_WRITE_WITH_RSP_IND:
            print('')
            print('event_id : BLE_GATT_DESC_WRITE_WITH_RSP_IND, status = {}'.format(status))
            if status == 0:
                if ble_client.gatt_statue == gatt_status.BLE_GATT_WRITE_CHARA_VALUE:
                    pass
                elif ble_client.gatt_statue == gatt_status.BLE_GATT_WRITE_CHARA_DESC:
                    pass
            else:
                print('ble write characteristic descriptor failed.')
                break
        elif event_id == event.BLE_GATT_DESC_READ_IND:
            print('')
            # read characteristic descriptor
            print('event_id : BLE_GATT_DESC_READ_IND, status = {}'.format(status))
            if status == 0:
                data_len = msg[2]
                data = msg[3]
                print('data_len = {}, data : {}'.format(data_len, data))
                if ble_client.gatt_statue == gatt_status.BLE_GATT_READ_CHARA_DESC:
                    # print('read characteristic descriptor.')
                    pass
            else:
                print('ble read characteristic descriptor failed.')
                break
        elif event_id == event.BLE_GATT_ATT_ERROR_IND:
            print('')
            print('event_id : BLE_GATT_ATT_ERROR_IND, status = {}'.format(status))
            if status == 0:
                errcode = msg[2]
                print('errcode = {:#06x}'.format(errcode))
                if ble_client.gatt_statue == gatt_status.BLE_GATT_DISCOVER_INCLUDES:
                    ble_client.gatt_statue = gatt_status.BLE_GATT_DISCOVER_CHARACTERISTIC
                    print('execute the function discover_all_characteristic.')
                    ret = ble_client.discover_all_characteristic()
                    if ret != 0:
                        print('Execution result: Failed.')
                        ble_client.gatt_close()
                        break
                elif ble_client.gatt_statue == gatt_status.BLE_GATT_DISCOVER_CHARACTERISTIC:
                    ble_client.gatt_statue = gatt_status.BLE_GATT_IDLE
                    print('execute the function discover_all_characteristic_descriptor.')
                    ret = ble_client.discover_all_characteristic_descriptor()
                    if ret != 0:
                        print('Execution result: Failed.')
                        ble_client.gatt_close()
                        break
                elif ble_client.gatt_statue == gatt_status.BLE_GATT_IDLE:
                    print('Send exchange MTU Request, MTU 247')
                    ble.exchangeMtu(ble_client.connect_id, 247)
            else:
                print('ble attribute error.')
                ble_client.gatt_close()
                break
        elif event_id == event.BLE_GATT_SMP_COMPLETE_IND:
            print('')
            print('event_id : BLE_GATT_SMP_COMPLETE_IND, status = {}'.format(status))
            if status == 0:
                print('[callback] ble smp pairing complete.')
                if pair_timer_status == 1:
                    print('stop pair timer.')
                    pair_timer.stop()
                    pair_timer_status = 0
                pair_timer.delete_timer()
                if ble_client.gatt_statue == gatt_status.BLE_GATT_DISCOVER_SERVICE:
                    if ble_client.discover_service_mode == 0:
                        print('execute the function discover_all_service.')
                        ret = ble_client.discover_all_service()
                    else:
                        print('execute the function discover_service_by_uuid.')
                        ret = ble_client.discover_service_by_uuid()
                    if ret != 0:
                        print('Execution result: Failed.')
                        ble_client.gatt_close()
                        break
            else:
                print('[callback] ble smp pairing fail.')
        elif event_id == event.BLE_GATT_SMP_USER_CONFIRM_IND:
            print('')
            print('event_id : BLE_GATT_SMP_USER_CONFIRM_IND, status = {}'.format(status))
            if status == 0:
                print('[callback] ble smp user confirm indication.')
                connect_id = msg[2]
                pair_mode = msg[3]
                pin_code = msg[4]
                print('connect_id = {:#06x}'.format(connect_id))
                print('pair_mode = {:#06x}'.format(pair_mode))
                print('pin_code = {}'.format(pin_code))

                if pair_mode == pair.BLE_SMP_PAIR_FAIL or pair_mode == pair.BLE_SMP_LEGACY_OOB or pair_mode == pair.BLE_SMP_SECURE_OOB:
                    # Not support OOB
                    print('[callback] ble smp No operation is required')
                elif pair_mode == pair.BLE_SMP_LEGACY_JUST_WORK or pair_mode == pair.BLE_SMP_SECURE_JUST_WORK or pair_mode == pair.BLE_SMP_SECURE_NUMBER_COMPARISON:
                    print('[callback] ble smp Confirm pairing, No PIN code is required')
                    print('[callback] ble client will execute \'ble.smpUserConfirm(connect_id, 1, 0)\' to Confirm pairing')
                    ble.smpUserConfirm(connect_id, 1, 0)
                    # If you want to cancel pairing, you can use the 'ble.smpUserConfirm(connect_id,0,0)'
                elif pair_mode == pair.BLE_SMP_LEGACY_PASSKEY_OUTPUT or pair_mode == pair.BLE_SMP_SECURE_PASSKEY_OUTPUT:
                    print('[callback] ble client smp The PIN code is displayed, wait peer device enters PIN code.')
                    # If you want to cancel pairing, you can use the 'ble.smpUserConfirm(connect_id,0,0)'
                elif pair_mode == pair.BLE_SMP_LEGACY_PASSKEY_INPUT or pair_mode == pair.BLE_SMP_SECURE_PASSKEY_INPUT:
                    print('[callback] ble smp Confirm pairing, Please enter the PIN code displayed by peer device!!!')
                    print('>>> ble.smpUserConfirm(connect_id, 2, xxxxxx)')
                    # If you want to cancel pairing, you can use the 'ble.smpUserConfirm(connect_id,0,0)'
            else:
                print('[callback] ble smp user confirm indication fail.')
        else:
            print('unknown event id : {}.'.format(event_id))

    # ble_client.release()


event = EVENT(event_dict)
pair = EVENT(pair_mode_dict)
gatt_status = EVENT(gatt_status_dict)
msg_queue = Queue(50)
ble_client = BleClient()


def main():
    print('create client event handler task.')
    _thread.start_new_thread(ble_gatt_client_event_handler, ())
    # ble.setScanFilter(0)
    ret = ble_client.gatt_open()
    if ret != 0:
        return -1

    # count = 0
    # while True:
    #     utime.sleep(1)
    #     count += 1
    #     cur_time = utime.localtime()
    #     timestamp = "{:02d}:{:02d}:{:02d}".format(cur_time[3], cur_time[4], cur_time[5])
    #     if count % 5 == 0:
    #         print('[{}] BLE Client running, count = {}......'.format(timestamp, count))
    #         print('')
    #     if count > 130: #
    #         count = 0
    #         print('!!!!! stop BLE Client now !!!!!')
    #         ble_status = ble_client.gatt_get_status()
    #         if ble_status == 1:
    #             ble_client.gatt_close()
    #         break
    #     else:
    #         ble_status = ble_client.gatt_get_status()
    #         if ble_status == 0: # stopped
    #             print('BLE connection has been disconnected.')
    #             break

if __name__ == '__main__':
    main()
