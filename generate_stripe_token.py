import stripe
import os

stripe.api_key = os.getenv('STRIPE_TEST_SECRET_KEY')

token = stripe.Token.create(
        card={
                    "number": '4242424242424242',
                    "exp_month": 12,
                    "exp_year": 2018,
                    "cvc": '123'
                },
)

print(token['id'])
