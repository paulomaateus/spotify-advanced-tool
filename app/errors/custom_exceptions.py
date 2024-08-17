
    
class LoginErrorException(Exception):
    def __init__(self, message:str, status_code: int):
        self.message= message
        self.status= status_code 
        super().__init__(self.message)
        
class SpotifyErrorException(Exception):
    def __init__(self, message:str, status_code: int):
        self.message= message
        self.status= status_code 
        super().__init__(self.message)