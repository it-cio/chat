import asyncio
from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import run_async, run_js


chat_msg = []
online_users = set()

MAX_MESSAGES_COUNT = 100


async def main():
    global chat_msg

    put_markdown("## 🧊 Добро пожаловать в онлайн чат!")

    msg_box = output()
    put_scrollable(msg_box, height=300, keep_bottom=True)

    nickname = await input(
        "Войти в чат", required=True, placeholder="Ваше имя",
        validate=lambda n: "Такой ник уже используется!" if n in online_users or n == '📢' else None)
    online_users.add(nickname)

    chat_msg.append(('📢', f"'{nickname}' присоединился к чату!"))

    refresh_task = run_async(refresh_msg(nickname, msg_box))

    while True:
        data = await input_group("💭 Новое сообщение", [
            input(placeholder="Текст сообщения", name="msg"),
            actions(name="cmd", buttons=["Отправить", {'label':"Выйти из чата", 'type':'cancel'}])
        ], validate=lambda m: ('msg', "Введите текст сообщения!") if m["cmd"] == "Отправить" and not m["msg"] else None)

        if data is None:
            break

        msg_box.append(put_markdown(f"'{nickname}': {data['msg']}"))
        chat_msg.append((nickname, data['msg']))

    # exit chat
    refresh_task.close()

    online_users.remove(nickname)
    toast("Вы вышли из чата!")
    msg_box.append(put_markdown(f"📢 Пользователь '{nickname}' покинул чат!"))
    chat_msg.append(('📢', f"Пользователь '{nickname}' покинул чат!"))

    put_buttons(['Перезайти'], onclick=lambda btn: run_js('window.location.reload()'))


async def refresh_msg(nickname, msg_box):
    global chat_msg
    last_idx = len(chat_msg)

    while True:
        await asyncio.sleep(1)

        for m in chat_msg[last_idx:]:
            if m[0] != nickname:
                msg_box.append(put_markdown(f"'{m[0]}': {m[1]}"))

        # remove expired
        if len(chat_msg) > MAX_MESSAGES_COUNT:
            chat_msg = chat_msg[len(chat_msg) // 2:]

        last_idx = len(chat_msg)


if __name__ == "__main__":
    start_server(main, debug=True, port=8080, cdn=False)





