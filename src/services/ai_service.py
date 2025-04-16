class AIService:
    @staticmethod
    async def analyze_text(text: str) -> dict:
        """
        Имитация работы AI API с задержкой 1-3 секунды
        """
        import asyncio
        import random

        await asyncio.sleep(random.uniform(1, 3))

        # Простая логика категоризации на основе ключевых слов
        if any(word in text.lower() for word in ["error", "exception", "failed"]):
            category = "critical"
            confidence = random.uniform(0.7, 0.95)
        elif any(word in text.lower() for word in ["warning", "attention", "careful"]):
            category = "warning"
            confidence = random.uniform(0.6, 0.9)
        else:
            category = "info"
            confidence = random.uniform(0.8, 0.99)
        return {
            "category": category,
            "confidence": confidence,
            "keywords": random.sample(text.split(), min(3, len(text.split()))),
        }
