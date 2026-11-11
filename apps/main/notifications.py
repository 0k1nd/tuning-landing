"""Уведомления о новых заявках.

Пока только запись в лог (в разработке — консоль). Рабочий канал (почта, Telegram, CRM)
и способ отправки (Celery или синхронно) ещё не выбраны — подключаются здесь.
"""

import logging

from apps.main.models import Lead

logger = logging.getLogger(__name__)


def notify_new_lead(lead: Lead) -> None:
    logger.info(
        "Новая заявка #%s: %s, %s, модель: %s, источник: %s",
        lead.pk,
        lead.name,
        lead.phone,
        lead.car_model or "—",
        lead.source or "—",
    )
