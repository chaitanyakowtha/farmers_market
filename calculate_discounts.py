import pandas as pd
from basket_bill import Product

class Discount:
    """
    Utilized for computing discounts. Requires product volume dictionary for creating an object.
    """
    def __init__(self, discounts_file_name):
        # self.basket = basket
        self.discounts = self.read_discounts(discounts_file_name)

    def read_discounts(self, file_name):
        """
        Reads the discounts csv file & returns a dataframe
        :param file_name: Discounts CSV filename
        :return: Pandas dataframe of discounts data
        """
        discounts = pd.read_csv(f'{file_name}.csv')

        return discounts

    def get_product_vs_offer_and_volume(self, df):
        """
        Consumes discount dataframe & returns multiple metadata from it
        :param df: discount dataframe
        :return: product_vs_min_volume: Dict: Each product code vs Min volume required for applying discount
        :return: product_offer: Dict: Product vs Offer available mapping
        :return: base_product_vs_offer_product: Dict: Product vs Offer-On (which product) mapping
        """

        product_vs_min_volume = {}
        product_offer = {}
        base_product_vs_offer_product = {}

        for i in df.itertuples():
            product_vs_min_volume[i[4].lower()] = i[5]
            product_offer[i[4].lower()] = i[1]
            base_product_vs_offer_product[i[4].lower()] = i[7].lower()

        return product_vs_min_volume, product_offer, base_product_vs_offer_product

    def get_applicable_discounts(self, actual_volume):
        """
        Takes in the product volume dictionary & returns applicable discounts, any residuals (product codes) which doesnt
        have any offers
        :param actual_volume: Dict: Product code vs number of items for each product
        :return: applicable_discounts: List: All applicable discounts for a given register
        :return: residual: Dict: All product codes vs volumes
        """

        applicable_discounts = []
        residual = {}

        min_vol_criteria, product_vs_offer, base_product_vs_offer_product = self.get_product_vs_offer_and_volume(self.discounts)

        for basket_item, volume in actual_volume.items():
            offer_on_product = base_product_vs_offer_product.get(basket_item)
            if min_vol_criteria.get(basket_item):
                if volume >= min_vol_criteria.get(basket_item) and actual_volume.get(offer_on_product):
                    applicable_discounts.append(product_vs_offer.get(basket_item))
                else:
                    residual[basket_item.upper()] = volume
            else:
                for prod, offering in base_product_vs_offer_product.items():
                    if (offering == basket_item) and (prod not in actual_volume):
                        residual[basket_item.upper()] = volume
            # else:


        if "APPL" in applicable_discounts and "APOM" in applicable_discounts:
            applicable_discounts.remove("APOM")
            residual['OM1'] = actual_volume.get('om1')

        return applicable_discounts, residual

    def get_basket_items_discount(self, offer_info, actual_volume, product_prices):
        """
        Computes all applicable offers if the offer type is Dicsount. Buy 1 get 1 or any other discounts
        :param offer_info: Offer class object. Contanins complete metadata of each offer
        :param actual_volume: Dict: Product code vs Volumes
        :param product_prices: Dict: Product code vs prices
        :return: Basket with all offers applied for entries applicable for this offer
        """
        prod_code = offer_info.base_prod_code
        base_prod_vol = actual_volume.get(prod_code.lower())

        discount_basket = []

        if base_prod_vol >= offer_info.min_vol:
            offer_on_prod = offer_info.offer_on
            if actual_volume.get(offer_on_prod.lower()):
                print(f"Base product volume is greater than minimum required volume & product on offer is also available "
                  f"in cart..")
                if offer_info.is_limited:
                    print(f"Limited offer..")
                    if prod_code == offer_on_prod:
                        # total_allowed_items_on_offer = Limit Volume of base product * (Offer Product Max Volume/Minimum volume of base product)
                        total_allowed_items_on_offer = offer_info.limit_vol * (offer_info.offer_prod_volume/offer_info.min_vol)
                        max_limit = 1
                        for i in range(0, base_prod_vol):
                            base_prod_actual_price = product_prices.get(prod_code.lower()).get('price')
                            discount_basket.append((prod_code, base_prod_actual_price))
                            while max_limit <= total_allowed_items_on_offer:
                                discounted_price = (base_prod_actual_price *(offer_info.discount_perc/100))*-1
                                discount_basket.append((offer_info.offer_code, discounted_price))
                                max_limit += 1
                    else:
                        total_allowed_items_on_offer = offer_info.limit_vol * (offer_info.offer_prod_volume / offer_info.min_vol)
                        for i in range(0, base_prod_vol):
                            base_prod_actual_price = product_prices.get(prod_code.lower()).get('price')
                            discount_basket.append((prod_code, base_prod_actual_price))
                        max_limit = 1
                        while max_limit <= total_allowed_items_on_offer:
                            offer_onprod_actual_price = product_prices.get(offer_on_prod.lower()).get('price')
                            discounted_price = (offer_onprod_actual_price *(offer_info.discount_perc/100))*-1
                            for j in range(0, actual_volume.get(offer_on_prod.lower())):
                                discount_basket.append((offer_on_prod, offer_onprod_actual_price))
                                discount_basket.append((offer_info.offer_code, discounted_price))
                                max_limit += 1
                else:
                    print(f"Unlimited offer..")
                    if prod_code == offer_on_prod:
                        if base_prod_vol > offer_info.min_vol:
                            for i in range(0, base_prod_vol):
                                base_prod_actual_price = product_prices.get(prod_code.lower()).get('price')
                                discount_basket.append((prod_code, base_prod_actual_price))
                                if i%2 != 0:
                                    discounted_price = (base_prod_actual_price *(offer_info.discount_perc/100))*-1
                                    discount_basket.append((offer_info.offer_code, discounted_price))
                        else:
                            for i in range(0, base_prod_vol):
                                base_prod_actual_price = product_prices.get(prod_code.lower()).get('price')
                                discount_basket.append((prod_code, base_prod_actual_price))
                    else:
                        for i in range(0, base_prod_vol):
                            base_prod_actual_price = product_prices.get(prod_code.lower()).get('price')
                            discount_basket.append((prod_code, base_prod_actual_price))

                        offer_onprod_actual_price = product_prices.get(offer_on_prod.lower()).get('price')
                        discounted_price = (offer_onprod_actual_price * (offer_info.discount_perc / 100))*-1

                        for j in range(0, actual_volume.get(offer_on_prod.lower())):
                            discount_basket.append((offer_on_prod, offer_onprod_actual_price))
                            discount_basket.append((offer_info.offer_code, discounted_price))


        return discount_basket


    def get_basket_items_pricedrop(self, offer_info, actual_volume, product_prices):
        """
        Computes all applicable offers if the offer type is PriceDrop.
        :param offer_info: Offer class object. Contanins complete metadata of each offer
        :param actual_volume: Dict: Product code vs Volumes
        :param product_prices: Dict: Product code vs prices
        :return: Basket with all offers applied for entries applicable for this offer
        """
        prod_code = offer_info.base_prod_code
        base_prod_vol = actual_volume.get(prod_code.lower())

        pricedrop_basket = []

        if base_prod_vol >= offer_info.min_vol:
            offer_on_prod = offer_info.offer_on
            if actual_volume.get(offer_on_prod.lower()):
                print(
                    f"Base product volume is greater than minimum required volume & product on offer is also available "
                    f"in cart..")
                if offer_info.is_limited:
                    print(f"Limited offer..")
                    if prod_code == offer_on_prod:
                        # total_allowed_items_on_offer = Limit Volume of base product * (Offer Product Max Volume/Minimum volume of base product)
                        total_allowed_items_on_offer = offer_info.limit_vol * (
                                    offer_info.offer_prod_volume / offer_info.min_vol)
                        max_limit = 1
                        for i in range(0, base_prod_vol):
                            base_prod_actual_price = product_prices.get(prod_code.lower()).get('price')
                            pricedrop_basket.append((prod_code, base_prod_actual_price))
                            while max_limit <= total_allowed_items_on_offer:
                                new_price = (base_prod_actual_price - (offer_info.new_price)) * -1
                                pricedrop_basket.append((offer_info.offer_code, new_price))
                                max_limit += 1
                    else:
                        total_allowed_items_on_offer = offer_info.limit_vol * (
                                    offer_info.offer_prod_volume / offer_info.min_vol)
                        for i in range(0, base_prod_vol):
                            base_prod_actual_price = product_prices.get(prod_code.lower()).get('price')
                            pricedrop_basket.append((prod_code, base_prod_actual_price))
                        max_limit = 1
                        while max_limit <= total_allowed_items_on_offer:
                            offer_onprod_actual_price = product_prices.get(offer_on_prod.lower()).get('price')
                            new_price = (base_prod_actual_price - (offer_info.new_price)) * -1
                            for j in range(0, actual_volume.get(offer_on_prod).lower()):
                                pricedrop_basket.append((offer_on_prod, offer_onprod_actual_price))
                                pricedrop_basket.append((offer_info.offer_code, new_price))
                                max_limit += 1
                else:
                    print(f"Unlimited offer..")
                    if prod_code == offer_on_prod:
                        for i in range(0, base_prod_vol):
                            base_prod_actual_price = product_prices.get(prod_code.lower()).get('price')
                            pricedrop_basket.append((prod_code, base_prod_actual_price))
                            new_price = (base_prod_actual_price - (offer_info.new_price))*-1
                            pricedrop_basket.append((offer_info.offer_code, new_price))
                    else:
                        for i in range(0, base_prod_vol):
                            base_prod_actual_price = product_prices.get(prod_code.lower()).get('price')
                            pricedrop_basket.append((prod_code, base_prod_actual_price))

                        offer_onprod_actual_price = product_prices.get(offer_on_prod.lower()).get('price')
                        new_price = (offer_onprod_actual_price - (offer_info.new_price)) * -1

                        for j in range(0, actual_volume.get(offer_on_prod).lower()):
                            pricedrop_basket.append((offer_on_prod, offer_onprod_actual_price))
                            pricedrop_basket.append((offer_info.offer_code, new_price))

            return pricedrop_basket

    def get_basket_with_discounts(self, actual_volume, applicable_discounts, residual):
        """
        Methd for invoking discount & price drop offer computation methods
        :param actual_volume: Dict: Product code Vs voume
        :param applicable_discounts: List: List of applicable discounts
        :param residual: Dict: Just the product code vs volume dict, which doesn't have any offers
        :return:
        """

        # product_vs_min_volume, product_offer = self.get_product_vs_offer_and_volume(self.discounts)
        pr = Product('items')
        product_prices = pr.product_meta

        basket = []

        for discount in applicable_discounts:
            offer_info = Offer('discount', discount)

            if offer_info.offer_type.lower() == "discount":
                temp_basket = self.get_basket_items_discount(offer_info, actual_volume, product_prices)
                for item in temp_basket:
                    basket.append(item)
            elif offer_info.offer_type.lower() == "pricedrop":
                temp_basket = self.get_basket_items_pricedrop(offer_info, actual_volume, product_prices)
                for item in temp_basket:
                    basket.append(item)

        if residual:
            for product, volume in residual.items():
                for i in range(0, volume):
                    basket.append((product, product_prices.get(product.lower()).get('price')))

        return basket

class Offer(Discount):
    """
    Just reads the discount csv, grabs all metadata & makes them available in class object
    """
    def __init__(self, discounts_file_name, offer_code):
        self.discounts = self.read_discounts(discounts_file_name)
        self.offer_code = offer_code
        offer_details = self.discounts.loc[self.discounts['OfferCode'] == self.offer_code]
        self.is_limited = offer_details.Limited.iloc[0]
        self.limit_vol = offer_details.LimitVol.iloc[0]
        self.base_prod_code = offer_details.BaseProductCode.iloc[0]
        self.min_vol = offer_details.MinVolumeCriteria.iloc[0]
        self.offer_type = offer_details.OfferType.iloc[0]
        self.offer_on = offer_details.OfferOnProduct.iloc[0]
        self.offer_prod_volume = offer_details.OfferProductVolume.iloc[0]
        self.discount_perc = offer_details.DiscountPercentage.iloc[0]
        self.new_price = offer_details.NewPrice.iloc[0]

    def read_discounts(self, file_name):
        discounts = pd.read_csv(f'{file_name}.csv')

        return discounts



# unit_basket = [[('ch1', 3.11), ('ap1', 6.0), ('cf1', 11.23), ('cf1', 11.23), ('mk1', 4.75), ('om1', 3.69), ('ap1', 6.0), ('ap1', 6.0)]]
# basket_volume = {'ch1': 1, 'ap1': 3, 'cf1': 2, 'mk1': 1, 'om1': 1}
#
# #Test1
# # unit_basket = [[('ch1', 3.11), ('ap1', 6.0), ('cf1', 11.23), ('mk1', 4.75)]]
# # basket_volume = {'ch1': 1, 'ap1': 1, 'cf1': 1, 'mk1': 1}
#
# # unit_basket = [[('ap1', 6.0),('mk1', 4.75)]]
# # basket_volume = {'ap1': 1, 'mk1': 1}
#
# # unit_basket = [[('cf1', 11.23),('cf1', 11.23)]]
# # basket_volume = {'cf1': 2}
#
# # unit_basket = [[('ch1', 3.11), ('ap1', 6.0), ('ap1', 6.0), ('ap1', 6.0)]]
# # basket_volume = {'ch1': 1, 'ap1': 3}
#
# discount = Discount('discount')
#
# # product_vs_min_volume, product_offer = discount.get_product_vs_offer_and_volume(discount.discounts)
# applicable_offers, residual = discount.get_applicable_discounts(basket_volume)
# print(f"Applicable Offers - {applicable_offers}")
#
# final_basket = discount.get_basket_with_discounts(basket_volume, applicable_offers, residual)
# print(f"FINAL BASKET: {final_basket}")
#
# for item in final_basket:
#     print(str(item[0]).ljust(20), str(item[1]).rjust(20))