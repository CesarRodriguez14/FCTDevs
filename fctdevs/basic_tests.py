class BasicTests():
    def electric_test(self,_val,_max=None,_min=None,_logFlag=False):
        result = True
        log = ''
        if _max != None:
            log += f'MAX:{_max}\t'
            result = _val <= _max and result
        if _min != None:
            log += f'MIN:{_min}\t'
            result = _val >= _min and result
        log += f'VAL:{_val}\t'
        log += 'OK' if result else 'NG'
        if _logFlag:
            print(log)
        return result
    
    def led_test(self,_rgb,_max,_min,_logFlag=False):
        result = []
        for i,color in enumerate(_rgb):
            result.append(self.electric_test(color,_max[i],_min[i],_logFlag))
        return result
            

