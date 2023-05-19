import discord
import os
import gspread
from dotenv import load_dotenv, find_dotenv

def user_index(user_name, dict_list):
    counter=0
    
    for dict in dict_list:
        if user_name == dict['Nome']:
            return counter 
        counter+=1   
        
    return -1
        

load_dotenv(find_dotenv())

SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE')
TOKEN = os.getenv('TOKEN')

gc = gspread.service_account(CREDENTIALS_FILE)
sh = gc.open_by_key(SPREADSHEET_ID)

wsheet = sh.sheet1

DICT = wsheet.get_all_records()

intents = discord.Intents.all()
client = discord.Client(intents=intents)

#bot entrando no servidor
@client.event
async def on_guild_join(guild):
    await guild.system_channel.send('wassup')

#reagindo a mensagens
@client.event
async def on_message(message):
    DICT = wsheet.get_all_records()
    
    if message.author == client.user:
        return
    
    if message.content.startswith('!help'):
        text = await message.channel.send('''!create_account <user> <idade> <balanço (BRL)> - Adiciona uma conta na planilha 
                                          \n!check_user_info <user> - Verifica os dados do usuário
                                          \n!delete_account <user> - Deleta conta
                                          \n!get_balance <user> - Verifica balanço da conta
                                          \n!total_balance - Verifica todo o balanço gerido (BRL)''')
        await text.add_reaction('\U0001f44d')
        
    elif message.content.startswith('!get_balance'):
        text = message.content.split(' ')
        
        if len(text) != 2 or text[0] != '!get_balance':
            await message.channel.send("Formato incorreto")
            return
        
        user = text[1]
        
        user_idx= user_index(user, DICT)
        
        if user_idx != -1:
            await message.channel.send(DICT[user_idx]['Balanço (BRL)'])
        else:
            await message.channel.send("Usuário não existe")
            
    elif message.content.startswith("!create_account"):
        text = message.content.split(' ')
        
        if len(text) != 4 or text[0] != "!create_account":
            
            await  message.channel.send("formato: !create_account <user> <idade> <balanço (BRL)>")
            return
        
        name = text[1]
        age = text[2]
        balance = text[3]
        
        if user_index(name, DICT) != -1:
            await message.channel.send('Este usuário já existe!')
            return
        
        row = len(DICT) + 2
        
        new_dict = {'Nome': name, 'Idade': age, 'Balanço (BRL)': balance}
        
        DICT.append(new_dict)
        
        for i in range(3):
            wsheet.update_cell(row, i+1, text[i+1])
        
        print(DICT)
        
        await message.channel.send('I updated the worksheet :)')
        
    elif message.content.startswith('!delete_account'):
        text = message.content.split(' ')
        
        user_idx = user_index(text[1], DICT)
        
        if len(text) != 2 or text[0] != '!delete_account':
            ##continuar
            return
        
        if user_idx == -1:
            await message.channel.send('Este usuário não existe')
            return
        
        wsheet.delete_rows(user_idx + 2)
        await message.channel.send('Conta deletada.')
        
    elif message.content.startswith('!check_user_info'):
        text = message.content.split(' ')
        
        if len(text) != 2 or text[0] != '!check_user_info':
            await  message.channel.send("formato: !check_user_info <user>")
            return
        
        user = text[1]
        
        idx = user_index(user, DICT)
        
        if idx == -1:
            await message.channel.send('Este usuário não existe!')
            return
        
        await message.channel.send(DICT[idx])
        
    elif message.content.startswith('!total_balance'):
        if(message.content != '!total_balance'):
            await message.channel.send('Este comando nao aceita parametros!')
            return
        
        sum=0
        for i in range(len(DICT)):  
            sum += DICT[i]['Balanço (BRL)']
        
        await message.channel.send('Balanço total gerido (BRL): {}'.format(sum))
        
client.run(TOKEN)


