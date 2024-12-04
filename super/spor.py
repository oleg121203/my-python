from typing import List
from typing import List, Tuple
import discord
from discord.ext import commands
import asyncio

models = ['Mixtral 8x7B', 'Qwen2.5', 'Coder 1.5B']

answers = {
    "AI Libraries": {
        "Mixtral 8x7B": {"answer": "Для створення програми слід використовувати бібліотеку «Mixtral», оскільки вона має дуже швидку роботу та ефективне використання ресурсів."},
        "Qwen2.5": {"answer": "Для створення прогр��ми слід використовувати бібліотеку «Qwen», оскільки вона має дуже добре спроєктовану архітектуру та високий рівень безпеки."},
        "Qwen2.5": {"answer": "Для створення програми слід використовувати бібліотеку «Qwen», оскільки вона має дуже добре спроєктовану архітектуру та високий рівень безпеки."},
    },
    # Додайте тут іншу інформацію
    # Add more information here

questions = {
    "AI Libraries": {
        "Mixtral 8x7B": ["Що таке Mixtral?", "Які переваги має Mixtral?"],
        "Qwen2.5": ["Що таке Qwen?", "Які особливості має Qwen?"],
        "Coder 1.5B": ["Що таке Coder?", "Які можливості має Coder?"]
    },
    # Додайте тут інші питання
}

async def process_model_response(ctx, topic, model, model_answers, question=None):
    """Асинхронна обробка відповіді однієї моделі"""
    model = model.strip()
    answer_data = answers.get(topic, {}).get(model, {})

    if answer_data:
        answer = answer_data.get("answer")
        if question:
            model_answers[model] = {"question": question, "answer": answer}
            await ctx.send(f"Модель {model} на питання '{question}': {answer}")
        else:
            model_answers[model] = answer
            await ctx.send(f"Модель {model}: {answer}")
    else:
        await ctx.send(f"Модель {model} не може відповісти на питання з теми '{topic}'.")

    return model_answers

async def compare_model_answers(ctx, topic, models_list, questions, model_answers):
    """Порівняння відповідей моделей"""
    if len(model_answers) > 1:
        first_model, second_model = [model for model, answer in model_answers.items() if answer is not None]
        first_question, second_question = questions

        if first_question == second_question and first_model != second_model:
            await ctx.send(f"Моделі {first_model} та {second_model} дають різні відповіді на запитання '{first_question}'")
        else:
            await ctx.send(f"Моделі {list(model_answers.keys())} згодні у відповідях на питання '{first_question}'")

async def debate(ctx, prompt: str, questions: List[str] = None, models_list=None):
    if prompt not in answers:
        available_topics = ", ".join(answers.keys())
        await ctx.send(f"Доступні теми: {available_topics}")
        return

    current_models = models_list.split(',') if models_list else models
    model_answers = {}

    tasks = []
    if questions:
        tasks = [
            process_model_response(ctx, prompt, model, model_answers, question)
            for model in current_models
            for question in questions
        ]
    else:
        tasks = [
            process_model_response(ctx, prompt, model, model_answers)
            for model in current_models
        ]

    await asyncio.gather(*tasks)
    await compare_model_answers(ctx, prompt, current_models, questions or [], model_answers)

# Rename спор to use new debate function
async def спор(ctx, prompt: str, models_list=None, questions=None):
    await debate(ctx, prompt, questions, models_list)

models = ['Mixtral 8x7B', 'Qwen2.5', 'Coder 1.5B']

answers = {
    "AI Libraries": {
        "Mixtral 8x7B": {"answer": "Для створення програми слід використовувати бібліотеку «Mixtral», оскільки вона має дуже швидку роботу та ефективне використання ресурсів."},
        "Qwen2.5": {"answer": "Для створення програми слід використовувати бібліотеку «Qwen», оскільки вона має дуже добре спроєктовану архітектуру та високий рівень безпеки."},
        "Coder 1.5B": {"answer": "Для створення програми слід використовувати бібліотеку «Coder», оскільки вона має дуже добре підтримку багатьох мов програмування."}
    },
    "Scraper": [
        {"name": "Я", "answer": "Для створення програми слід використовувати бібліотеку «Scrapy», оскільки вона має дуже добре спроєктовану архітектуру та високий рівень безпеки."},
        {"name": "Модель 2", "answer": "Для створення програми слід використовувати бібліотеку «BeautifulSoup» або «Selenium», оскільки вони мають дуже добре підтримку роботи з веб-сторінками."},
        {"name": "Модель 3", "answer": "Для створення програми слід використовувати бібліотеку «Scrapy» або «Apache Nutch», оскільки вони мають дуже добре спроєктовану архітектуру та високий рівень безпеки."}
    ],
    "BeautifulSoup": [
        {"name": "Я", "answer": "Є надлишкові бібліотеки, такі як «BeautifulSoup», які можуть бути замінені на більш сучасні бібліотеки, такі як «Scrapy» або «Selenium»."},
        {"name": "Модель 2", "answer": "Є надлишков�� бібліотеки, такі як «BeautifulSoup», які повинні бути виключені з програми, оскільки вони не мають ніякої користі."},
        {"name": "Модель 3", "answer": "Є надлишкові бібліотеки, такі як «BeautifulSoup», які можуть бути замінені на більш сучасні бібліотеки, такими як «Scrapy» або «Apache Nutch»."}
    ],
    "Selenium": [
        {"name": "Я", "answer": "Є надлишкові бібліотеки, такі як «Selenium», які повинні бути виключені з програми, оскільки вони не мають ніякої користі."},
        {"name": "Модель 2", "answer": "Є надлишкові бібліотеки, такі як «Selenium», які можуть бути замінені на більш сучасні бібліотеки, такими як «Scrapy» або «BeautifulSoup»."},
        {"name": "Модель 3", "answer": "Є надлишкові бібліотеки, такі як «Selenium», які повинні бути виключені з програми, оскільки вони не мають ніякої користі."}
    ]
}

    # Add other information here
}
questions = {
    "AI Libraries": {
        "Mixtral 8x7B": ["Що таке Mixtral?", "Які переваги має Mixtral?"],
        "Qwen2.5": ["Що таке Qwen?", "Які особлив��сті має Qwen?"],
        "Coder 1.5B": ["Що таке Coder?", "Які можливості має Coder?"]
        "Mixtral 8x7B": ["Що таке Mixtral?", "What are the advantages of Mixtral?"],
        "Qwen2.5": ["What is Qwen?", "What are the features of Qwen?"],
        "Coder 1.5B": ["What is Coder?", "What are the possibilities of Coder?"]
    },
    "Scraper": {
        "Я": ["Що таке Scrapy?", "Які переваги має Scrapy?"],
        "Модель 2": ["Що таке BeautifulSoup?", "Що таке Selenium?"],
        "Модель 3": ["Що таке Apache Nutch?", "Які особливості має Scrapy?"]
    }
    # ...можете добавить вопросы для других категорій
}

async def process_model_response(ctx, topic, model, model_answers):
    """Асинхронная обработка ответа одной модели"""
    # Add other questions here
}

async def process_model_response(ctx, topic: str, model: str, model_answers: dict, question: str = None) -> dict:
    """Asynchronous processing of a single model's response"""
    model = model.strip()
    answer_data = answers.get(topic, {}).get(model, {})

    if answer_data:
        answer = answer_data["answer"]
        model_answers[model] = answer
        await ctx.send(f"Модель {model}: {answer}")

        if topic in questions and model in questions[topic]:
            await ctx.send(f"Додаткові питання від моделі {model}:")
            for question in questions[topic][model]:
                await ctx.send(f"- {question}")

    return model_answers

async def спор(ctx, промт: str, models_list=None):
    if промт not in answers:
        available_topics = ", ".join(answers.keys())
        await ctx.send(f"Доступні теми: {available_topics}")
        return

    current_models = models_list.split(',') if models_list else models
    model_answers = {}

    # Создаем задачи для каждой модели
    tasks = [
        process_model_response(ctx, промт, model, model_answers)
        for model in current_models
    ]

    # Запускаем все задачи параллельно
    await asyncio.gather(*tasks)

    # Проверяем совпадения о��ветов
    for model1, answer1 in model_answers.items():
        for model2, answer2 in model_answers.items():
            if model1 != model2 and answer1.lower() == answer2.lower():
                await ctx.send(f"Суперечка була зупинена! Моделі {model1} та {model2} дійшли згоди.")
                return

    if model_answers:
        await ctx.send("Суперечка триває...")
    else:
        await ctx.send("Не знайдено відповідей для ��казаних моделей.")




        "Mixtral 8x7B": ["Що таке Mixtral?", "What are the advantages of Mixtral?"],
        "Qwen2.5": ["What is Qwen?", "What are the features of Qwen?"],
        "Coder

        answer = answer_data.get("answer")
        if question:
            model_answers[model] = {"question": question, "answer": answer}
            await ctx.send(f"Model {model} on question '{question}': {answer}")
        else:
            model_answers[model] = answer
            await ctx.send(f"Model {model}: {answer}")
    else:
        await ctx.send(f"Model {model} cannot answer the question on topic '{topic}'.")

    return model_answers

async def compare_model_answers(ctx, topic: str, models_list: List[str], questions: List[str], model_answers: dict) -> None:
    """Comparing the answers of models"""
    if len(model_answers) > 1:
        first_model, second_model = [model for model, answer in model_answers.items() if answer is not None]
        first_question, second_question = questions

        if first_question == second_question and first_model != second_model:
            await ctx.send(f"Models {first_model} and {second_model} give different answers on question '{first_question}'")
        else:
            await ctx.send(f"Models {list(model_answers.keys())} agree on answer of question '{first_question}'")

            if all([answer is not None for answer in model_answers.values()]):
                await ctx.send("All models have answered. The debate is over.")
                return

            await asyncio.sleep(5)  # Delay before the next round of debate
            await next_round(ctx, topic, models_list, questions, model_answers)
    elif len(model_answers) == 1:
        model, answer = list(model_answers.items())[0]
        await ctx.send(f"Model {model} answered: {answer}")
        await ctx.send(f"Model {model} is waiting for the next question...")
        if questions:
            await next_round(ctx, topic, models_list, questions, model_answers)
        else:
            await ctx.send("All models have answered. The debate is over.")
    else:
        await ctx.send("No answers found for the specified models.")

async def next_round(ctx, topic, models_list, questions, model_answers):
    # Implement the code for the next round here
    pass

@commands.command()
async def debate(ctx, prompt: str, models_list: str = None, questions: str = None):
    if prompt not in answers:
        available_topics = ", ".join(answers.keys())
        await ctx.send(f"Available topics: {available_topics}")
        return

    current_models = models_list.split(",") if models_list else models
    model_answers = {}

    tasks = []
    if questions:
        questions_list = questions.split(",")
        tasks = [
            process_model_response(ctx, prompt, model, model_answers, question.strip())
            for model in current_models
            for question in questions_list
        ]
    else:
        tasks = [
            process_model_response(ctx, prompt, model, model_answers)
            for model in current_models
        ]

    await asyncio.gather(*tasks)
    await compare_model_answers(ctx, prompt, current_models, questions or [], model_answers)

bot = commands.Bot(command_prefix="!")

bot.command()(debate)

bot.run("your-bot-token")
