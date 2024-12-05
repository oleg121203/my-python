from typing import List
import discord
from discord.ext import commands
import asyncio
from config import models, answers, questions, debate_settings, debate_history

async def process_model_response(ctx, topic: str, model: str, model_answers: dict, question: str = None) -> dict:
    try:
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
    except Exception as e:
        print(f"Error in process_model_response: {e}")
        return model_answers

async def спор(ctx, prompt):
    try:
        if ':' not in prompt:
            available_topics = ", ".join(answers.keys())
            await ctx.send(f"Використання: /спор <тема>:<модель1>,<модель2>\nДоступні теми: {available_topics}")
            return

        topic, models_str = prompt.split(':', 1)
        selected_models = [m.strip() for m in models_str.split(',')]

        if topic not in answers:
            await ctx.send(f"Тема '{topic}' не знайдена")
            return

        for model in selected_models:
            if model not in models:
                await ctx.send(f"Модель '{model}' не знайдена")
                return

        # Send responses from each model
        for model in selected_models:
            answer = answers[topic][model]["answer"]
            await ctx.send(f"**{model}**: {answer}")

    except Exception as e:
        await ctx.send(f"Помилка: {str(e)}")
