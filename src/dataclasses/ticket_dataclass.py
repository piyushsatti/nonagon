from base_dataclass import Base

# inherited class decleration
class TicketDataclass(Base):
    
    table_name:str = locals()['__qualname__']
        
    guild_id:str = ''
    toggle:int = -1
    # json('message_id' -> [title, desc, channel_id, category_id, message_id->ticket_ids])
    message_to_ticket_map:dict = {}
    
    meta_data:dict = locals()['__annotations__']
    meta_data['super'] = {
        'primary_key': ['guild_id'],
        'defaults': {
            'toggle': 1
        }
    }
    
    # helper
    def set_data(self):
        self.data = {
            'guild_id': self.guild_id,
            'toggle': self.toggle,
            'message_to_ticket_map': self.message_to_ticket_map
        }
    
    def load(self):
        self.set_data()
        tmp = self.callback_read(self.table_name, self.data, self.meta_data)
        self.guild_id = tmp[0]
        self.toggle = tmp[1]
        if tmp[2] is not None:
            self.message_to_ticket_map = tmp[2]
        else:
            self.message_to_ticket_map = {}

    ### Hidden ###
    def __init__(self) -> None:
        super().__init__()
        self.data = self.set_data()
    
    def create(self):
        self.set_data()
        self.callback_create(self.table_name, self.data, self.meta_data)
    
    def read(self):
        self.set_data()
        return self.callback_read(self.table_name, self.data, self.meta_data)
    
    def update(self):
        self.set_data()
        self.callback_update(self.table_name, self.data, self.meta_data)
    
    def delete(self):
        self.set_data()
        self.callback_delete(self.table_name, self.data, self.meta_data)
    ##############