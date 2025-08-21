import os
import datetime

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import NL2SQLTool
from config import ADVANCED_DB_CONFIG, LLM_MODEL

from src.backend.chat.tools.boxscore import BoxScoreTool

llm = LLM(
	model=LLM_MODEL
)

@CrewBase
class AssistAI():
	"""AssistAI crew"""

	db_uri = f"postgresql://{ADVANCED_DB_CONFIG['user']}:{ADVANCED_DB_CONFIG['password']}@{ADVANCED_DB_CONFIG['host']}/{ADVANCED_DB_CONFIG['dbname']}"
	nl2sql = NL2SQLTool(db_uri=db_uri, result_as_answer=True)
	boxscore_tool = BoxScoreTool(result_as_answer=True)

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# BRANCH 1: SQL + Natural Language
	@agent
	def sql_dev(self) -> Agent:
		return Agent(
			config=self.agents_config['sql_dev'],
			verbose=True,
			tools=[self.nl2sql],
			llm=llm
		)

	@agent
	def writer(self) -> Agent:
		return Agent(
			config=self.agents_config['writer'],
			verbose=True,
			llm=llm
		)
	
	# BRANCH 2: Explicación de términos estadísticos
	@agent
	def stats_explainer(self) -> Agent:
		return Agent(
			config=self.agents_config['stats_explainer'],
			verbose=True,
			llm=llm
		)
	
	# BRANCH 3: Generación de informe de un partido
	@agent
	def boxscore_extractor(self) -> Agent:
		return Agent(
			config=self.agents_config['boxscore_extractor'],
			verbose=True,
			tools=[self.boxscore_tool],
			llm=llm
		)

	@agent
	def report_generator(self) -> Agent:
		return Agent(
			config=self.agents_config['report_generator'],
			verbose=True,
			llm=llm
		)

	# BRANCH 1: SQL + Natural Language
	@task
	def sql_query(self) -> Task:
		return Task(
			config=self.tasks_config['sql_query'],
		)

	@task
	def writer_sql(self) -> Task:
		return Task(
			config=self.tasks_config['writer_sql'],
		)

	# BRANCH 2: Explicación de términos estadísticos
	@task
	def stats_explanation(self) -> Task:
		return Task(
			config=self.tasks_config['stats_explanation'],
		)

	# BRANCH 3: Generación de informe de un partido
	@task
	def boxscore_extraction(self) -> Task:
		return Task(
			config=self.tasks_config['boxscore_extraction'],
		)
	
	@task
	def report_generation(self) -> Task:
		return Task(
			config=self.tasks_config['report_generation'],
		)

	@crew
	def crew_sql(self, id: str) -> Crew:

		self.id = id

		return Crew(
			agents=[
				self.sql_dev(),
				self.writer()
			],
			tasks=[
				self.sql_query(),
				self.writer_sql()
			],
			process=Process.sequential,
			verbose=True
		)
	
	@crew
	def crew_stats(self, id: str) -> Crew:
		self.id = id

		return Crew(
			agents=[
				self.stats_explainer()
			],
			tasks=[
				self.stats_explanation()
			],
			process=Process.sequential,
			verbose=True
		)
	
	@crew
	def crew_boxscore(self, id: str) -> Crew:
		self.id = id

		return Crew(
			agents=[
				self.boxscore_extractor(),
				self.report_generator()
			],
			tasks=[
				self.boxscore_extraction(),
				self.report_generation()
			],
			process=Process.sequential,
			verbose=True
		)

	def create_id(self):
		"""Creates a unique ID for the crew"""
		id = str(hash(datetime.datetime.now().timestamp()))
		if id not in os.listdir("memory"):
			os.mkdir(f"memory/{id}")
		else:
			i = 0
			while id in os.listdir("memory") and i < 5:
				i += 1
				id = str(hash(datetime.datetime.now().timestamp()))
				if id not in os.listdir("memory"):
					os.mkdir(f"memory/{id}")
					break
			if i == 5:
				raise Exception("Could not create a unique ID for the crew")
		return id
	
	def get_branch(self, question: str, context: str) -> str:
		messages = [
            {"role": "system", "content": "You are an expert on conversation flows. Your task is to determine which branch to follow based on the user's question."},
            {"role": "user", "content": f"""
			You are given a question from a user and the context of the conversation (this is the last messages of the conversation) and the user question. You have to take into account that the user question is related to the last messages of the conversation (the last parts of the conversation context), if the user question is just a number, he is selecting an specific question from the last message of the conversation, so take that into account.
            Determine the best branch to follow to answer the user's question.
            There are three branches available:

            1. General: The user is asking anything related to basketball stats, such as player performance, team standings, or game results. For example: "¿Quién es el mejor tirador de 3?", "¿Cuál es el equipo con más victorias esta temporada?"...
            2. Stat Explainer: The user is asking for an explanation of a specific basketball statistic or term. For example: "¿Qué es el PER?", "¿Cómo se calcula el rating ofensivo?"...
            3. Boxscore: The user is asking for a boxscore report of a specific game, and gives the url to that game. For example: "https://www.euroleaguebasketball.net/en/euroleague/game-center/2023-24/real-madrid-panathinaikos-aktor-athens/E2023/333/", "Analiza este partido https://www.euroleaguebasketball.net/en/euroleague/game-center/2023-24/real-madrid-panathinaikos-aktor-athens/E2023/333/"

			Conversation context: {context}
			User question: {question}

			Return the intent as one of the following: 'general' or 'stat_explainer' or 'boxscore'. Respond with only one of these three options, without any additional text or explanation.
            """}
        ]

		response = llm.call(messages=messages)

		return response.strip().lower()
