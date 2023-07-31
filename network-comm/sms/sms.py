# codeing=UTF-8
import net
import checkNet
import sms as SMS


class QuecSMS():

    def __init__(self):
        self.__enable_log = False
        self.sms_set_enable_log()
        self.sms = SMS
        self.sms.setCallback(self.__SMS_Call_back)
        self.message=""

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
        
    #    message_ref        ：短信参考标识，同一个标识表明为同一条短信
    #    message_total_num  ：此条长短信总条数
    #    message_seq        ：此条短信在长短信中的序号
    #    sub_message_data   ：词条短信的内容
    #    pdu_tye            ：PDU类型，bit 6标记是否包含用户报文头，长短信需要
    #    sub_message_len    ：此条短信内容长度
    def sms_append_sub_message_data(self,data):
        self.message = self.message + data
        
    def sms_decode_pdu_message(self):
        return self.sms.decodePdu(self.message,self.sms.getPduLength(self.message))
    
    def sms_get_message_info(self,index):
        
        message0=self.sms.searchPduMsg(index)
        self.message = message0
        #获取SCA
        sca_num  = int(message0[0:2],16)
        data_len = 2
        sca      = message0[data_len:data_len+sca_num*2]
        data_len = data_len+sca_num*2
        pdu_tye   = int(message0[data_len:data_len+1*2],16)
        
        data_len = data_len+1*2
        mr       = message0[data_len:data_len+1*2]
        
        data_len = data_len+1*2
        oa       = message0[data_len:data_len+sca_num*2]
        
        data_len = data_len+sca_num*2
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
        sub_message_data = message0[data_len:data_len+sub_message_len*2]
        message_ref = int(sub_message_head[6:8],16)
        message_total_num = int(sub_message_head[8:10],16)
        message_seq = int(sub_message_head[10:12],16)
        return message_ref,message_total_num,message_seq,pdu_tye,sub_message_len,sub_message_data
if __name__ == '__main__':
    sms1 = QuecSMS()
    sms2 = QuecSMS()
    #示例中索引0 、1为长短新的第一条第二条数据，以此为例展示长短信的合并
    #长短信合并只能用PDU方式读取解码合并，TEXT方式无法判断短信顺序
    
    message0=list(sms1.sms_get_message_info(0))
    message1=list(sms2.sms_get_message_info(1))
    #合成一条短信步骤
    
    # 1、设置PDU_type 为用户数据不包含头信息，合成一条设置成短信内容没有头部信息
    pdu_type = "{:0>2X}".format(message0[3]&0xBF)
    # pdu_type 起始位置18
    message = sms1.sms_replace_data_index(18,pdu_type)
    
    # 2、将后续的字串内容取出追加到第一条信息用户数据之后
    sms1.sms_append_sub_message_data(message1[5])
    
    
    # 3、短信长度起始位置56，修改长度为原本长度加上追加的字串长度
    message0[4]=message0[4]+message1[4]
    message_len = "{:0>2X}".format(message0[4])
    sms1.sms_replace_data_index(56,message_len)
    
    # 4、去掉用户数据报文头
    sms1.sms_delete_user_data_head()
    
    # 5、解码修改后的PDU串
    message=sms1.sms_decode_pdu_message()
    
    print("Get meger message : {}".format(message))
    