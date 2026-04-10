import json

class pswHandler():
    def __init__(self,_psw_file:str):
        self.psw_file = _psw_file
        self.last_user_to_validate = "UNDEFINED"
        self.getPSW()

    def getPSW(self):
        self.state = True
        try:
            with open(self.psw_file,'r',encoding = 'utf-8') as _file:
                _data = json.load(_file)
                self.psw = _data["psw"]
                self.users = _data["users"]
                self.max_fails = _data["max_fails"]
        except:
            self.state = False
        return self.state

    def validatePSW(self,_last_fails_count:int,_psw:str):
        if _last_fails_count >= self.max_fails:
            res_flag = _psw in self.users
            if res_flag:
                self.last_user_to_validate = _psw
        else:
            res_flag = _psw = self.psw
        return res_flag

