import base64
import logging
import requests
import urllib.parse as urlparse
from collections import OrderedDict
from urllib.parse import parse_qs

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography import x509

from .config import configuration


_logger = logging.getLogger(__name__)


class GpwebpayClient:
    def _create_payment_data(self, order_number="", amount=0):
        """To create the DIGEST we need to keep the order of the params"""
        self.data = OrderedDict()
        self.data["MERCHANTNUMBER"] = configuration.GPWEBPAY_MERCHANT_ID
        self.data["OPERATION"] = "CREATE_ORDER"
        self.data["ORDERNUMBER"] = order_number
        self.data["AMOUNT"] = str(amount)
        self.data["CURRENCY"] = configuration.GPWEBPAY_CURRENCY
        self.data["DEPOSITFLAG"] = configuration.GPWEBPAY_DEPOSIT_FLAG
        self.data["URL"] = configuration.GPWEBPAY_RESPONSE_URL

    def _create_message(self, data):
        # Create message according to GPWebPay documentation (4.1.1)
        message = "|".join(data.values())
        return message.encode("utf-8")

    def _sign_message(self, message_bytes, key_bytes):
        # Sign the message according to GPWebPay documentation (4.1.3)
        # b) Apply EMSA-PKCS1-v1_5-ENCODE
        private_key = serialization.load_pem_private_key(
            key_bytes,
            password=configuration.GPWEBPAY_MERCHANT_PRIVATE_KEY_PASSPHRASE.encode(
                "UTF-8"
            ),
            backend=default_backend(),
        )

        # c) Apply RSASSA-PKCS1-V1_5-SIGN and a) Apply SHA1 algorithm on the digest
        signature = private_key.sign(message_bytes, padding.PKCS1v15(), hashes.SHA1())

        # d) Encode c) with BASE64
        digest = base64.b64encode(signature)

        # Put the digest in the data
        self.data["DIGEST"] = digest

    def _create_callback_data(self, url):
        # All the data is in the querystring
        parsed = urlparse.urlparse(url)
        qs = parse_qs(parsed.query)
        data = {key: value[0] for key, value in qs.items()}
        return data

    def request_payment(self, order_number=None, amount=0, key_bytes=None):
        self._create_payment_data(order_number=order_number, amount=amount)
        message = self._create_message(self.data)
        self._sign_message(message, key_bytes=key_bytes)

        # Send the request
        # TODO: check if we need all these headers
        headers = {
            "accept-charset": "UTF-8",
            "accept-encoding": "UTF-8",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = requests.post(
            configuration.GPWEBPAY_TEST_URL, data=self.data, headers=headers
        )

        return response

    def is_payment_valid(self, url, key_bytes=None):
        """Verify the validity of the response from GPWebPay"""
        data = self._create_callback_data(url)
        digest = data.pop("DIGEST")  # Remove the DIGEST
        digest1 = data.pop("DIGEST1")  # Remove the DIGEST1
        # TODO: check with DIGEST1
        message = self._create_message(data)

        # Decode the DIGEST using base64
        signature = base64.b64decode(digest)

        # Load the public key
        public_key = x509.load_pem_x509_certificate(
            key_bytes, backend=default_backend(),
        ).public_key()

        # Verify the message
        try:
            public_key.verify(signature, message, padding.PKCS1v15(), hashes.SHA1())
            return True
        except InvalidSignature:
            return False
