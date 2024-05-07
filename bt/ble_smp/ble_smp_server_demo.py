# -*- coding: UTF-8 -*-

import ble
import utime


BLE_GATT_SYS_SERVICE = 0  # 0-Delete the default GAP and GATT servers  1-Retain the default GAP and GATT services
BLE_SERVER_HANDLE = 0
_BLE_NAME = "QUEC HID"


event_dict = {
    'BLE_START_STATUS_IND': 0,  # ble start
    'BLE_STOP_STATUS_IND': 1,   # ble stop
    'BLE_CONNECT_IND': 16,  # ble connect
    'BLE_DISCONNECT_IND': 17,   # ble disconnect
    'BLE_UPDATE_CONN_PARAM_IND': 18,    # ble update connection parameter
    'BLE_SCAN_REPORT_IND': 19,  # ble gatt client scan and report other devices
    'BLE_GATT_MTU': 20, # ble connection mtu
    'BLE_GATT_RECV_WRITE_IND': 21, # when ble client write characteristic value or descriptor,server get the notice
    'BLE_GATT_RECV_READ_IND': 22, # when ble client read characteristic value or descriptor,server get the notice
    'BLE_GATT_RECV_NOTIFICATION_IND': 23,   # client receive notification
    'BLE_GATT_RECV_INDICATION_IND': 24, # client receive indication
    'BLE_GATT_SEND_END': 25, # server send notification,and receive send end notice
    'BLE_GATT_SMP_COMPLETE_IND': 63, # BLE smp complete
    'BLE_GATT_SMP_USER_CONFIRM_IND': 64, # BLE SMP confirm user passkey
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


event = EVENT(event_dict)
pair = EVENT(pair_mode_dict)


def ble_callback(args):
    global BLE_GATT_SYS_SERVICE
    global BLE_SERVER_HANDLE
    event_id = args[0]
    status = args[1]
    # print('[ble_callback]: event_id={}, status={}'.format(event_id, status))

    if event_id == event.BLE_START_STATUS_IND:  # ble start
        print('[ble_callback]event_id: BLE_START_STATUS_IND')
        if status == 0:
            print('[callback] BLE start success.')
            mac = ble.getPublicAddr()
            if mac != -1 and len(mac) == 6:
                addr = '{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}'.format(mac[5], mac[4], mac[3], mac[2], mac[1], mac[0])
                print('BLE public addr : {}'.format(addr))
            ret = ble_gatt_set_name()
            if ret != 0:
                ble_gatt_close()
                return
            ret = ble_gatt_set_param()
            if ret != 0:
                ble_gatt_close()
                return
            ret = ble_gatt_set_data()
            if ret != 0:
                ble_gatt_close()
                return
            ret = ble_gatt_set_rsp_data()
            if ret != 0:
                ble_gatt_close()
                return
            ret = ble_gatt_add_service()
            if ret != 0:
                ble_gatt_close()
                return
            ret = ble_gatt_add_characteristic()
            if ret != 0:
                ble_gatt_close()
                return
            ret = ble_gatt_add_characteristic_value()
            if ret != 0:
                ble_gatt_close()
                return
            ret = ble_gatt_add_characteristic_desc()
            if ret != 0:
                ble_gatt_close()
                return
            ret = ble_gatt_add_service_complete()
            if ret != 0:
                ble_gatt_close()
                return
            if BLE_GATT_SYS_SERVICE == 0:
                BLE_SERVER_HANDLE = 1
            else:
                BLE_SERVER_HANDLE = 16
            ret = ble_adv_start()
            if ret != 0:
                ble_gatt_close()
                return
        else:
            print('[callback] BLE start failed.')
    elif event_id == event.BLE_STOP_STATUS_IND:  # ble stop
        print('[ble_callback]event_id: BLE_STOP_STATUS_IND')
        if status == 0:
            print('[callback] ble stop successful.')
            ble_status = ble.getStatus()
            print('ble status is {}'.format(ble_status))
            ble_gatt_server_release()
        else:
            print('[callback] ble stop failed.')
    elif event_id == event.BLE_CONNECT_IND:  # ble connect
        print('[ble_callback]event_id: BLE_CONNECT_IND')
        if status == 0:
            print('[callback] ble connect successful.')
            connect_id = args[2]
            addr = args[3]
            addr_str = '{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}'.format(addr[0], addr[1], addr[2], addr[3], addr[4], addr[5])
            print('[callback] connect_id = {}, addr = {}'.format(connect_id, addr_str))

            print('[callback] ble smp set config:')
            print('ble smp set config: I/O capability input and output, Secure Connections Pairing')
            ret = ble.smpSetConfig(4, 9, 123456, 600) #I/O capability input and output, Secure Connections Pairing
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

            # print('[callback] ble smp start pair...')
            # ret = ble.smpStartPair(connect_id)
            # if ret != 0:
            #     print('[callback] ble smp start pair failed!')
        else:
            print('[callback] ble connect failed.')
    elif event_id == event.BLE_DISCONNECT_IND:  # ble disconnect
        print('[ble_callback]event_id: BLE_DISCONNECT_IND')
        if status == 0:
            print('[callback] ble disconnect successful.')
            connect_id = args[2]
            addr = args[3]
            addr_str = '{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}'.format(addr[0], addr[1], addr[2], addr[3], addr[4], addr[5])
            ble_gatt_close()
            print('[callback] connect_id = {}, addr = {}'.format(connect_id, addr_str))
        else:
            print('[callback] ble disconnect failed.')
            ble_gatt_close()
            return
    elif event_id == event.BLE_UPDATE_CONN_PARAM_IND:  # ble update connection parameter
        print('[ble_callback]event_id: BLE_UPDATE_CONN_PARAM_IND')
        if status == 0:
            print('[callback] ble update parameter successful.')
            connect_id = args[2]
            max_interval = args[3]
            min_interval = args[4]
            latency = args[5]
            timeout = args[6]
            print('[callback] connect_id={},max_interval={},min_interval={},latency={},timeout={}'.format(connect_id, max_interval, min_interval, latency, timeout))
        else:
            print('[callback] ble update parameter failed.')
            ble_gatt_close()
            return
    elif event_id == event.BLE_GATT_MTU:  # ble connection mtu
        print('[ble_callback]event_id: BLE_GATT_MTU')
        if status == 0:
            print('[callback] ble connect mtu successful.')
            handle = args[2]
            ble_mtu = args[3]
            print('[callback] handle = {:#06x}, ble_mtu = {}'.format(handle, ble_mtu))
        else:
            print('[callback] ble connect mtu failed.')
            ble_gatt_close()
            return
    elif event_id == event.BLE_GATT_RECV_WRITE_IND:
        print('[ble_callback]event_id: BLE_GATT_RECV_WRITE_IND')
        if status == 0:
            print('[callback] ble recv successful.')
            data_len = args[2]
            data = args[3]  # This is a bytearray
            attr_handle = args[4]
            short_uuid = args[5]
            long_uuid = args[6]  # This is a bytearray
            print('len={}, data:{}'.format(data_len, data))
            print('attr_handle = {:#06x}'.format(attr_handle))
            print('short uuid = {:#06x}'.format(short_uuid))
            print('long uuid = {}'.format(long_uuid))
        else:
            print('[callback] ble recv failed.')
            ble_gatt_close()
            return
    elif event_id == event.BLE_GATT_RECV_READ_IND:
        print('[ble_callback]event_id: BLE_GATT_RECV_READ_IND')
        if status == 0:
            print('[callback] ble recv read successful.')
            data_len = args[2]
            data = args[3]  # This is a bytearray
            attr_handle = args[4]
            short_uuid = args[5]
            long_uuid = args[6]  # This is a bytearray
            print('len={}, data:{}'.format(data_len, data))
            print('attr_handle = {:#06x}'.format(attr_handle))
            print('short uuid = {:#06x}'.format(short_uuid))
            print('long uuid = {}'.format(long_uuid))
        else:
            print('[callback] ble recv read failed.')
            ble_gatt_close()
            return
    elif event_id == event.BLE_GATT_SMP_COMPLETE_IND:
        print('[ble_callback]event_id: BLE_GATT_SMP_COMPLETE_IND')
        if status == 0:
            print('[callback] ble smp pairing complete.')
        else:
            print('[callback] ble smp pairing fail.')
    elif event_id == event.BLE_GATT_SMP_USER_CONFIRM_IND:
        print('[ble_callback]event_id: BLE_GATT_SMP_USER_CONFIRM_IND')
        if status == 0:
            print('[callback] ble smp user confirm indication.')
            connect_id = args[2]
            pair_mode = args[3]
            pin_code = args[4]
            print('connect_id = {:#06x}'.format(connect_id))
            print('pair_mode = {:#06x}'.format(pair_mode))
            print('pin_code = {}'.format(pin_code))

            if pair_mode == pair.BLE_SMP_PAIR_FAIL or pair_mode == pair.BLE_SMP_LEGACY_OOB or pair_mode == pair.BLE_SMP_SECURE_OOB:
                # Not support OOB
                print('[callback] ble smp No operation is required')
            elif pair_mode == pair.BLE_SMP_LEGACY_JUST_WORK or pair_mode == pair.BLE_SMP_SECURE_JUST_WORK or pair_mode == pair.BLE_SMP_SECURE_NUMBER_COMPARISON:
                print('[callback] ble smp Confirm pairing, No PIN code is required')
                print('[callback] ble server will execute \'ble.smpUserConfirm(connect_id, 1, 0)\' to Confirm pairing')
                ble.smpUserConfirm(connect_id, 1, 0)
                # If you want to cancel pairing, you can use the 'ble.smpUserConfirm(connect_id,0,0)'
            elif pair_mode == pair.BLE_SMP_LEGACY_PASSKEY_OUTPUT or pair_mode == pair.BLE_SMP_SECURE_PASSKEY_OUTPUT:
                print('[callback] ble server smp The PIN code is displayed, wait peer device enters PIN code')
                # If you want to cancel pairing, you can use the 'ble.smpUserConfirm(connect_id,0,0)'
            elif pair_mode == pair.BLE_SMP_LEGACY_PASSKEY_INPUT or pair_mode == pair.BLE_SMP_SECURE_PASSKEY_INPUT:
                print('[callback] ble smp Confirm pairing, Please enter the PIN code displayed by peer device!!!')
                print('>>> ble.smpUserConfirm(connect_id,2,xxxxxx)')
                # If you want to cancel pairing, you can use the 'ble.smpUserConfirm(connect_id,0,0)'
        else:
            print('[callback] ble smp user confirm indication fail.')
    elif event_id == event.BLE_GATT_SEND_END:
        print('[ble_callback]event_id: BLE_GATT_SEND_END')
        if status == 0:
            print('[callback] ble send data successful.')
        else:
            print('[callback] ble send data failed.')
    else:
        print('unknown event id {}.'.format(event_id))


def ble_gatt_server_init(cb):
    ret = ble.serverInit(cb)
    if ret != 0:
        print('ble_gatt_server_init failed.')
        return -1
    print('ble_gatt_server_init success.')
    return 0


def ble_gatt_server_release():
    ret = ble.serverRelease()
    if ret != 0:
        print('ble_gatt_server_release failed.')
        return -1
    print('ble_gatt_server_release success.')
    return 0


def ble_gatt_open():
    ret = ble.gattStart()
    if ret != 0:
        print('ble_gatt_open failed.')
        return -1
    print('ble_gatt_open success.')
    return 0


def ble_gatt_close():
    ret = ble.gattStop()
    if ret != 0:
        print('ble_gatt_close failed.')
        return -1
    print('ble_gatt_close success.')
    return 0


def ble_gatt_set_name():
    code = 0  # utf8
    name = _BLE_NAME
    ret = ble.setLocalName(code, name)
    if ret != 0:
        print('ble_gatt_set_name failed.')
        return -1
    print('ble_gatt_set_name success.')
    return 0


def ble_gatt_set_param():
    min_adv =  0x30  #0x300
    max_adv =  0x30  #0x320
    adv_type = 0  # Connectable non-directed broadcast, selected by default
    addr_type = 1 #RANDOM address   #0 Public address
    channel = 0x07
    filter_strategy = 0  # Process scan and connection requests for all devices
    discov_mode = 2
    no_br_edr = 1
    enable_adv = 1
    ret = ble.setAdvParam(min_adv, max_adv, adv_type, addr_type, channel, filter_strategy, discov_mode, no_br_edr, enable_adv)
    if ret != 0:
        print('ble_gatt_set_param failed.')
        return -1
    print('ble_gatt_set_param success.')
    return 0


def ble_gatt_set_data():
    adv_data = [0x02, 0x01, 0x06]
    ble_name = _BLE_NAME
    length = len(ble_name) + 1
    adv_data.append(length)
    adv_data.append(0x09)
    name_encode = ble_name.encode('UTF-8')
    for i in range(0, len(name_encode)):
        adv_data.append(name_encode[i])
    print('set adv_data:{}'.format(adv_data))
    # FLAGS
    adv_data.append(2)
    adv_data.append(1)
    adv_data.append(2)
    # TX_POWER
    adv_data.append(2)
    adv_data.append(0xa)
    adv_data.append(2)
    # UUID_HID
    adv_data.append(3)
    adv_data.append(0x3)
    adv_data.append(0x12)
    adv_data.append(0x18)
    # HID_APPEARANCE
    adv_data.append(3)
    adv_data.append(0x19)
    adv_data.append(0xc0)
    adv_data.append(0x03)
    
    data = bytearray(adv_data)
    ret = ble.setAdvData(data)
    if ret != 0:
        print('ble_gatt_set_data failed.')
        return -1
    print('ble_gatt_set_data success.')
    return 0


def ble_gatt_set_rsp_data():
    adv_data = []
    ble_name = _BLE_NAME
    length = len(ble_name) + 1
    adv_data.append(length)
    adv_data.append(0x09)
    name_encode = ble_name.encode('UTF-8')
    for i in range(0, len(name_encode)):
        adv_data.append(name_encode[i])
    print('set adv_rsp_data:{}'.format(adv_data))
    data = bytearray(adv_data)
    ret = ble.setAdvRspData(data)
    if ret != 0:
        print('ble_gatt_set_rsp_data failed.')
        return -1
    print('ble_gatt_set_rsp_data success.')
    return 0


def ble_gatt_add_service():
    primary = 1
    server_id = 0x01
    uuid_type = 1  # Short UUID
    uuid_s = 0x1812 # UUID_HID
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    ret = ble.addService(primary, server_id, uuid_type, uuid_s, uuid_l)
    if ret != 0:
        print('ble_gatt_add_service1 failed.')
        return -1

    primary = 1
    server_id = 0x02
    uuid_type = 1  # Short UUID
    uuid_s = 0x180A # UUID_DEVICE_INFO
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    ret = ble.addService(primary, server_id, uuid_type, uuid_s, uuid_l)
    if ret != 0:
        print('ble_gatt_add_service2 failed.')
        return -1

    primary = 1
    server_id = 0x03
    uuid_type = 1  #Short UUID
    uuid_s = 0x180F # UUID_BATTERY_SERVICE
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    ret = ble.addService(primary, server_id, uuid_type, uuid_s, uuid_l)
    if ret != 0:
        print('ble_gatt_add_service3 failed.')
        return -1

    print('ble_gatt_add_service success.')
    return 0


def ble_gatt_add_characteristic():
    server_id = 0x01
    chara_id = 0x01
    chara_prop = 0x02 | 0x04  # 0x02-readable 0x04-Writable and does not require a link layer reply 0x08-writable 0x10-notification 0x20-indicate
    uuid_type = 1  # Short UUID
    uuid_s = 0x2A4E # UUID_PROTOCOL
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    ret = ble.addChara(server_id, chara_id, chara_prop, uuid_type, uuid_s, uuid_l)
    if ret != 0:
        print('ble_gatt_add_characteristic1 failed.')
        return -1

    server_id = 0x01
    chara_id = 0x02
    chara_prop = 0x02 | 0x08 | 0x10  # 0x02-readable 0x04-Writable and does not require a link layer reply 0x08-writable 0x10-notification 0x20-indicate
    uuid_type = 1  # Short UUID
    uuid_s = 0x2A4D # UUID_HIDREPORT
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    ret = ble.addChara(server_id, chara_id, chara_prop, uuid_type, uuid_s, uuid_l)
    if ret != 0:
        print('ble_gatt_add_characteristic2 failed.')
        return -1

    server_id = 0x01
    chara_id = 0x03
    chara_prop = 0x02  # 0x02-readable 0x04-Writable and does not require a link layer reply 0x08-writable 0x10-notification 0x20-indicate
    uuid_type = 1  # Short UUID
    uuid_s = 0x2A4B # UUID_HIDREPORT_MAP
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    ret = ble.addChara(server_id, chara_id, chara_prop, uuid_type, uuid_s, uuid_l)
    if ret != 0:
        print('ble_gatt_add_characteristic3 failed.')
        return -1

    server_id = 0x01
    chara_id = 0x04
    chara_prop = 0x02 | 0x08 | 0x10  # 0x02-readable 0x04-Writable and does not require a link layer reply 0x08-writable 0x10-notification 0x20-indicate
    uuid_type = 1  # Short UUID
    uuid_s = 0x2A22 # UUID_HIDBOOT_KB_INPUT
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    ret = ble.addChara(server_id, chara_id, chara_prop, uuid_type, uuid_s, uuid_l)
    if ret != 0:
        print('ble_gatt_add_characteristic4 failed.')
        return -1

    server_id = 0x01
    chara_id = 0x05
    chara_prop = 0x02 | 0x04 | 0x08  # 0x02-readable 0x04-Writable and does not require a link layer reply 0x08-writable 0x10-notification 0x20-indicate
    uuid_type = 1  # short UUID
    uuid_s = 0x2A32 # UUID_HIDBOOT_KB_OUTPUT
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    ret = ble.addChara(server_id, chara_id, chara_prop, uuid_type, uuid_s, uuid_l)
    if ret != 0:
        print('ble_gatt_add_characteristic5 failed.')
        return -1

    server_id = 0x01
    chara_id = 0x06
    chara_prop = 0x02 | 0x08 | 0x10  # 0x02-readable 0x04-Writable and does not require a link layer reply 0x08-writable 0x10-notification 0x20-indicate
    uuid_type = 1  # Short UUID
    uuid_s = 0x2A33 # UUID_HIDBOOT_MOUSE_INPUT
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    ret = ble.addChara(server_id, chara_id, chara_prop, uuid_type, uuid_s, uuid_l)
    if ret != 0:
        print('ble_gatt_add_characteristic6 failed.')
        return -1

    server_id = 0x01
    chara_id = 0x07
    chara_prop = 0x02  # 0x02-readable 0x04-Writable and does not require a link layer reply 0x08-writable 0x10-notification 0x20-indicate
    uuid_type = 1  # Short UUID
    uuid_s = 0x2A4A # UUID_HIDINFO
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    ret = ble.addChara(server_id, chara_id, chara_prop, uuid_type, uuid_s, uuid_l)
    if ret != 0:
        print('ble_gatt_add_characteristic7 failed.')
        return -1

    server_id = 0x01
    chara_id = 0x08
    chara_prop = 0x08  # 0x02-readable 0x04-Writable and does not require a link layer reply 0x08-writable 0x10-notification 0x20-indicate
    uuid_type = 1  # short UUID
    uuid_s = 0x2A4C # UUID_HIDCONTROLPOINT
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    ret = ble.addChara(server_id, chara_id, chara_prop, uuid_type, uuid_s, uuid_l)
    if ret != 0:
        print('ble_gatt_add_characteristic8 failed.')
        return -1

    server_id = 0x02
    chara_id = 0x09
    chara_prop = 0x02  # 0x02-readable 0x04-Writable and does not require a link layer reply 0x08-writable 0x10-notification 0x20-indicate
    uuid_type = 1  # Short UUID
    uuid_s = 0x2A23 # UUID_SYSTEM_ID
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    ret = ble.addChara(server_id, chara_id, chara_prop, uuid_type, uuid_s, uuid_l)
    if ret != 0:
        print('ble_gatt_add_characteristic9 failed.')
        return -1

    server_id = 0x02
    chara_id = 0x0a
    chara_prop = 0x02  # 0x02-readable 0x04-Writable and does not require a link layer reply 0x08-writable 0x10-notification 0x20-indicate
    uuid_type = 1  # Short UUID
    uuid_s = 0x2A24 # UUID_MODEL_NUMBER
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    ret = ble.addChara(server_id, chara_id, chara_prop, uuid_type, uuid_s, uuid_l)
    if ret != 0:
        print('ble_gatt_add_characteristic10 failed.')
        return -1

    server_id = 0x02
    chara_id = 0x0b
    chara_prop = 0x02  # 0x02-readable 0x04-Writable and does not require a link layer reply 0x08-writable 0x10-notification 0x20-indicate
    uuid_type = 1  # short UUID
    uuid_s = 0x2A25 # UUID_SERIAL_NUMBER
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    ret = ble.addChara(server_id, chara_id, chara_prop, uuid_type, uuid_s, uuid_l)
    if ret != 0:
        print('ble_gatt_add_characteristic11 failed.')
        return -1

    server_id = 0x02
    chara_id = 0x0c
    chara_prop = 0x02  # 0x02-readable 0x04-Writable and does not require a link layer reply 0x08-writable 0x10-notification 0x20-indicate
    uuid_type = 1  # short UUID
    uuid_s = 0x2A26 # UUID_FIRMWARE_VERSION
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    ret = ble.addChara(server_id, chara_id, chara_prop, uuid_type, uuid_s, uuid_l)
    if ret != 0:
        print('ble_gatt_add_characteristic12 failed.')
        return -1

    server_id = 0x02
    chara_id = 0x0d
    chara_prop = 0x02  # 0x02-readable 0x04-Writable and does not require a link layer reply 0x08-writable 0x10-notification 0x20-indicate
    uuid_type = 1  # short UUID
    uuid_s = 0x2A27 # UUID_HARDWARE_VERSION
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    ret = ble.addChara(server_id, chara_id, chara_prop, uuid_type, uuid_s, uuid_l)
    if ret != 0:
        print('ble_gatt_add_characteristic13 failed.')
        return -1

    server_id = 0x02
    chara_id = 0x0e
    chara_prop = 0x02  # 0x02-readable 0x04-Writable and does not require a link layer reply 0x08-writable 0x10-notification 0x20-indicate
    uuid_type = 1  # short UUID
    uuid_s = 0x2A28 # UUID_SOFTWARE_VERSION
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    ret = ble.addChara(server_id, chara_id, chara_prop, uuid_type, uuid_s, uuid_l)
    if ret != 0:
        print('ble_gatt_add_characteristic14 failed.')
        return -1

    server_id = 0x02
    chara_id = 0x0f
    chara_prop = 0x02  # 0x02-readable 0x04-Writable and does not require a link layer reply 0x08-writable 0x10-notification 0x20-indicate
    uuid_type = 1  # short UUID
    uuid_s = 0x2A29 # UUID_MANUFACTURER_NAME
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    ret = ble.addChara(server_id, chara_id, chara_prop, uuid_type, uuid_s, uuid_l)
    if ret != 0:
        print('ble_gatt_add_characteristic15 failed.')
        return -1

    server_id = 0x02
    chara_id = 0x10
    chara_prop = 0x02  # 0x02-readable 0x04-Writable and does not require a link layer reply 0x08-writable 0x10-notification 0x20-indicate
    uuid_type = 1  # short UUID
    uuid_s = 0x2A2A # UUID_IEEE_LIST
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    ret = ble.addChara(server_id, chara_id, chara_prop, uuid_type, uuid_s, uuid_l)
    if ret != 0:
        print('ble_gatt_add_characteristic16 failed.')
        return -1

    server_id = 0x02
    chara_id = 0x11
    chara_prop = 0x02  # 0x02-readable 0x04-Writable and does not require a link layer reply 0x08-writable 0x10-notification 0x20-indicate
    uuid_type = 1  # short UUID
    uuid_s = 0x2A50 # UUID_PNP_ID
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    ret = ble.addChara(server_id, chara_id, chara_prop, uuid_type, uuid_s, uuid_l)
    if ret != 0:
        print('ble_gatt_add_characteristic17 failed.')
        return -1

    server_id = 0x03
    chara_id = 0x12
    chara_prop = 0x02 | 0x10  # 0x02-readable 0x04-Writable and does not require a link layer reply 0x08-writable 0x10-notification 0x20-indicate
    uuid_type = 1  # short UUID
    uuid_s = 0x2A19 # UUID_BATTERY
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    ret = ble.addChara(server_id, chara_id, chara_prop, uuid_type, uuid_s, uuid_l)
    if ret != 0:
        print('ble_gatt_add_characteristic18 failed.')
        return -1

    print('ble_gatt_add_characteristic success.')
    return 0


def ble_gatt_add_characteristic_value():
    data = [0x01]
    server_id = 0x01
    chara_id = 0x01
    permission = 0x0001 | 0x0002 | 0x40 | 0x200 # 0x01 - Readable permission 0x02 - Writable permission  0x04 - Read need authentication 0x08 - Read need authorization 0x10 - Read need encryption 0x20 - Read requires authorization authentication 0x40 - Write need authentication 0x80 - Write need authorization 0x0100 - Write need encryption 0x0200 - Write requires authorization authentication
    uuid_type = 1  # short UUID
    uuid_s = 0x2A4E # UUID_PROTOCOL protocol_mode
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    value = bytearray(data)
    ret = ble.addCharaValue(server_id, chara_id, permission, uuid_type, uuid_s, uuid_l, value)
    if ret != 0:
        print('ble_gatt_add_characteristic_value1 failed.')
        return -1

    data = [0x00]
    server_id = 0x01
    chara_id = 0x02
    permission = 0x0001 | 0x0002
    uuid_type = 1  # short UUID
    uuid_s = 0x2A4D # UUID_HIDREPORT
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    for i in range(0, 7):
        data.append(0x00)
    value = bytearray(data)
    ret = ble.addCharaValue(server_id, chara_id, permission, uuid_type, uuid_s, uuid_l, value)
    if ret != 0:
        print('ble_gatt_add_characteristic_value2 failed.')
        return -1

    data = [0x05, 0x0c, 0x09, 0x01, 0xa1, 0x01, 0x85, 0x01, 0x15, 0x00, 0x25, 0x01, 0x75, 0x01, 0x95, 0x01, 0x09, 0xCD, 0x81, 0x06, 0x0a, 0x83,0x01, 0x81, 0x06, 0x09, 0xb5, 0x81, 0x06, 0x09, 0xb6, 0x81, 0x06, 0x09, 0xea, 0x81, 0x06, 0x09, 0xe9, 0x81, 0x06, 0x0a, 0x25, 0x02, 0x81, 0x06, 0x0a, 0x24, 0x02, 0x81, 0x06, 0xc0]
    server_id = 0x01
    chara_id = 0x03
    permission = 0x0001 | 0x0002
    uuid_type = 1  # Short UUID
    uuid_s = 0x2A4B # UUID_HIDREPORT_MAP map
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    value = bytearray(data)
    ret = ble.addCharaValue(server_id, chara_id, permission, uuid_type, uuid_s, uuid_l, value)
    if ret != 0:
        print('ble_gatt_add_characteristic_value5 failed.')
        return -1

    data = [0x00]
    server_id = 0x01
    chara_id = 0x04
    permission = 0x0001 | 0x0002
    uuid_type = 1  # Short UUID
    uuid_s = 0x2A22 # UUID_HIDBOOT_KB_INPUT boot_kb_input
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    for i in range(0, 5):
        data.append(0x00)
    value = bytearray(data)
    ret = ble.addCharaValue(server_id, chara_id, permission, uuid_type, uuid_s, uuid_l, value)
    if ret != 0:
        print('ble_gatt_add_characteristic_value6 failed.')
        return -1

    data = [0x00]
    server_id = 0x01
    chara_id = 0x05
    permission = 0x0001 | 0x0002
    uuid_type = 1  # Short UUID
    uuid_s = 0x2A32 # UUID_HIDBOOT_KB_INPUT boot_kb_output
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    for i in range(0, 5):
        data.append(0x00)
    value = bytearray(data)
    ret = ble.addCharaValue(server_id, chara_id, permission, uuid_type, uuid_s, uuid_l, value)
    if ret != 0:
        print('ble_gatt_add_characteristic_value7 failed.')
        return -1

    data = [0x00]
    server_id = 0x01
    chara_id = 0x06
    permission = 0x0001 | 0x0002
    uuid_type = 1  # Short UUID
    uuid_s = 0x2A33 # UUID_HIDBOOT_KB_INPUT boot_mouse_input
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    for i in range(0, 5):
        data.append(0x00)
    value = bytearray(data)
    ret = ble.addCharaValue(server_id, chara_id, permission, uuid_type, uuid_s, uuid_l, value)
    if ret != 0:
        print('ble_gatt_add_characteristic_value8 failed.')
        return -1

    data = [0x11, 0x10, 0x00, 0x03]
    server_id = 0x01
    chara_id = 0x07
    permission = 0x0001 | 0x0002
    uuid_type = 1  # Short UUID
    uuid_s = 0x2A4A # UUID_HIDINFO
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    value = bytearray(data)
    ret = ble.addCharaValue(server_id, chara_id, permission, uuid_type, uuid_s, uuid_l, value)
    if ret != 0:
        print('ble_gatt_add_characteristic_value9 failed.')
        return -1

    data = [0x01]
    server_id = 0x01
    chara_id = 0x08
    permission = 0x0001 | 0x0002
    uuid_type = 1  # Short UUID
    uuid_s = 0x2A4C # UUID_HIDCONTROLPOINT
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    value = bytearray(data)
    ret = ble.addCharaValue(server_id, chara_id, permission, uuid_type, uuid_s, uuid_l, value)
    if ret != 0:
        print('ble_gatt_add_characteristic_value10 failed.')
        return -1

    data = [0x01, 0x02]
    server_id = 0x02
    chara_id = 0x09
    permission = 0x0001 | 0x0002
    uuid_type = 1  # Short UUID
    uuid_s = 0x2A23 # UUID_SYSTEM_ID
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    value = bytearray(data)
    ret = ble.addCharaValue(server_id, chara_id, permission, uuid_type, uuid_s, uuid_l, value)
    if ret != 0:
        print('ble_gatt_add_characteristic_value11 failed.')
        return -1

    data = [0x02, 0x03]
    server_id = 0x02
    chara_id = 0x0a
    permission = 0x0001 | 0x0002
    uuid_type = 1  # Short UUID
    uuid_s = 0x2A24 # UUID_MODEL_NUMBER
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    value = bytearray(data)
    ret = ble.addCharaValue(server_id, chara_id, permission, uuid_type, uuid_s, uuid_l, value)
    if ret != 0:
        print('ble_gatt_add_characteristic_value12 failed.')
        return -1

    data = [0x03, 0x04]
    server_id = 0x02
    chara_id = 0x0b
    permission = 0x0001 | 0x0002
    uuid_type = 1  # Short UUID
    uuid_s = 0x2A25 # UUID_SERIAL_NUMBER
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    value = bytearray(data)
    ret = ble.addCharaValue(server_id, chara_id, permission, uuid_type, uuid_s, uuid_l, value)
    if ret != 0:
        print('ble_gatt_add_characteristic_value13 failed.')
        return -1

    data = [0x04, 0x05]
    server_id = 0x02
    chara_id = 0x0c
    permission = 0x0001 | 0x0002
    uuid_type = 1  # Short UUID
    uuid_s = 0x2A26 # UUID_FIRMWARE_VERSION
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    value = bytearray(data)
    ret = ble.addCharaValue(server_id, chara_id, permission, uuid_type, uuid_s, uuid_l, value)
    if ret != 0:
        print('ble_gatt_add_characteristic_value14 failed.')
        return -1

    data = [0x05, 0x06]
    server_id = 0x02
    chara_id = 0x0d
    permission = 0x0001 | 0x0002
    uuid_type = 1  # Short UUID
    uuid_s = 0x2A27 # UUID_HARDWARE_VERSION
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    value = bytearray(data)
    ret = ble.addCharaValue(server_id, chara_id, permission, uuid_type, uuid_s, uuid_l, value)
    if ret != 0:
        print('ble_gatt_add_characteristic_value15 failed.')
        return -1

    data = [0x05, 0x17]
    server_id = 0x02
    chara_id = 0x0e
    permission = 0x0001 | 0x0002
    uuid_type = 1  # Short UUID
    uuid_s = 0x2A28 # UUID_SOFTWARE_VERSION
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    value = bytearray(data)
    ret = ble.addCharaValue(server_id, chara_id, permission, uuid_type, uuid_s, uuid_l, value)
    if ret != 0:
        print('ble_gatt_add_characteristic_value16 failed.')
        return -1

    data = [0x06, 0x07]
    server_id = 0x02
    chara_id = 0x0f
    permission = 0x00f4#0x0001 | 0x0002 | 
    uuid_type = 1  # Short UUID
    uuid_s = 0x2A29 # UUID_MANUFACTURER_NAME
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    value = bytearray(data)
    ret = ble.addCharaValue(server_id, chara_id, permission, uuid_type, uuid_s, uuid_l, value)
    if ret != 0:
        print('ble_gatt_add_characteristic_value17 failed.')
        return -1

    data = [0x07, 0x08]
    server_id = 0x02
    chara_id = 0x10
    permission = 0x0001 | 0x0002
    uuid_type = 1  # Short UUID
    uuid_s = 0x2A2A # UUID_IEEE_LIST
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    value = bytearray(data)
    ret = ble.addCharaValue(server_id, chara_id, permission, uuid_type, uuid_s, uuid_l, value)
    if ret != 0:
        print('ble_gatt_add_characteristic_value18 failed.')
        return -1

    data = [0x08, 0x09]
    server_id = 0x02
    chara_id = 0x11
    permission = 0x0001 | 0x0002
    uuid_type = 1  # Short UUID
    uuid_s = 0x2A50 # UUID_PNP_ID
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    value = bytearray(data)
    ret = ble.addCharaValue(server_id, chara_id, permission, uuid_type, uuid_s, uuid_l, value)
    if ret != 0:
        print('ble_gatt_add_characteristic_value19 failed.')
        return -1

    data = [0x0a, 0x0b]
    server_id = 0x03
    chara_id = 0x12
    permission = 0x0001 | 0x0002
    uuid_type = 1  # Short UUID
    uuid_s = 0x2A19 # UUID_BATTERY
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    value = bytearray(data)
    ret = ble.addCharaValue(server_id, chara_id, permission, uuid_type, uuid_s, uuid_l, value)
    if ret != 0:
        print('ble_gatt_add_characteristic_value20 failed.')
        return -1

    print('ble_gatt_add_characteristic_value success.')
    return 0


def ble_gatt_add_characteristic_desc():
    data = [0x01, 0x01] # input report
    server_id = 0x01
    chara_id = 0x02
    permission = 0x0001 | 0x0002
    uuid_type = 1  # Short UUID
    uuid_s = 0x2908
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    value = bytearray(data)
    ret = ble.addCharaDesc(server_id, chara_id, permission, uuid_type, uuid_s, uuid_l, value)
    if ret != 0:
        print('ble_gatt_add_characteristic_desc1 failed.')
        return -1

    data = [0x04, 0x02] # output report
    server_id = 0x01
    chara_id = 0x02
    permission = 0x0001 | 0x0002
    uuid_type = 1  # Short UUID
    uuid_s = 0x2908
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    value = bytearray(data)
    ret = ble.addCharaDesc(server_id, chara_id, permission, uuid_type, uuid_s, uuid_l, value)
    if ret != 0:
        print('ble_gatt_add_characteristic_desc2 failed.')
        return -1

    data = [0x05, 0x03] # feature report
    server_id = 0x01
    chara_id = 0x02
    permission = 0x0001 | 0x0002
    uuid_type = 1  # Short UUID
    uuid_s = 0x2908
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    value = bytearray(data)
    ret = ble.addCharaDesc(server_id, chara_id, permission, uuid_type, uuid_s, uuid_l, value)
    if ret != 0:
        print('ble_gatt_add_characteristic_desc3 failed.')
        return -1

    data = [0x00, 0x01] # input report client config
    server_id = 0x01
    chara_id = 0x02
    permission = 0x0001 | 0x0002
    uuid_type = 1  # Short UUID
    uuid_s = 0x2902
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    value = bytearray(data)
    ret = ble.addCharaDesc(server_id, chara_id, permission, uuid_type, uuid_s, uuid_l, value)
    if ret != 0:
        print('ble_gatt_add_characteristic_desc4 failed.')
        return -1

    data = [0x00, 0x01] # boot_kb_input client config
    server_id = 0x01
    chara_id = 0x04
    permission = 0x0001 | 0x0002
    uuid_type = 1  # Short UUID
    uuid_s = 0x2902
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    value = bytearray(data)
    ret = ble.addCharaDesc(server_id, chara_id, permission, uuid_type, uuid_s, uuid_l, value)
    if ret != 0:
        print('ble_gatt_add_characteristic_desc5 failed.')
        return -1

    data = [0x00, 0x01] # boot_mouse_input client config
    server_id = 0x01
    chara_id = 0x06
    permission = 0x0001 | 0x0002
    uuid_type = 1  # Short UUID
    uuid_s = 0x2902
    uuid_l = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    value = bytearray(data)
    ret = ble.addCharaDesc(server_id, chara_id, permission, uuid_type, uuid_s, uuid_l, value)
    if ret != 0:
        print('ble_gatt_add_characteristic_desc6 failed.')
        return -1

    print('ble_gatt_add_characteristic_desc success.')
    return 0


def ble_gatt_send_notification():
    #global BLE_SERVER_HANDLE
    #data = [0x39, 0x39, 0x39, 0x39, 0x39]  # test data
    #conn_id = 0
    #attr_handle = BLE_SERVER_HANDLE + 2
    #value = bytearray(data)
    #ret = ble.sendNotification(conn_id, attr_handle, value)
    #if ret != 0:
    #    print('ble_gatt_send_notification failed.')
    #    return -1
    print('ble_gatt_send_notification success.')
    return 0


def ble_gatt_add_service_complete():
    global BLE_GATT_SYS_SERVICE
    ret = ble.addOrClearService(1, BLE_GATT_SYS_SERVICE)
    if ret != 0:
        print('ble_gatt_add_service_complete failed.')
        return -1
    print('ble_gatt_add_service_complete success.')
    return 0


def ble_gatt_clear_service_complete():
    global BLE_GATT_SYS_SERVICE
    ret = ble.addOrClearService(0, BLE_GATT_SYS_SERVICE)
    if ret != 0:
        print('ble_gatt_clear_service_complete failed.')
        return -1
    print('ble_gatt_clear_service_complete success.')
    return 0


def ble_adv_start():
    ret = ble.advStart()
    if ret != 0:
        print('ble_adv_start failed.')
        return -1
    print('ble_adv_start success.')
    return 0


def ble_adv_stop():
    ret = ble.advStop()
    if ret != 0:
        print('ble_adv_stop failed.')
        return -1
    print('ble_adv_stop success.')
    return 0


def main():
    ret = ble_gatt_server_init(ble_callback)
    if ret == 0:
        ret = ble_gatt_open()
        if ret != 0:
            return -1
    else:
        return -1
    # count = 0
    # while True:
    #     utime.sleep(1)
    #     count += 1
    #     if count % 5 == 0:
    #         print('##### BLE running, count = {}......'.format(count))
    #     if count > 1200:
    #         count = 0
    #         print('!!!!! stop BLE now !!!!!')
    #         ble_gatt_close()
    #         return 0


if __name__ == '__main__':
    main()
