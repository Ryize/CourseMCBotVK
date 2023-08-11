import os

from yookassa import Payment, Configuration
import uuid
Configuration.account_id = os.environ.get('SHOP_ID')
Configuration.secret_key = os.environ.get('SECRET_KEY')


def get_payment_url(amount):
    idempotence_key = str(uuid.uuid4())
    quantity = int(amount / 50)
    payment = Payment.create({
        'amount': {
            'value': f'{amount}',
            'currency': 'RUB'
        },
        'confirmation': {
            'type': 'redirect',
            'return_url': 'https://coursemc.ru/billing/success/'
        },
        'description': 'Оплата занятий',
        'receipt': {
            'email': 'chekashovmatvey@gmail.com',
            'items': [
                {
                    'description': 'Урок',
                    'amount': {
                        'value': '50',
                        'currency': 'RUB'
                    }, 'vat_code': 1,
                    'quantity': quantity}],
            'tax_system_id': 1,
        }
    }, idempotence_key)

    return payment.confirmation.confirmation_url
