import mysql.connector
from mysql.connector import Error

class pyMysqlConnector:
    def __init__(self,host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = mysql.connector.connect(
                host = self.host,
                database = self.database,
                user = self.user,
                password = self.password
            )
        self.column_names = None
        
    def getColumnNames(self,table):
        try:
            if self.connection.is_connected():
                # print("DB 연결 성공")
                
                cursor = self.connection.cursor()
                
                cursor.execute(f"SHOW COLUMNS FROM {table}")
                
                columns = cursor.fetchall()
                self.column_names = [column[0] for column in columns]
                return self.column_names
            
        except Error as e:
            print(f"error in getColumnNames : {e}")
            return None
    
    def insertDataToMysql(self, table, data):
        try:
            if self.connection.is_connected():
                # print("DB 연결 성공")
                
                cursor = self.connection.cursor()
                head_query = f"INSERT INTO {table} ("
                self.body_query = ""
                for i in self.column_names:
                    self.body_query += i+','

                self.body_query = self.body_query[:-1] + ")"

                tail_query = "VALUES (" + "%s,"*len(self.column_names)
                tail_query = tail_query[:-1] + ")"

                update_query = " on duplicate key update "
                for i in self.column_names:
                    update_query += f"{i} = values({i}),"
                update_query = update_query[:-1]

                insert_query = head_query+self.body_query+tail_query+update_query
                cursor.executemany(insert_query, data)
                self.connection.commit()

        except Error as e:
            print(f"error in insertDataToMysql : {e}")

    def fetch_data(self, query):
        try:
            if self.connection.is_connected():
                cursor = self.connection.cursor(dictionary=True)
                cursor.execute(query)

                records = cursor.fetchall()
                result_list = [record for record in records]

                print("Total number of rows in table: ", cursor.rowcount)
                # for row in result_list:
                #     print(row)

                return result_list
            
        except Error as e:
            print(f"Error in fetch_data : {e}")

    