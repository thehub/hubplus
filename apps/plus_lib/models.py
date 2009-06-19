
""" This app, plus_lib for common code shared by other hub_plus apps. Might be moved if there's a better place to put it """

class DisplayStatus :
    def __init__(self,txt,time) :
        self.txt=txt
        self.time=time

    def __str__(self) :
        return self.txt
