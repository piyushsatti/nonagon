import sqlite3, os, json

db_connection = sqlite3.connect(
            os.path.join(
                os.getcwd(), 
                'db', 
                'peppermint.db'
            )
        )

# Template class
class Base():
    conn = db_connection
    
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def create_table(table_name, meta_data):
        try:
            q = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
            for k in meta_data.keys():
                if k in ['super', 'meta_data', 'table_name']:
                    continue
                
                if meta_data[k] == int:
                    if k in meta_data['super']['defaults'].keys():
                        q += f"{k} INT DEFAULT {meta_data['super']['defaults'][k]},\n"
                    else:
                        q += f"{k} INT,\n"
                elif meta_data[k] == str or meta_data[k] == dict:
                    if k in meta_data['super']['defaults'].keys():
                        q += f"{k} VARCHAR DEFAULT \'{meta_data['super']['defaults'][k]}\',\n"
                    else:
                        q += f"{k} VARCHAR,\n"
                        
            out = ""
            for i, prim in enumerate(meta_data['super']['primary_key']):
                if len(meta_data['super']['primary_key']) == 1:
                    out += f"{prim}"
                elif i == len(meta_data['super']['primary_key'])-1:
                    out += f"{prim}"
                else:
                    out += f"{prim},"
            q += f"PRIMARY KEY ({out})\n)"
            
            Base.manage_table(q, table_name)
        except:
            raise
        
    @staticmethod
    def delete_table(table_name):
        try:
            q = f"DROP TABLE {table_name}"
            Base.manage_table(q, table_name)
        except:
            raise
    
    @staticmethod
    def read_all(table_name):
        try:
            q = f"SELECT * FROM TABLE {table_name}"
            Base.manage_table(q, table_name)
        except:
            raise
        
    # CRUD
    def callback_create(self, table_name, data, meta_data):
        try: 
            self.check_primary_keys(data, meta_data)
            # if what I am inserting is none then dont insert that
            cols = ""
            out = ""
            for i, k in enumerate(data.keys()):
                if data[k] in ['',-1,{}]:
                    continue
                cols += k + ','
                if meta_data[k] == int:
                    out += f"{data[k]},"
                elif meta_data[k] == str:
                    out += f"\'{data[k]}\',"
                elif meta_data[k] == dict:
                    data_json = self.json_to_str(data[k])
                    out += f"\'{data_json}\',"
            
            q = f"INSERT INTO {table_name} ({cols[:-1]})\n VALUES ({out[:-1]})"
            Base.manage_table(q, table_name)
        except:
            raise
    
    def callback_read(self, table_name, data, meta_data):
        try:
            condition = self.get_primary_key_condition(data, meta_data)
            q = f"SELECT * FROM {table_name} WHERE {condition}"
            
            is_dict = []
            for k in meta_data.keys():
                if k in ['super', 'meta_data', 'table_name']:
                    continue
                if meta_data[k] == dict:
                    is_dict.append(True)
                else:
                    is_dict.append(False)
            
            out = []
            for i, val in enumerate(Base.read_table(q, table_name)):
                if is_dict[i]:
                    out.append(
                        self.str_to_json(val)
                    ) 
                else:
                    out.append(val)
            return out
        except:
            raise
    
    def callback_update(self, table_name, data, meta_data):
        try:
            condition = self.get_primary_key_condition(data, meta_data)
            q = f"UPDATE {table_name}\nSET "
            
            for k in data.keys():
                if k not in meta_data['super']['primary_key']:
                    if meta_data[k] == int:
                        q += f"{k} = {data[k]},"
                    elif meta_data[k] == str:
                        q += f"{k} = \'{data[k]}\',"
                    elif meta_data[k] == dict:
                        data_json = self.json_to_str(data[k])
                        q += f"{k} = \'{data_json}\',"
            q = q[:-1]
            q += f"\nWHERE {condition}"
            
            Base.manage_table(q, table_name)
        except:
            raise
    
    def callback_delete(self, table_name, data, meta_data):
        try: 
            condition = self.get_primary_key_condition(data, meta_data)
            q = f"DELETE FROM {table_name} WHERE {condition}"
            Base.manage_table(q, table_name)
        except:
            raise
        
    # Helpers
    @classmethod
    def manage_table(cls, q, class_name):
        # print(q)
        try:
            cur = cls.conn.cursor()
            cur.execute(q)
            cls.conn.commit()
        except Exception as e:
            pass
            # print(f'Error in manage_table: {class_name}\n', e)
    
    @classmethod
    def read_table(cls, q, class_name):
        try:
            cur = cls.conn.cursor()
            cur.execute(q)
            return cur.fetchone()
        except Exception as e:
            pass
            # print(f'Error in read_table: {class_name}\n', e)
    
    @staticmethod
    def str_to_json(a):
        try:
            return json.loads(a)
        except:
            pass
            # print("Json object is NULL in DB")
    
    @staticmethod
    def json_to_str(a):
        return json.dumps(a)
    
    def check_primary_keys(self, data, meta_data):
        for k in meta_data['super']['primary_key']:
            if data[k] is None:
                assert False, f"Error: {k} key is primary and None"
                
    def get_primary_key_condition(self, data, meta_data):
        condition_list = []
        for k in meta_data['super']['primary_key']:
            if meta_data[k] == int:
                condition_list.append(f"{k} = {data[k]}")
            elif meta_data[k] == str or meta_data[k] == dict:
                condition_list.append(f"{k} = \'{data[k]}\'")
        
        condition = ''
        for i, cond in enumerate(condition_list):
            if len(meta_data['super']['primary_key']) == 1:
                condition += f"{cond}"
            elif i == len(meta_data['super']['primary_key'])-1:
                condition += f"{cond}"
            else:
                condition += f"{cond} AND "
        
        return condition