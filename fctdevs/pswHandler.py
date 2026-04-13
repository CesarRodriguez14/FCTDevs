import json

class pswHandler():
    PSW_NO_READ_FLAG = -1
    PSW_USER_FLAG = 0
    PSW_PSW_FLAG = 1
    def __init__(self,_psw_file:str):
        self.psw_file = _psw_file
        self.last_user_to_validate = "UNDEFINED"
        self.state = False
        self.getPSW()

    def getPSW(self):
        try:
            with open(self.psw_file,'r',encoding = 'utf-8') as _file:
                _data = json.load(_file)
                self.psw = _data["psw"]
                self.users = _data["users"]
                self.max_fails = _data["max_fails"]
                self.state = True
        except:
            self.state = False
        return self.state
    
    def getPSWType(self,_last_fails_count:int):
        if self.state:
            if _last_fails_count >= self.max_fails:
                self.psw_type = self.PSW_USER_FLAG
            else:
                self.psw_type = self.PSW_PSW_FLAG
        else:
            self.psw_type = self.PSW_NO_READ_FLAG
        return self.psw_type


    def validatePSW(self,_last_fails_count:int,_psw:str):
        self.getPSWType(_last_fails_count)
        if self.psw_type == self.PSW_USER_FLAG:
            res_flag = _psw in self.users
            if res_flag:
                self.last_user_to_validate = _psw
        elif self.psw_type == self.PSW_PSW_FLAG:
            res_flag = _psw == self.psw
        return res_flag

