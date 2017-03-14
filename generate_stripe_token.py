import stripe
stripe.api_key = "sk_test_T86oR2vE8opYYtbfbYRV6Oz9"

token = stripe.Token.create(
        card={
                    "number": '4242424242424242',
                    "exp_month": 12,
                    "exp_year": 2018,
                    "cvc": '123'
                },
)

print(token['id'])
