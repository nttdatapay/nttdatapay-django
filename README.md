# nttdatapay-django

## Prerequisites
- UAT MID and keys will be provided by the NTT DATA Payment Services.

## Installation
1. Use the below commands to install pycryptodome and requests package
    - Install `pycryptodome` for encryption and decryption
        ```
        pip install pycryptodome
        ```
    
    - Install `requests` for rest API calling
        ```
        pip install requests
        ```

2. Modify the `atompay/views.py` file
    - Change the configuration details like merchId, password, product etc. in payview method.
    - Configure `authurl` according to UAT and Production environments.
    - This function includes the AUTH api call which will generate an atomtokenid. 
    - In resp(), change the response key provided by NDPS. This method will help to handle the response.

3. Add the `cacert.pem` in atompay directory.

4. Modify `atompay/templates/base.html`
    - Configure the atomcheckout.js in accordance with UAT and Production environments.
    - openpay() will open the NTT DATA Payment Page.

5. Modify `atompay/templates/response.html`
    - response.html is used to get the response details after the transaction is completed.

