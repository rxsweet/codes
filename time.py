from datetime import datetime

if __name__ == '__main__':
    today = datetime.today().strftime(': %Y-%m-%d %H:%M:%S')
    file = open('time.txt', 'w', encoding= 'utf-8')
    file.write(today)
    file.close()
