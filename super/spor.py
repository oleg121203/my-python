from typing import List
import discord
from discord.ext import commands
import asyncio

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
        {"name": "Модель 2", "answer": "Є надлишкові бібліотеки, такі як «BeautifulSoup», які повинні бути виключені з програми, оскільки вони не мають ніякої користі."},
        {"name": "Модель 3", "answer": "Є надлишкові бібліотеки, такі як «BeautifulSoup», які можуть бути замінені на більш сучасні бібліотеки, такими як «Scrapy» або «Apache Nutch»."}
    ],
    "Selenium": [
        {"name": "Я", "answer": "Є надлишкові бібліотеки, такі як «Selenium», які повинні бути виключені з програми, оскільки вони не мають ніякої користі."},
        {"name": "Модель 2", "answer": "Є надлишкові бібліотеки, такі як «Selenium», які можуть бути замінені на більш сучасні бібліотеки, такими як «Scrapy» або «BeautifulSoup»."},
        {"name": "Модель 3", "answer": "Є надлишкові бібліотеки, такі як «Selenium», які повинні бути виключені з програми, оскільки вони не мають нія��ої користі."}
    ]
}

questions = {
    "AI Libraries": {
        "Mixtral 8x7B": ["Що таке Mixtral?", "Які переваги має Mixtral?"],
        "Qwen2.5": ["Що таке Qwen?", "Які особливості має Qwen?"],
        "Coder 1.5B": ["Що таке Coder?", "Які можливості має Coder?"]
    },
    "Scraper": {
        "Я": ["Що таке Scrapy?", "Які переваги має Scrapy?"],
        "Модель 2": ["Що таке BeautifulSoup?", "Що таке Selenium?"],
        "Модель 3": ["Що таке Apache Nutch?", "Які особливості має Scrapy?"]
    }
}


async def process_model_response(ctx, topic: str, model: str, model_answers: dict, question: str = None) -> dict:
    """Asynchronous processing of a single model's response"""
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


async def спор(ctx, промт: str, models_list=None):
    if промт not in answers:
        available_topics = ", ".join(answers.keys())
        await ctx.send(f"Доступні теми: {available_topics}")
        return

    current_models = models_list.split(',') if models_list else models
    model_answers = {}

    tasks = [
        process_model_response(ctx, промт, model, model_answers)
        for model in current_models
    ]

    await asyncio.gather(*tasks)

    for model1, answer1 in model_answers.items():
        for model2, answer2 in model_answers.items():
            if model1 != model2 and answer1.lower() == answer2.lower():
                await ctx.send(f"Суперечка була зупинена! Моделі {model1} та {model2} дійшли згоди.")
                return

    if model_answers:
        await ctx.send("Суперечка триває...")
    else:
        await ctx.send("Не знайдено відповідей для вказаних моделей.")
