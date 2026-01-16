import sys
from core import PesapalDB

def run():
    print("="*40)
    print("PesapalDB Interactive Terminal")
    print("commands: exit, help")
    print("="*40)
    
    db = PesapalDB()

    while True:
        try:
            query = input("SQL> ")
            if query.strip().lower() == 'exit':
                break
            
            result = db.execute(query)
            
            if isinstance(result, list):
                if not result:
                    print("Empty Set")
                else:
                    # Basic table printer
                    print(result) 
                    print(f"({len(result)} rows)")
            else:
                print(result)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run()
