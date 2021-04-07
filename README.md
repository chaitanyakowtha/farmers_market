###FARMERS MARKET

**BUILDING DOCKER IMAGE**

Execute below command to build the docker image.

<code>docker build -t farmers-market --rm .</code>

**Executing Program from Docker Image**

<code>docker run -i -t farmers-market</code>

**Commands for interacting with App**

<code>checkin</code> to start a new bill & add products.\
<code>print_register</code> to chek a bill (interim).\
<code>finalize</code> to apply discounts & print the bill.

**Note**
* All products related data is available in items.csv
* Discount related data has been generalized & placed in discount.csv 





