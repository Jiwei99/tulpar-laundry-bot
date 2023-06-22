from db import setup_db
from controller import setup_bot 

def main():
    setup_db()
    setup_bot()

if __name__ == '__main__':
    main()