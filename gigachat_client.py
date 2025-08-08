"""
Клиент для работы с API ГигаЧат
"""

import asyncio
import logging
import httpx
from typing import Optional
import config

logger = logging.getLogger(__name__)

class GigaChatClient:
    def __init__(self):
        self.token = config.GIGACHAT_TOKEN
        self.base_url = config.GIGACHAT_BASE_URL
        self.scope = config.GIGACHAT_SCOPE
        self.access_token = None

    async def _get_access_token(self) -> str:
        """Получение access token для ГигаЧат API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Accept": "application/json",
                        "RqUID": "6f0b1291-c7f3-43c6-bb2e-9f3efb2dc98e",
                        "Authorization": f"Basic {self.token}"
                    },
                    data={
                        "scope": self.scope
                    }
                )

                if response.status_code == 200:
                    token_data = response.json()
                    return token_data["access_token"]
                else:
                    raise Exception(f"Ошибка получения токена: {response.text}")

        except Exception as e:
            logger.error(f"Ошибка аутентификации ГигаЧат: {e}")
            raise

    async def generate_answer(self, question: str, context: str) -> str:
        """Генерация ответа на основе вопроса и контекста"""
        if not self.access_token:
            self.access_token = await self._get_access_token()

        prompt = self._build_prompt(question, context)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "Authorization": f"Bearer {self.access_token}"
                    },
                    json={
                        "model": "GigaChat",
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.1,
                        "max_tokens": 1000
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    logger.error(f"Ошибка API ГигаЧат: {response.text}")
                    return "Извините, произошла ошибка при получении ответа от ИИ."

        except Exception as e:
            logger.error(f"Ошибка генерации ответа: {e}")
            return "Извините, произошла ошибка при обращении к ИИ."

    def _build_prompt(self, question: str, context: str) -> str:
        """Формирование промпта для ГигаЧат"""
        return f"""Ты - умный ассистент компании CAPSULAhair, специализирующейся на парикмахерских услугах.

Отвечай на вопросы клиентов, используя только предоставленную информацию из базы знаний.

Контекст из базы знаний:
{context}

Вопрос клиента: {question}

Требования к ответу:
1. Отвечай только на основе предоставленного контекста
2. Если информации недостаточно, честно скажи об этом
3. Будь дружелюбным и профессиональным
4. Структурируй ответ для лучшего восприятия
5. Если уместно, предложи дополнительные варианты

Ответ:"""
