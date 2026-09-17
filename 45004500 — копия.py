from telethon.sync import TelegramClient, errors
from time import sleep
from telethon.errors.rpcerrorlist import MessageTooLongError, PeerIdInvalidError
import dbm


def dbm_base():
    file = dbm.open('api2.dbm', 'c')
    try:
        file['api_id2']
    except:
        file['api_id2'] = input('Введите api_id:')
        file['api_hash2'] = input('Введите api_hash:')
    file.close()
    return dbm.open('api2.dbm', 'r')


file = dbm_base()
api_id = int(file['api_id2'].decode())
api_hash = file['api_hash2'].decode()
client = TelegramClient('client2', api_id, api_hash)

delay = int(input('Введите значение таймера в секундах: '))


def dialog_sort(dialog):
    # Сортирует диалоги по непрочитанным
    return dialog.unread_count


def spammer(client):
    k = 0
    j = 0

    def create_groups_list(groups=[]):
        # Создает список групп, где непрочитанных сообщений больше 10
        for dialog in client.iter_dialogs():
        # Начинает бегать по диалогам клиента
            if dialog.is_group:
            # True, если это группа
                if dialog.unread_count >= 1:
                # Сколько msg не прочитано в данный момент. Эта переменная не обновляется при поступлении новых сообщений
                    groups.append(dialog)
        return groups

    with client:
        for m in client.iter_messages('me', 1):
            # история моего чата
            msg = m
        while True:
            groups = create_groups_list()
            groups.sort(key=dialog_sort, reverse=True)
            for g in groups[:10000]:
                try:
                    client.forward_messages(g, msg, 'me')
                    # Отправляет сообщение msg в группу g и отправил я
                    k = k + 1
                except errors.ForbiddenError as o:
                    # Обработка того, что нельзя написать
                    client.delete_dialog(g)
                    if g.entity.username != None:
                        print(f'Error: {o.message} Аккаунт покинул @{g.entity.username}')
                    else:
                        print(f'Error: {o.message} Аккаунт покинул {g.name}')
                except errors.FloodError as e:
                    if e.seconds > 80:
                        continue
                    else:
                        print(f'Error: {e.message} Требуется ожидание {e.seconds} секунд')
                        sleep(e.seconds)
                except PeerIdInvalidError:
                    # На обработку бота
                    client.delete_dialog(g)
                except MessageTooLongError:
                    print(f'Message was too long ==> {g.name}')
                except errors.BadRequestError as i:
                    print(f'Error: {i.message}')
                except errors.RPCError as a:
                    print(f'Error: {a.message}')
            j = k + j
            k = 0
            print('Отправлено сообщений: ', j)
            sleep(delay)
            groups.clear()


if __name__ == '__main__':
    spammer(client)
