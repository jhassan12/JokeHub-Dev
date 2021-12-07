import requests
from bs4 import BeautifulSoup

class Joke(object):
	def __init__(self, author, content, likes, dislikes):
		self.author = author
		self.content = content
		self.likes = likes
		self.dislikes = dislikes

class LaughFactoryClient(object):
	def __init__(self):
		self.base_url = 'http://www.laughfactory.com/jokes/clean-jokes/'

	def load_data(self, page_num):
		url = self.base_url if page_num == 1 else self.base_url + str(page_num)
		data = requests.get(url)

		if data.status_code != 200:
			return None

		jokes = []

		soup = BeautifulSoup(data.content, 'html.parser')
		joke_containers = soup.find_all(class_="jokes")

		if soup.find(class_='jokes-sec') and 'No jokes found' in soup.find(class_='jokes-sec').text:
			return None

		for joke in joke_containers:
			content, author, likes, dislikes = '', '', '', ''

			if joke.find(class_='joke-msg') and joke.find(class_='joke-msg').find(class_='joke-publisher'):
				author = joke.find(class_='joke-msg').find(class_='joke-publisher').text.strip()

			if joke.find(class_='joke-msg') and joke.find(class_='joke-msg').find(class_='joke-text'):
				content = joke.find(class_='joke-msg').find(class_='joke-text').text.strip()

			if joke.find(class_='likes-dislikes-sec') and joke.find(class_='likes-dislikes-sec').find(class_='like'):
				likes = joke.find(class_='likes-dislikes-sec').find(class_='like').text.strip()

			if joke.find(class_='likes-dislikes-sec') and joke.find(class_='likes-dislikes-sec').find(class_='dislike'):
				dislikes = joke.find(class_='likes-dislikes-sec').find(class_='dislike').text.strip()

			if content and author and likes and dislikes:
				joke = Joke(author, content, likes, dislikes)
				jokes.append(joke)

		return jokes

	def load_pages(self, upper_limit):
		all_jokes = []
		all_joke_contents = set()

		for i in range(1, upper_limit + 1):
			jokes = self.load_data(i)

			if not jokes:
				continue

			for joke in jokes:
				if joke.content not in all_joke_contents:
					all_jokes.append(joke)
					all_joke_contents.add(joke.content)

		next_page = self.load_data(upper_limit + 1)

		return (all_jokes, next_page == None)




		



		

