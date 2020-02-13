import discord
from discord import utils
import pyowm
import config #скрыт

class MyClient(discord.Client):
	async def on_ready(self):	#проверка включения
		print('Logged on as {0}!'.format(self.user))

	async def on_raw_reaction_add(self, payload):	#добавление реакции
		if payload.message_id == config.POST_ID:
			channel = self.get_channel(payload.channel_id)	# получаем объект канала
			message = await channel.fetch_message(payload.message_id)	# получаем объект сообщения
			member = utils.get(message.guild.members, id=payload.user_id)	# получаем объект пользователя который поставил реакцию

			try:
				emoji = str(payload.emoji)	# эмоджик который выбрал юзер
				role = utils.get(message.guild.roles, id=config.ROLES[emoji])	# объект выбранной роли (если есть)
			
				if(len([i for i in member.roles if i.id not in config.EXCROLES]) <= config.MAX_ROLES_PER_USER):
					await member.add_roles(role)
					print('[SUCCESS] User {0.display_name} has been granted with role {1.name}'.format(member, role))
				else:
					await message.remove_reaction(payload.emoji, member)
					print('[ERROR] Too many roles for user {0.display_name}'.format(member))
			
			except KeyError as e:
				print('[ERROR] KeyError, no role found for ' + emoji)
			except Exception as e:
				print(repr(e))

	async def on_raw_reaction_remove(self, payload):	#удаление реакции
		channel = self.get_channel(payload.channel_id)	# получаем объект канала
		message = await channel.fetch_message(payload.message_id)	# получаем объект сообщения
		member = utils.get(message.guild.members, id=payload.user_id)	# получаем объект пользователя который поставил реакцию

		try:
			emoji = str(payload.emoji)	# эмоджик который выбрал юзер
			role = utils.get(message.guild.roles, id=config.ROLES[emoji])	# объект выбранной роли (если есть)

			await member.remove_roles(role)
			print('[SUCCESS] Role {1.name} has been remove for user {0.display_name}'.format(member, role))

		except KeyError as e:
			print('[ERROR] KeyError, no role found for ' + emoji)
		except Exception as e:
			print(repr(e))

	async def on_message(self, message):	 #обработка сообщений
		if message.content.startswith('!W'):	#если !W
			msg = message.content[3:]		#текст сообщения без команды
			owm = pyowm.OWM( config.TOKEN_OWM, language = "ru")		#объект погоды
			channel = message.channel	#объект канала
			try:
				observation = owm.weather_at_place(msg)		#поиск города
				w = observation.get_weather()	#информация о погоге
				temp = w.get_temperature('celsius')["temp"]		#температура
				answer = "В городе " + msg + " сейчас " + w.get_detailed_status() + "\n"
				answer += "Температура: " + str(temp) + "\n\n"	#составляем ответ
				if temp < 0:
					answer += "Очень холодно!"
				elif temp < 10:
					answer += "Холодно."
				elif temp < 20:
					answer += "Прохладно."
				else:
					answer += "Нормально."
				print("\n" + answer)	#ответ в консоль
				await channel.send(answer)	#ответ в канал
			except pyowm.exceptions.api_response_error.NotFoundError: #ошибка поиска
				await channel.send("Локация *{}* не найдена!".format(msg))	

	async def on_member_remove(self, member):	#выход пользователя
		channel = self.get_channel(config.CHANNAL_MAIN_ID)		#объект канала по ID
		print("\n *{}* вышел.".format(member.display_name))			#вывод в консоль вышедшего
		await channel.send("*{}* вышел.".format(member.display_name))		#вывод в канал вышедшего
		
# RUN
client = MyClient()
client.run(config.TOKEN)

#pyinstaller -F -i "E:\Code Dev\py\Discord Bot\Discord Bot\ico.ico" Discord_Bot.py
#компиляция в .exe