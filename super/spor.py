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

async def спор(ctx, promt: str, settings: dict = None):
    """Main спор function implementation"""
    try:
        if settings is None:
            settings = {
                'speed': 'medium',
                'permissions': []
            }
        
        models_list = None
        if ':' in promt:
            topic, models_list = promt.split(':', 1)
        else:
            topic = promt

        topic = topic.strip()
        if topic not in answers:
            available_topics = ", ".join(answers.keys())
            await ctx.send(f"❌ Тема не знайдена. Доступні теми: {available_topics}")
            return

        # Process debate settings
        delay = {
            'slow': 2.0,
            'medium': 1.0,
            'fast': 0.5
        }.get(settings.get('speed', 'medium'), 1.0)

        if settings.get('permissions'):
            if 'model_discussion' in settings['permissions']:
                await ctx.send("🤝 Моделі можуть обговорювати між собою")
            if 'question_clarification' in settings['permissions']:
                await ctx.send("❓ Моделі можуть уточнювати питанн��")

        # Process models
        current_models = [m.strip() for m in models_list.split(',')] if models_list else models
        if not all(model in models for model in current_models):
            available_models = ", ".join(models)
            await ctx.send(f"❌ Вказана неправильна модель. Доступні моделі: {available_models}")
            return

        # Get model responses
        model_answers = {}
        for model in current_models:
            await asyncio.sleep(delay)
            model_answers = await process_model_response(ctx, topic, model, model_answers)

        # Check for agreement
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
