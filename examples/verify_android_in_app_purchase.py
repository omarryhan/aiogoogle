import json
from pprint import pprint
import asyncio
from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds

'''
https://developers.google.com/android-publisher/api-ref/rest/v3/purchases.products/get
'''

service_account_key = json.load(open('test_service_account.json'))

creds = ServiceAccountCreds(
    scopes=[
        'https://www.googleapis.com/auth/androidpublisher'
    ],
    **service_account_key
)


async def verify_purchase(token, package_name, product_id):
    async with Aiogoogle(
            service_account_creds=creds
    ) as aiogoogle:
        publisher_api = await aiogoogle.discover('androidpublisher', 'v3')

        request = publisher_api.purchases.products.get(
            token=token,
            productId=product_id,
            packageName=package_name)

        validation_result = await aiogoogle.as_service_account(
            request,
            full_res=True,
            raise_for_status=False
        )
    pprint(validation_result.content)

if __name__ == "__main__":
    asyncio.run(verify_purchase(
        token='replace_this_with_your_token',
        product_id='replace_this_with_your_product_id',
        package_name='replace_this_with_your_package_name'
    ))
