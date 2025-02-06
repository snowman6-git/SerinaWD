const fs = require('fs');
const path = require('path');

import { Database } from "bun:sqlite";
const { DB, TOKEN, CLIENT_ID, GUILD_ID } = require('./config.json');
const { Client, GatewayIntentBits, REST, Routes } = require('discord.js');


const db = new Database(DB)
db.query("drop table community_chat").run()
db.query(`CREATE TABLE IF NOT EXISTS community_chat(id INTEGER PRIMARY KEY AUTOINCREMENT, user text, uid INTEGER, chat text, guild_id INTEGER, created TIMESTAMP DEFAULT CURRENT_TIMESTAMP);`).run()
const client = new Client({
  intents:  [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.GuildMembers,
  ]
});

const commands = [];
const rest = new REST().setToken(TOKEN);

const commandFiles = fs.readdirSync(path.join(__dirname, 'commands')).filter(file => file.endsWith('.js'));
for (const file of commandFiles) {
  const command = require(`./commands/${file}`);
  commands.push(command);
}

async function Command_Setup() {
  try {
    await rest.put(
      Routes.applicationGuildCommands(CLIENT_ID, GUILD_ID),
      { body: commands }
    );
    console.log(`✅ 슬래시 명령어 등록 완료`);
  } catch (error) { console.error('❌ 명령어 등록 실패:', error) }
}

client.on('messageCreate', async(message) => {
  if (message.author.bot) return;
  let text = message.content
  if (message.attachments.size > 0) {
    text += message.attachments.map((attachment) => attachment.proxyURL);
  }
  //나중에 길드별로 테이블할지 결정 id를 기반으로 테이블 2정규화 하기 + sql인젝션 방지(나만 되게) + 쓸만하다 싶으면 닉 말고 전부 id로만
  db.query(`INSERT INTO community_chat(user, uid, chat, guild_id) Values('${message.author.displayName}', '${message.author.id}', '${text}', '${message.guild.id}');`).run()
});

client.on('ready', () => {
  console.log(`✅ ${client.user.tag} 로그인 성공`);
  Command_Setup();
});

client.on('interactionCreate', async interaction => {
  if (!interaction.isCommand()) return;
  const command = commands.find(cmd => cmd.name === interaction.commandName);
  if (command) {
    await command.execute(interaction);
  }
});
client.login(TOKEN);