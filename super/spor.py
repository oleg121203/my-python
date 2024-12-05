from typing import List
import discord
from discord.ext import commands
import asyncio
from config import models, answers, questions

async def process_model_response(ctx, topic: str, model: str, model_answers: dict, question: str = None) -> dict:
    """Asynchronous processing of a single model's response"""
    model = model.strip()
    answer_data = answers.get(topic, {}).get(model, {})
    model = model
    if answer_data:
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
    if answer
    return model_answers
    return model_answers


    try:
        if ':' in промт:
            промт, models_list = промт.split(':', 1)
        
        промт = промт.strip()
        if промт not in answers:
            available_topics = ", ".join(answers.keys())
            await ctx.send(f"❌ Тема не знайдена. Доступні теми: {available_topics}")
            return

        current_models = [m.strip() for m in models_list.split(',')] if models_list else models
        if not all(model in models for model in current_models):
            available_models = ", ".join(models)
            await ctx.send(f"❌ Вказана неправильна модель. Доступні моделі: {available_models}")
            return

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

    except Exception as e:
        await ctx.send(f"❌ Помилка: {str(e)}")
        await ctx.send("Використання: /спор <тема> або /спор <тема>:<модель1>,<модель2>")
        await ctx.send("Використання: /спор <тема> або /спор <тема>:<модель1>,<модель2>")
        await ctx.send("Використання: /спор <тема> або /спор <тема>:<модель1>,<модель2>")
        await ctx.send("Використання: /спор <тема> або /спор <тема>:<модель1>,<модель2>")
