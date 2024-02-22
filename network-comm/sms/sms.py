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

# codeing=UTF-8
import net
import checkNet
import sms as SMS

#本示例演示将分开到达设备的两条长两条短信合并为一条短信
#本例演示要求短信索引值0和短信索引值1的短信同一条长短信的内容
    
class QuecSMS():

    def __init__(self):
        self.__enable_log = False
        self.sms_set_enable_log()
        self.sms = SMS
        self.sms.setCallback(self.__SMS_Call_back)
        self.message=""

    def sms_deal_phone_number(self,args):
        data=enumerate(args)
        data_str1=""
        data_str2=""
        data_str3=""
        for index,value in data:
            if index % 2 == 0:
                data_str1=data_str1+value
            else:
                data_str2=data_str2+value
        for i in range(0,len(data_str1)):
            data_str3=data_str3+data_str2[i]
            data_str3=data_str3+data_str1[i]
        return data_str3
        
    def sms_display(self):
        self.__log("Get Message Loction : {}".format(self.sms.getSaveLoc()))
        sms.setSaveLoc("ME", "ME", "ME")
        self.__log("Get ME Message Numbers : {}".format(self.sms.getMsgNums()))
        sms.setSaveLoc("SM", "SM", "SM")
        self.__log("Get SM  Message Numbers : {}".format(self.sms.getMsgNums()))

    def sms_set_enable_log(self,flag=True):
        self.__enable_log = flag

    def __log(self,args):
        if self.__enable_log:
            print("QuecSMS_LOG: {}".format(args))


    def __SMS_Call_back(self,args):
        self.__log("Get SIM Id          : {}".format(args[0]))
        self.__log("Get Message index   : {}".format(args[1]))
        self.__log("Get Message Storage : {}".format(args[2]))
        
    def sms_delete_user_data_head(self):
        
        self.message=self.message[:58]+self.message[58+2*6:]
        
    def sms_replace_data_index(self,index,data):
        self.message = self.message[:index] + data + self.message[index+len(data):]
    
    def sms_append_sub_message_data(self,data):
        self.message = self.message + data
        
    def sms_decode_pdu_message(self):
        return self.sms.decodePdu(self.message,self.sms.getPduLength(self.message))
    
    def sms_get_message_info(self,index):
        """
        ：param index    ：短信索引值
        ：tyoe  index    ：整形
        
        ：return         ：元组类型
        元组内容：
        （message_ref，message_total_num，message_seq，sub_message_data，pdu_tye，sub_message_len）
        
        ：message_ref        ：短信参考标识，同一个标识表明为同一条短信
        ：message_total_num  ：此条长短信总条数
        ：message_seq        ：此条短信在长短信中的序号
        ：sub_message_data   ：词条短信的内容
        ：pdu_tye            ：PDU类型，bit 6标记是否包含用户报文头，长短信需要
        ：sub_message_len    ：此条短信内容长度
        
        """
        message0=self.sms.searchPduMsg(index)
        self.message = message0
        sca_num  = int(message0[0:2],16) - 1
        data_len = 2
        addr_type= message0[data_len:data_len+1*2]
        data_len = data_len+1*2
        
        sca      = message0[data_len:data_len+sca_num*2]
        # 电话号码高低位需要转换
        sca = self.sms_deal_phone_number(sca)

        if sca_num % 2 == 1:
             print("Get SCA phone {}".format(sca[:-1]))
        else:
             print("Get SCA phone {}".format(sca))

        data_len = data_len+sca_num*2

        pdu_tye   = int(message0[data_len:data_len+1*2],16)
        data_len = data_len+1*2

        oa_num   = int(message0[data_len:data_len+1*2],16)
        data_len = data_len+1*2
        oa_addr_type   = message0[data_len:data_len+1*2]
        data_len = data_len+1*2

        if oa_num % 2 == 1:
             oa_num_t   = int((oa_num + 1)/2)
        else:
             oa_num_t   = int((oa_num )/2)

        oa       = message0[data_len:data_len+oa_num_t*2]
        # 电话号码高低位需要转换
        oa       = self.sms_deal_phone_number(oa)

        if oa_num % 2 == 1:
             print("Get OA phone {}".format(oa[:-1]))
        else:
             print("get OA phone {}".format(oa))

        data_len = data_len+oa_num_t*2
        pid      = message0[data_len:data_len+1*2]
        
        data_len = data_len+1*2
        dcs      = message0[data_len:data_len+1*2]
        data_len = data_len+1*2
        scts     = message0[data_len:data_len+7*2]
        data_len = data_len+7*2
        sub_message_len = int(message0[data_len:data_len+1*2],16)
        data_len = data_len+1*2
        sub_message_head = message0[data_len:data_len+6*2]
        data_len = data_len+6*2

        # 或短信用户数据
        sub_message_data = message0[data_len:data_len+sub_message_len*2]

        #长短信
        if ((pdu_tye & 0x40 ) >> 6) == 1:
                #长短信,处理长短信用户报文头
                message_ref = int(sub_message_head[6:8],16)
                message_total_num = int(sub_message_head[8:10],16)
                message_seq = int(sub_message_head[10:12],16)
                return message_ref,message_total_num,message_seq,pdu_tye,sub_message_len,sub_message_data
        else:
             # 短短信
             return 0,1,1,pdu_tye,sub_message_len,sub_message_data
             
if __name__ == '__main__':
    sms0 = QuecSMS()
    sms1 = QuecSMS()
    
    # 读取短信索引值0的短信内容
    message0=list(sms0.sms_get_message_info(0))
    
    # 读取短信索引值1的短信内容
    message1=list(sms1.sms_get_message_info(1))
    print("Get Messge 0 {}".format(message0))
    print("Get Messge 1 {}".format(message1))
    if message0[0] != message1[0]:
        print("Message 0 and Message 1 are not the content data of the same long SMS!")
        exit
    # 解码message0的PDU串
    message0_pdu=list(sms0.sms_decode_pdu_message())
    # 解码message1的PDU串
    message1_pdu=(sms1.sms_decode_pdu_message())
    
    # 合并短信
    #判断messge 0 和 message 1的短信序列号那个考前
    if message0[2] < message1[2]:
        message_merge=message0_pdu[1]+message1_pdu[1]
    else:
        message_merge=message1_pdu[1]+message0_pdu[1]
    print("Get Merger Message is {}".format(message_merge))
    