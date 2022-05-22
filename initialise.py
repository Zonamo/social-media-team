import subprocess
import sys
from datetime import datetime
import time
import os
import json

def install():
    packages = ["tweepy", "gspread", "discord"]
    for package in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    return

def first_time():
    file_exists = os.path.exists(sys.path[0] + '/first_time.txt')
    if file_exists == False:
        with open(os.path.join(sys.path[0],"first_time.txt"), "w") as file:
            file.write("0")
        install()
    return

first_time()

import gspread
from discord import Webhook, RequestsWebhookAdapter

def credentials():
    creds = {
  "type": "service_account",
  "project_id": "propane-gift-347313",
  "private_key_id": "59b3f2443786b5a060c8c7d0b0cb3d8a90babc75",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDGxMy9jc4Ser0o\nch8NyFoKhClbloS15O94jm3bE1/LCmg9LnI2i7/sUZunal+BZM1z5Vbdfge+5uGC\nY0lVmWy07+AcuGdlO32tcQEAaE9XVYfSz+AWGeFhFvWgFUKtxiRH9Q7yaDPwLrVM\nS4t8rJdwD3AnYgdPQddPgm1m8XgVDuXactmUKEIVWjI4fArg5Wl21roIZ199ca3A\nmfrlJ48ir1w3WGeVoyxSAObff3dL03TC4VvipLlPjDNVoEGxSsDPY1CJfgMotBP+\nqhawtLywFSfK9by5YkMfMsmOYH4wp0mUJGxdBEtdbAq09iD0a5TLZ4ZGo7gOtO+Y\nFhwx8DW/AgMBAAECggEAX2rU0D/1B0j1aieSgbbGhprYEbfpYDoUvR4+XTbpOtp1\nnL0hpc6jZMnuO0lkrIRb3kFfWDdqd3l1EvcfmqBqn1cxkgfx1pZe5/ZB4VSxlb6g\n05HnxCRLXaS8Z8sc9beS7hoVQUfFewypCoWPYdumXOyETduQn7r/JZN6ejr7hruF\nxSbbtPplm4AOG1AQg/s5YerWeYZOkxjg+G4chax0GFmIJ7CvdpYKMP5++C7jjV7a\nYm5yGU4w/NW64JzLqoapdVTD4qFxX+PN9r29gTvMnhRy3+ZCnJbAlwMpQqXF/Uat\nT0U83sfd1yVQIm2r0DLgBVWVcScxgTLt2hRJyhzVeQKBgQDs368I2TuWw086GnsJ\nATblzLUfQLytmc0b9MzV6/RGiCLrZ3jIJxkG25eE/yXvCE5mYvGuE1e4g8rhdHCc\nyxF7GWsEjN5P79oSkNeKwawjMxvv9SUPJ2ij0rrta06xKBO5PhQysqlv5W26TB/y\nnvIAT4jXxI3sVqNXxlOuR2V9aQKBgQDW0XasARpSfNXCX0VbZhLTnH3WITCYdyJC\nkeaIaFWMEAYuXKb5eL1UwGS4UwtnvL+TpK9F2eB0Z6EdfVhxFUlbB8JQHgY5e6Ph\n3ENE4lMsjXRwniS7ItnGosLTWr1llcR5yuN7ViMczVbMtx4zhsbP9gADbx3Cw9HB\nouVy5Z4s5wKBgALiXmE/M+iMDETq2aCscRyvN21f/mwmuUaj3nKkYt8Q/UvcgK3/\nO+DHf7rQ2IdmlH3Oqp6yAZlvkWLZZh2io13aW2E8zeAvTXp4ZQd9gDkVgDuVwpPC\nqRWFlV0at2SU1lilFt3fKwz/wCxKjQEJSm0SitoFvKyqCWciNRakK+oxAoGAaP3h\nUXoMgmpvE1v7Cwvdgb2Hp0N7e9kmToD+uoa74QPn8XrpRR7k8mpCD/DOrzoKLEAe\nRjaRxHLtxPsBYeu0eaBWMVArXKb4VyiPXDh9zFWqpmw0qZ4D8FiWfjRoQyEq8Rff\njOVxrd8SYGXThf2GaBfks8j4M7v/ZfOWz0w4vdsCgYEA2xoir2xxlSF/FMJ/GFLt\nj+Hgm8+MPVLCsCu19ShZ5RBZtot30mMAJ6a1wc+mrmqhd4bGqRGcN/ew5PH/ZtiT\nwvRMeal9vTDUcapqVJRbRtxWmObuOixhjMYtXArEsiNZNpeiudccyuDuVTkUNvY1\ndWoZEin0ijydaJ+ZWTIPrBY=\n-----END PRIVATE KEY-----\n",
  "client_email": "sheet-get@propane-gift-347313.iam.gserviceaccount.com",
  "client_id": "110161093902709763192",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/sheet-get%40propane-gift-347313.iam.gserviceaccount.com"
}
    with open(os.path.join(sys.path[0],"credentials.json"), "w") as file:
        file.write(json.dumps(creds))
    return

def json_handler():
    i = 0
    while i < 4:
        i += 1
        try:
            print('get sheet')
            gc = gspread.service_account(filename=os.path.join(sys.path[0],'credentials.json'))          #is directory problem or not
            sh = gc.open_by_key('1w4wNzx2Yk2I3knQw-VHzFll6QQpAK9aOGi90Osuguks')
            worksheet = sh.sheet1
            res = worksheet.get_all_records()
            with open(os.path.join(sys.path[0], 'sheet.txt'), 'w') as file:
                file.write(json.dumps(res)) 
            break
        except Exception as Argument:
            print(f'sheetGet error: {Argument}')
            f = open(os.path.join(sys.path[0], "fooks_sheetGET.txt"), "a")
            f.write(f':\n{Argument}\n')
            f.close()
            if i == 3:
                while True:
                    try:
                        webhook = Webhook.from_url("https://discord.com/api/webhooks/972978746275557376/Wg80pNqX2dG7fXY34ypmo0Rxifo0sVFlLMyDaQmfLKJwkwntTb95b-u8l7o9-agrWDzv", adapter=RequestsWebhookAdapter())
                        webhook.send(f"Sheet get 3x fail:\n{Argument}")
                        break
                    except:
                        continue
            else:   
                time.sleep(60)
            continue
 
    return

def initialise_hashtag_bearers():
    client_spots = [ 
    [0,'AAAAAAAAAAAAAAAAAAAAABZqbgEAAAAAicVd9cEZ56%2BaVBPx7KXD5ycS6hg%3DYgHnn0mlpuPhxUBwIQcCTbpUvirF2BASukXGbZa2zWuUIcI4jk'], [0,'AAAAAAAAAAAAAAAAAAAAABF8bgEAAAAAfv4l1EKHOms%2BbHiBz5%2FyZrJfWYE%3DScpO0D56TQcRn3gI8luiFsL77LPYPUb3aVK7cnSylQOCtHC5T3'], [0,'AAAAAAAAAAAAAAAAAAAAAC18bgEAAAAAxnNeBXuH2a8asoaVuNq6banSxkw%3DvCX8OjnCOInptMFJzwtcgu9luP5xFn8BTfEjgjLjoTXQ0WpZhB'], [0,'AAAAAAAAAAAAAAAAAAAAAEh8bgEAAAAAKHE8dA1FZ0omtdIRXG0LJd17NfE%3D7QxmdB3oJgVMh82Qgjl7Eixzq484tMaZluHPBw5t5J69bxkwhw'], [0,'AAAAAAAAAAAAAAAAAAAAAFx8bgEAAAAA3L1pwJUFGN5LqIbjZhpfTZgON6I%3DPW5b3lF0KuIAhPg2Tu8CUW1LUH9e2n4OlOOUG24vafTzlA3bUZ'], [0, 'AAAAAAAAAAAAAAAAAAAAAHx8bgEAAAAAN72UAcdPw%2BA9tkfex8X1gblY7%2FY%3DhH5sWGfpIlVI6HkGZYp42Zv7UEhVi8St8Z2IkjAE0kOj3U0Tyn'], [0, 'AAAAAAAAAAAAAAAAAAAAAJZ8bgEAAAAAIBa4%2BXyhvI6Cedsih1lZThRZNCM%3DPIhk5FZxxsc97BvtqCHWR7X3esk3xryXbKCfLm2twBQSvfZFBg'], [0, 'AAAAAAAAAAAAAAAAAAAAAKZ8bgEAAAAAq%2FcKIbYye6B0GdZeetXEbhFpoHI%3Dbfa1brolFGqhQV3Vah460HZxcFUdpGoCAeEGQcNpz2kv5rhNO8'], [0,'AAAAAAAAAAAAAAAAAAAAAL98bgEAAAAAL6wTEBpB8AtNFwUEqlxiK6mGClE%3DfV7aeRf4n7s6zs35I8Xa8avpNgv59Mb8NdGQHiZtKLiAUwwwB5'], [0, 'AAAAAAAAAAAAAAAAAAAAANp8bgEAAAAA%2BJ0H1I2%2BSLO7OiQ8Znjb0vZ5Hl0%3DzqoMeavjflG57kMIFBlUZGL5zHU8N79i6lb61JUUZvKxWCaJ0r'], [0, 'AAAAAAAAAAAAAAAAAAAAAG8XbwEAAAAAAaGR19AqjvYnNJMDwbpndBiqhG0%3DxTuXxro6LTQE8R8IPAbNJh2SZ6mqzRKwPlRpDhaSucgwdY84Wg'], [0, 'AAAAAAAAAAAAAAAAAAAAAIQXbwEAAAAAsaStGjNSK3PdiINa%2FBRTOR%2FrFmM%3DCpJyrrD6Rd4rVdxMTOadTnx6w0mvkbCFUL74BVeXcNkUCsIOhr'], [0, 'AAAAAAAAAAAAAAAAAAAAAJsXbwEAAAAAoKJ85P06Zc5ZCbsR7yBZk41WG%2Fo%3DinkoXrneAWmjRLrOwLJod4Ucfa3zKHOCjdfpuHEup1oymQ27XO']
    ]
    client_spots_json = json.dumps(client_spots)
    with open(os.path.join(sys.path[0],"bearers_hashtags.json"), "w") as file:
        file.write(client_spots_json)
    return

def initialise_mention_bearers():
    client_spots = [ 
    [0,'AAAAAAAAAAAAAAAAAAAAAK4XbwEAAAAAy%2BfUJl4%2Bmbr7p5Nlw79SIWkKtW4%3DWNHIMT1lP7OFWDaACmk6wl3CaNNJvM8wMXg1AVKt677GuCUjBD'], [0,'AAAAAAAAAAAAAAAAAAAAAMQXbwEAAAAAM4DWHdBejujguiyLfikSEg03%2B2A%3DSmC80m4MD6msqBXKvscsD9vsdILtgKeUixWa7fMQ6oqBGeDnb2'], [0,'AAAAAAAAAAAAAAAAAAAAANgXbwEAAAAA0V1zeo7XgCAYtykL7Fx6LlOc5U4%3DTpB3URhorTlu9tpdYvLzJsVpoxxBp8fuP4IZPsw1Spob1E3XdQ'], [0,'AAAAAAAAAAAAAAAAAAAAAPoXbwEAAAAALtSQriNLW5FhV6Me4%2FPYOvvLCDY%3DrS7IwILGt6g0S7sXQmpT9ZDHIbD0XhBVDjXd8XT2eWu1vWRmEF'], [0,'AAAAAAAAAAAAAAAAAAAAAAoYbwEAAAAAAJTjMNKgmAIfPQmEA%2BoC5cXLlck%3DDCjZR9VfmE1IHwrrfMVOq5r4QspRv7kfbLOIpkvmaYvCvkoteq'], [0, 'AAAAAAAAAAAAAAAAAAAAACIYbwEAAAAAOzKQKzm3aUmr4kbApEAuMaAcMRI%3DMe9BH6HezfJYq2DhNXGNSlfGzgERD8VRYbyEAezur16NNkAaQF'], [0, 'AAAAAAAAAAAAAAAAAAAAADcYbwEAAAAAcB06m%2FeeRU8epgnXhhifrhIaAm8%3DFdJA6xmcL5kL4KDt9twaRjYUjwLtwqpYGWSOyFfcY90pRu0gls'], [0, 'AAAAAAAAAAAAAAAAAAAAAFkYbwEAAAAAxl5l%2BDSEnQoW4D4fGb5%2B3equDSM%3D4FUisjbUC5WdRXXGPpCCFoqARzWXtrnRZAmDNsgaoIqNwVaq1S'], [0, 'AAAAAAAAAAAAAAAAAAAAAHMYbwEAAAAAxkTRjFXoKHyKO0tRCLvUUN48wSI%3DBivkNdBQ3jzflvthxAV1PDa3IDMOaXvDN0LoZ4Vs4qds7KWBBp'], [0, 'AAAAAAAAAAAAAAAAAAAAAIcYbwEAAAAAsfQa%2BbD1M9t%2BAWRVwsFWHinBHx4%3DYLkjnhDRITgxgp8GZI6w7jzKOzeJo0lQcbJv30lH2Qmzgfqzia']
    ]
    client_spots_json = json.dumps(client_spots)
    with open(os.path.join(sys.path[0],"bearers_mentions.json"), "w") as file:
        file.write(client_spots_json)
    return

def initialize_update_count():
    with open(os.path.join(sys.path[0], 'update_count.txt'), 'w') as file:
        file.write(str(0))

def prepare():
    with open(os.path.join(sys.path[0],"first_time.txt"), "r") as file:
        string = file.read() 
        if string == "1":
            credentials()
            initialise_hashtag_bearers()
            initialise_mention_bearers()
            initialize_update_count()
            json_handler()
            with open(os.path.join(sys.path[0],"first_time.txt"), "w") as file:
                file.write("buen dia")
        else:
            json_handler()
            ok = 1
    return
