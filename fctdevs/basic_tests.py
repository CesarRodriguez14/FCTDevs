class BasicTests():
    def electric_test(self,_val,_max=None,_min=None,_logFlag=False):
        result = True
        log = ''
        if _max != None:
            log.append(f'MAX:{_max}\t')
            result = _val <= _max and result
        if _min != None:
            log.append(f'MIN:{_min}\t')
            result = _val >= _min and result
        log.append(f'VAL:{_val}\t')
        log.append('OK' if result else 'NG')
        if _logFlag:
            print(log)
        return result
    
    def led_test(self,_rgb,_max,_min):
        result = []
        for i,color in enumerate(_rgb):
            result.append(self.electric_test(color,_max[i],_min[i]))
        return result
            

