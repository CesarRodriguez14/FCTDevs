class BasicTests():
    def electric_test(self,_val,_max=None,_min=None):
        result = True
        if _max != None:
            result = _val <= _max and result
        if _min != None:
            result = _val >= _min and result
        return result
    
    def led_test(self,_rgb,_max,_min):
        result = True
        for i,color in enumerate(_rgb):
            result = self.electric_test(color,_max[i],_min[i]) and result
        return result
            

