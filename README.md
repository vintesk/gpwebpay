# gpwebpay
![Build](https://github.com/filias/gpwebpay/workflows/build/badge.svg)
![Tests](https://github.com/filias/gpwebpay/workflows/tests/badge.svg)
[![codecov](https://codecov.io/gh/filias/gpwebpay/branch/master/graphs/badge.svg?branch=master)](https://codecov.io/github/filias/gpwebpay?branch=master)
[![GitHub contributors](https://img.shields.io/github/contributors/filias/gpwebpay)](https://github.com/filias/gpwebpay/graphs/contributors/)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://https://github.com/psf/black)

GPWebPay Gateway access with python.

* Free software: MIT license

Configuration
-------

Environmental variables needed:
```
GPWEBPAY_MERCHANT_ID = "0987654321"     # Your merchant's id from gpwebpay
GPWEBPAY_MERCHANT_PRIVATE_KEY = ""      # Your merchant's private key base64 encoded (cat gpwebpay-pvk.key | base64 -w0)
GPWEBPAY_PUBLIC_KEY = ""                # GPWebPay's public key base64 encoded (cat gpwebpay-pub.key | base64 -w0)
GPWEBPAY_RESPONSE_URL = ""              # The url for the callback
```
Optional:
```
GPWEBPAY_CURRENCY = "978"                       # If not set EUR is the default currency
GPWEBPAY_DEPOSIT_FLAG = "1"                     # Requests instant payment
GPWEBPAY_MERCHANT_PRIVATE_KEY_PASSPHRASE = ""   # If any
```

To use this package create a GpwebpayClient:

```python
import base64
import os

from gpwebpay import gpwebpay

gw = gpwebpay.GpwebpayClient()

# Get your merchant's private key
private_key = os.getenv("GPWEBPAY_MERCHANT_PRIVATE_KEY")
# Decode your private key with base64
key_bytes = base64.b64decode(private_key)

# Call this method to request a payment to GPWebPay.
# Returns a response, redirect to response.url to go to GPWebPay's and make the payment
# The order_number needs to be unique and the amount in cents.
gw.request_payment(order_numer="123456", amount=999, key_bytes=key_bytes)

# Get GPWebPay's public key
public_key = os.getenv("GPWEBPAY_PUBLIC_KEY")
# Decode it with base64
key_bytes = base64.b64decode(public_key)

# Call this method to verify the response from GPWebPay
# You need to pass here the url you received on the callback
gw.is_response_valid(url, key_bytes=key_bytes)

# Call this method to check the status of a payment (To be implemented)
gw.check_status(order_numer="123456")

```

For more details refer to the [GPWebPay documentation](http://www.gpwebpay.cz/en/Download)


Tests
-------

To run the tests:
```bash
 pytest
 ```


Demo shop
-------

There is a demoshop folder which demonstrates the usage of this package in your webshop.
It is a flask app.

You will need to setup the environmental variables mentioned above for it to work.

To run it locally:
```bash
python demoshop/app.py
```


Development
-------
We use poetry to manage dependencies, packaging and publishing.
If you want to develop locally [install poetry](https://python-poetry.org/docs/#installation) and run:

```bash
poetry install
```


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage