import json

class pswHandler():
    PSW_FAIL_FLAG = -1
    PSW_USER_FLAG = 0
    PSW_PSW_FLAG = 1
    def __init__(self,_psw_file:str):
        self.psw_file = _psw_file
        self.last_user_to_validate = "UNDEFINED"
        self.getPSW()

    def getPSW(self,_last_fails_count:int):
        self.state = self.PSW_PSW_FLAG
        try:
            with open(self.psw_file,'r',encoding = 'utf-8') as _file:
                _data = json.load(_file)
                self.psw = _data["psw"]
                self.users = _data["users"]
                self.max_fails = _data["max_fails"]
            if _last_fails_count >= self.max_fails:
                self.state = self.PSW_USER_FLAG
            else:
                self.state = self.PSW_PSW_FLAG
        except:
            self.state = self.PSW_FAIL_FLAG
        return self.state

    def validatePSW(self,_last_fails_count:int,_psw:str):
        if _last_fails_count >= self.max_fails:
            res_flag = _psw in self.users
            if res_flag:
                self.last_user_to_validate = _psw
        else:
            res_flag = _psw == self.psw
        return res_flag

