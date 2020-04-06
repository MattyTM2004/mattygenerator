import string, random, os, sqlite3, time

def errorLOG(log):
    if not os.path.exists('./ERROR.txt'):
        f = open('./ERROR.txt', 'w')
        f.close()
    fecha, hora = time.strftime("%d/%m/%y"), time.strftime("%H:%M:%S")
    try:
        f = open('./ERROR.txt', 'a')
        f.write(f'[{fecha} {hora}] {log}\n')
        f.close()
    except Exception as EX:
        print(EX)

def LOG(usuario, ip, log):
    if not os.path.exists('./LOG.txt'):
        f = open('./LOG.txt', 'w')
        f.close()
    fecha, hora = time.strftime("%d/%m/%y"), time.strftime("%H:%M:%S")

    try:
        f = open('./LOG.txt', 'a')
        f.write(f'[{fecha} {hora}] [{usuario} {ip}] {log}\n')
        f.close()
    except Exception as EX:
        print(EX)



def generate_invites(action,cant=None):
    if not os.path.exists('./invites.txt'):
        f = open('./invites.txt', 'w')
        f.close()
    if action == 'add':
        for i in range(cant):
            invite = ''
            for i in range(16):
                invite += f'{random.randint(0,9)}{random.choice(string.ascii_letters)}'
            f = open('./invites.txt', 'a')
            f.write(f'{invite}\n')
            f.close()
    
    elif action == 'delete':
        os.remove('./invites.txt')

def check_invite(invite):
    if not os.path.exists('./invites.txt'):
        f = open('./invites.txt', 'w')
        f.close()
    with open('./invites.txt', 'r') as f:
        f.seek(0)
        if not invite in f.read():
            pass
        else:
            return 'normal'

    with open('./admin.txt', 'r') as f:
        f.seek(0)
        if not invite in f.read():
            return False
        else:
            return 'admin'

def get_user_level(user):
    conexion = sqlite3.connect("users_database.db")
    cursor = conexion.cursor()
    lista = cursor.execute(f"SELECT * FROM users WHERE username = '{user}'").fetchall()

    return int(lista[0][4])

def get_users():
    conexion = sqlite3.connect("users_database.db")
    cursor = conexion.cursor()
    normal = cursor.execute('SELECT * FROM users WHERE level="0" ').fetchall()
    admins = cursor.execute('SELECT * FROM users WHERE level="1" ').fetchall()

    return normal, admins

def delete_user(user):
    global errorLOG
    conexion = sqlite3.connect("users_database.db")
    cursor = conexion.cursor()
    try:
        cursor.execute(f"DELETE FROM users WHERE username='{user}'")
        conexion.commit()
        return True
    except Exception as EX:
        errorLOG(EX)
        return False

def make_admin(user):
    global errorLOG
    conexion = sqlite3.connect("users_database.db")
    cursor = conexion.cursor()
    try:
        cursor.execute(f"UPDATE users SET level='1' WHERE username='{user}'")
        conexion.commit()
        return True
    except Exception as EX:
        errorLOG(EX)
        return False

def make_normal(user):
    global errorLOG
    conexion = sqlite3.connect("users_database.db")
    cursor = conexion.cursor()
    try:
        cursor.execute(f"UPDATE users SET level='0' WHERE username='{user}'")
        conexion.commit()
        return True
    except Exception as EX:
        errorLOG(EX)
        return False

def delete_database(user):
    global errorLOG
    conexion = sqlite3.connect("users_database.db")
    cursor = conexion.cursor()
    try:
        cursor.execute(f"DELETE FROM users")
        conexion.commit()
        return True
    except Exception as EX:
        errorLOG(EX)
        return False

if __name__ == '__main__':
    generate_invites('add', 5)