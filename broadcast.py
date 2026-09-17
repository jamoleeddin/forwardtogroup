"""Bir martalik broadcast: aniq ro'yxatdagi chatlarga Saved Messages'dagi
oxirgi xabarni forward qiladi. Cheksiz sikl yo'q, avtomatik guruh topish yo'q.

Ishga tushirish:
    python broadcast.py            # haqiqiy yuborish
    python broadcast.py --dry-run  # faqat ko'rsatadi, yubormaydi
"""

import argparse
import os
import sys
from time import sleep

from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.errors import FloodWaitError, RPCError

TARGETS_FILE = "targets.txt"
PAUSE_BETWEEN_SENDS = 2  # sekund, oddiy rate-limit himoyasi


def load_targets(path):
    """targets.txt dan chat identifikatorlarini o'qiydi (# — izoh)."""
    if not os.path.exists(path):
        sys.exit(f"{path} topilmadi. targets.example.txt dan nusxa oling.")

    targets = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            targets.append(int(line) if line.lstrip("-").isdigit() else line)

    if not targets:
        sys.exit(f"{path} bo'sh — yuboradigan manzil yo'q.")
    return targets


def get_source_message(client):
    """Saved Messages'dagi eng oxirgi xabarni qaytaradi."""
    for message in client.iter_messages("me", 1):
        return message
    sys.exit("Saved Messages bo'sh — avval yubormoqchi bo'lgan xabaringizni o'sha yerga tashlang.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Hech narsa yubormaydi, faqat rejani chiqaradi.")
    args = parser.parse_args()

    load_dotenv()
    try:
        api_id = int(os.environ["TELEGRAM_API_ID"])
        api_hash = os.environ["TELEGRAM_API_HASH"]
    except KeyError as missing:
        sys.exit(f"{missing} o'rnatilmagan. .env.example ga qarang.")

    targets = load_targets(TARGETS_FILE)

    with TelegramClient("session", api_id, api_hash) as client:
        message = get_source_message(client)
        print(f"Manba xabar: id={message.id}")
        print(f"Manzillar soni: {len(targets)}")

        sent = failed = 0
        for target in targets:
            if args.dry_run:
                print(f"[dry-run] {target}")
                continue
            try:
                client.forward_messages(target, message, "me")
                sent += 1
                print(f"OK   {target}")
            except FloodWaitError as e:
                # Telegram kutishni so'radi — kutamiz va bir marta qayta urinamiz.
                print(f"WAIT {target}: {e.seconds}s")
                sleep(e.seconds)
                try:
                    client.forward_messages(target, message, "me")
                    sent += 1
                    print(f"OK   {target}")
                except RPCError as retry_error:
                    failed += 1
                    print(f"FAIL {target}: {retry_error}")
            except RPCError as e:
                failed += 1
                print(f"FAIL {target}: {e}")
            sleep(PAUSE_BETWEEN_SENDS)

        print(f"\nYuborildi: {sent}, xato: {failed}")


if __name__ == "__main__":
    main()
