import re
import math
import random
from telegram import Update, User, constants
from telegram.ext import CallbackContext
from commands.scoreboard import get_user_level
from commands.utils.warnings import *


class WilduWeapon:

    def __init__(self, name, taivutus, level, damage):
        self.name = name
        self.taivutus = taivutus
        self.level = level
        self.damage = damage

LOOTBOX_PRICE = 50

WEAPON_DROP_LIST = [
    WilduWeapon('Penis', 'Peniksellä', 1, 2),
    WilduWeapon('Penis123', 'Peniksellä 123', 123, 3),
    WilduWeapon('Kirves', 'Kirveellä', 4, 4),
    WilduWeapon('Lapio', 'Lapiolla', 3, 3),
    WilduWeapon('Aamutähti', 'Aamutähdellä', 12, 3),
    WilduWeapon('Rynnäkkökivääri', 'Rynnäkkökiväärillä', 762, 4),
    WilduWeapon('Rynnäkkökonekivääri', 'Rynnäkkökonekiväärillä', 69, 5),
    WilduWeapon('Taikasauva', 'Taikasauvalla', 1, 2),
    WilduWeapon('Pesäpallomaila', 'Pesäpallomailalla \(BONK\)', 8, 3),
    WilduWeapon('Sorkkarauta', 'Sorkkaraudalla', 3, 3),
    WilduWeapon('Golfmaila', 'Golfmailalla', 9, 3),
    WilduWeapon('Löylykauha', 'Löylykauhalla', 12, 2),
    WilduWeapon('Harja', 'Harjalla', 2, 2),
    WilduWeapon('Näppäimistö', 'Näppäimistöllä', 2, 2),
    WilduWeapon('SarmatOhjusEliNatoKoodillaSatan2', 'Saatanalla', 666, 10),
    WilduWeapon('Akkuporakone', 'Akkuporakoneella', 13, 3),
    WilduWeapon('Soppatykki', 'Soppatykillä', 2, 4),
    WilduWeapon('kaljapullo', 'Käyttäen ammuksina 33cl kaljapulloja', 33, 5),
    WilduWeapon('Ruoska', 'Ruoskalla \(ihana julmuri\)', 88, 2),
    WilduWeapon('Miketsu', 'Miketsulla', 21, 3),
    WilduWeapon('Lutku', 'Lutkulla', 10, 2),
    WilduWeapon('Spärderi', 'Spärderillä', 10, 2),
    WilduWeapon('Paistinpannu', 'Paistinpannulla \(KLONG\)', 15, 3),
    WilduWeapon('Mutsis', 'Mutsis\-vitsillä \(räh\)', 69, 1),
    WilduWeapon('Leka', 'Lekalla', 2, 4),
    WilduWeapon('Rankaisuväline', 'Rankaisuvälineellä', 4, 4),
    WilduWeapon('ThinkPad™', 'ThinkPadilla™', 2001, 6),
    WilduWeapon('Daevvoo', 'Daevvoolla', 3, 4),
    WilduWeapon('Kuolemanshotti', 'Kuoleman shotilla', 66, 4),
    WilduWeapon('Kivimiekka', 'Kivimiekalla \(PVPkivaa\)', 12, 2),
    WilduWeapon('Patonki🇫🇷', 'Patongilla🇫🇷', 42, 0),
    WilduWeapon('Lusikka', 'Lusikalla', 0, 1),
    WilduWeapon('Tuikutin', 'Tuikuttimella', 8, 4),
    WilduWeapon('Timuhakku', 'Timuhakulla', 16, 3),
    WilduWeapon('Ilmakivääri', 'Ilmakiväärillä', 12, 3),
    WilduWeapon('Katupora', 'Katuporalla', 23, 3),
    WilduWeapon('SeVitunBigFuckingGunBFGSiitDoomista', 'Sillä vitun BFGllä Doomista', 666, 12),
]

VERB_LIST = [
    'läimäytti',
    'läsäytti',
    'täräytti',
    'töytäisi',
    'huitaisi',
    'ampui',
    'mankeloi',
    'rasautti',
    'lasautti',
    'jymäytti',
    'jysäytti',
    'rankaisi',
    'rutisti',
    'lakaisi',
    'haravoi',
    'haavoitti',
    'viihdytti',
    'tyydytti',
    'luikautti',
    'täränti',
    'kurmuutti',
    'sujautti',
    'paukautti',
    'kuristi',
    'lävisti',
    'kumautti',
    'poistutti',
    'simputti',
    'kiustasi',
    'hankasi',
    'hieroi',
    'ravisti',
    'servasi',
    'PK:tti',
    'uunitti',
    'lennätti',
    'näytti kaapin paikan',
    'heilautti',
    'ruikautti',
    'frägäsi',
    'palkitsi',
    'ruoski',
    'julmuroi',
    'pahoinpiteli',
    'kaltoinkohteli',
    'kolautti',
    'kolasi',
    'hävitti',
    'poisthi',
    'kelasi',
    'ryysti',
    'rippasi',
    'simppasi',
    'paijasi',
    'silitti',
    'tasoitti',
    'viilasi',
    'hoiteli',
    'voiteli',
    'rasvasi',
    'pisti purukaluston uusiksi',
    'antoi tukkapöllyä',
    'näytti tupenrapinat',
    'aktivoi kiveskiertymän',
    'väänsi rusetille',
    'toimitti',
    'ryyppäsi',
    'sagetti',
    'hidetti',
    'vasaroi',
    'porasi',
    'päräytti',
    'käräytti',
    'räjäytti',
    'niisti',
    'litisti',
    'paukutti',
    'tuhosi',
    'murhasi',
    'viipaloi',
    'siipaloi',
    'PISTI PASKAT PINOON',
    'viikkasi',
    'väänsi paskat pihalle',
    'kiillotti',
]

class WilduPlayer:

    def __init__(self, user: User, context):
        self.user = user
        self.id = user.id
        self.name = user.first_name
        self.tag = user.mention_markdown_v2(name=user.name)

        self.weapon_inventory = [WilduWeapon('nyrkki', 'nyrkillä', 1, 1)]
        self.misc_inventory = []
        self.hp = self.get_max_hp(context)
        self.gold = 50
        self.equip_weapon_idx = 0

    def get_max_hp(self, context):
        level = get_user_level(context, self.id)
        return level * 10

    def equipped_weapon(self):
        return self.weapon_inventory[self.equip_weapon_idx]

    def get_damage(self, context):
        level = get_user_level(context, self.id)
        base = level * 1
        multiplier = self.equipped_weapon().damage
        rigged = random.random()
        if rigged < 0.1:
            return 0
        else:
            return int(rigged * base * multiplier)

    def change_weapon(self, weapon_name):
        index = None
        for i, weapon in enumerate(self.weapon_inventory):
            if weapon_name == weapon.name:
                index = i
        if index is not None:
            self.equip_weapon_idx = index
            return True
        else: return False
    
    def damage(self, damage):
        # Returns wether alive or dead after damage
        self.hp -= int(damage)
        self.hp = int(self.hp)
        if self.hp <= 0:
            self.hp = 0
            return False
        return True


class Wildu:

    def __init__(self):
        self.players = []

    async def reward_player(self, player, modifier, context, chat_id):
        gold_added = random.randint(int(modifier / 2), int(modifier * 2))
        player.gold += gold_added
        await context.bot.send_message(chat_id=chat_id,
            text=f"{player.tag} loottasi ruumiista {gold_added} kultakolikkoa\!\!",
            parse_mode=constants.ParseMode.MARKDOWN_V2)
    
    def find_player_by_id(self, id):
        plr = None
        for player in self.players:
            if player.id == id:
                plr = player
        return plr
    
    async def buy_lootbox(self, buyer_id, context, chat_id):
        buyer = self.find_player_by_id(buyer_id)
        if buyer is None:
            await context.bot.send_message(chat_id=chat_id,
                text='Sinun on ensin liityttävä Wilduun')
            return
        
        if buyer.gold < LOOTBOX_PRICE:
            await context.bot.send_message(chat_id=chat_id,
                text=f'Liian vähän rahaa\! Tarvitset {LOOTBOX_PRICE} kolikkoa')
            return

        buyer.gold -= LOOTBOX_PRICE
        drop = random.choice(WEAPON_DROP_LIST)
        buyer.weapon_inventory.append(drop)
        
        await context.bot.send_message(chat_id=chat_id,
            text=f'{buyer.tag} avasi LootBoxin™ ja sieltä paljastui\.\.\.\n'\
                +f'**{drop.name}** \(lvl\. {drop.level}\) \!\!\n\n'\
                +f'Ota käyttöön uusi aseesi /wildu equip {drop.name}',
            parse_mode=constants.ParseMode.MARKDOWN_V2)

    
    async def hit_player(self, hitter_id, target: str, context, chat_id):
        hitter = self.find_player_by_id(hitter_id)

        if hitter is None:
            await context.bot.send_message(chat_id=chat_id,
                text='Sinun on ensin liityttävä Wilduun')
            return

        target_player = None
        target_idx = None
        for i, player in enumerate(self.players):
            if player.name == target:
                target_player = player
                target_idx = i
        
        if target_player is not None:
            damage = hitter.get_damage(context)
            weapon = hitter.equipped_weapon()
            target_alive = target_player.damage(damage)
            if not target_alive:
                post_script = f' {target_player.name} menetti henkensä ja poistettiin wildusta\!'
                self.players.pop(target_idx)
            else:
                post_script = f' {target_player.hp} HP jäljellä\.'
            
            if damage <= 0:
                text = 'You missed\.'
            else:
                verb = random.choice(VERB_LIST)
                text = f'{hitter.tag} {verb} käyttäjää {target_player.tag} {weapon.taivutus} '\
                    + f'\(lvl\. {weapon.level}\) ja aiheutti {damage} vahinkoa\!'\
                    + post_script
            
            print(text)
            await context.bot.send_message(chat_id=chat_id,
                text=text,
                parse_mode=constants.ParseMode.MARKDOWN_V2)

            if not target_alive:
                await self.reward_player(hitter, get_user_level(context, target_player.id),
                    context, chat_id)

        else:
            await context.bot.send_message(chat_id=chat_id,
                text=f"{hitter.tag} yritti lyödä {target}, mutta käyttäjää ei löytynyt\!",
                parse_mode=constants.ParseMode.MARKDOWN_V2)
    
    def generate_scoreboard(self, context):
        board = 'Wildussa seikkailee:\n\n'
        for player in self.players:
            level = get_user_level(context, player.id)
            board += f'Lvl {level} {player.name}\n'\
                   + f'HP: {player.hp}\n'\
                   + f'Kultaa: {player.gold} kolikkoa\n'\
                   + f'Aseistus: \n'\
                   + '\n'.join([f'  {w.name} \(lvl\. {w.level}\)' for w in player.weapon_inventory])\
                   + '\n\n'
        return board

def get_wildu(context):
    wildu = context.chat_data.get('wildu', None)
    if wildu is None:
        wildu = Wildu()
        context.chat_data['wildu'] = wildu
    return wildu


async def wildu_scoreboard(update: Update, context):
    wildu = get_wildu(context)
    await context.bot.send_message(chat_id=update.effective_chat.id,
        text=wildu.generate_scoreboard(context),
        parse_mode=constants.ParseMode.MARKDOWN_V2)


async def wildu_join(update: Update, context):
    wildu = get_wildu(context)
    user = update.effective_user
    args = context.args
    if len(args) != 1:
        await warning_wrong_number_of_args(update, context)
        return
    if user is None:
        await warning_unknown(update, context)
        return

    existing = wildu.find_player_by_id(user.id)
    if existing is None:
        wildu.players.append(WilduPlayer(user, context))
        await context.bot.send_message(chat_id=update.effective_chat.id,
            text=f"{user.first_name} on saapunut PK\-seudulle\.\.\.",
            parse_mode=constants.ParseMode.MARKDOWN_V2)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
            text=f"{user.first_name} on jo PK\-seudulla\.\.\.",
            parse_mode=constants.ParseMode.MARKDOWN_V2)


async def wildu_reset(update, context):
    wildu = Wildu()
    context.chat_data['wildu'] = wildu
    await context.bot.send_message(chat_id=update.effective_chat.id,
        text=f"PK\-seutu resetoitu\.\.\.",
        parse_mode=constants.ParseMode.MARKDOWN_V2)


async def wildu_lootbox(update, context):
    wildu = get_wildu(context)
    user = update.effective_user
    await wildu.buy_lootbox(user.id, context, update.effective_chat.id)


async def wildu_attack(update, context):
    wildu = get_wildu(context)
    args = context.args
    user = update.effective_user
    if len(args) != 2:
        await warning_wrong_number_of_args(update, context)
        return
    if user is None:
        await warning_unknown(update, context)
        return

    attacker_id = user.id
    target_name = args[1]
    await wildu.hit_player(attacker_id, target_name, context, update.effective_chat.id)


async def wildu_equip(update, context):
    wildu = get_wildu(context)
    args = context.args
    user = update.effective_user
    if len(args) != 2:
        await warning_wrong_number_of_args(update, context)
        return
    if user is None:
        await warning_unknown(update, context)
        return

    user_id = user.id
    player = wildu.find_player_by_id(user_id)
    weapon_name = args[1]
    success = player.change_weapon(weapon_name)

    if success:
        await context.bot.send_message(chat_id=update.effective_chat.id,
            text=f"{player.tag} ottaa käyttöönsä {weapon_name}",
            parse_mode=constants.ParseMode.MARKDOWN_V2)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
            text=f"Asetta ei löydy\?",
            parse_mode=constants.ParseMode.MARKDOWN_V2)


HELP_TEXT = 'Käyttö: \n'\
    +f'/wildu reset [RESETOI WILDUN ESIM PÄIVITYKSIEN JÄLKEEN]\n'\
    +f'/wildu join\n'\
    +f'/wildu lootbox\n'\
    +f'/wildu attack <pelaajanimi>\n'\
    +f'/wildu equip <aseen nimi>\n'\
    +f'/wildu scoreboard\n'
COMMANDS = {
    'reset': wildu_reset,
    'join': wildu_join,
    'lootbox': wildu_lootbox,
    'attack': wildu_attack,
    'equip': wildu_equip,
    'scoreboard': wildu_scoreboard
}
async def cmd_wildu(update: Update, context):
    args = context.args
    if len(args) == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=HELP_TEXT)
        return
    
    if args[0] in COMMANDS:
        await COMMANDS[args[0]](update, context)