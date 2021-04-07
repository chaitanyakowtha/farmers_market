from basket_bill import Product
from calculate_discounts import Discount
import sys

def main():
    """
    Main function
    :return: invokes other functions
    """
    # Use a breakpoint in the code line below to debug your script.
    print(f"Enter CHECKIN to start a new bill...")
    print(f"Enter FINALIZE to complete a bill")
    initial_input = input()

    pr = Product('items')

    if initial_input.lower() == "checkin":
        checkin(pr.product_meta)
    elif initial_input.lower() == "finalize":
        finalize()
    else:
        print(f"Input is invalid, please check, provided input-{initial_input}")

def print_basket_value(basket):
    """
    Utilized to print register with product codes & price in right, left justified manner
    :param basket: List of tuples. First element of tuple is product code & second element is price
    :return: Just prints the register along with total amount
    """

    basket_value = 0
    for item in basket:
        print(str(item[0]).ljust(20), str(item[1]).rjust(20))
        basket_value += item[1]
    print('--------------------------------------------------------')

    print(str(basket_value).rjust(50))

def checkin(product_meta):
    """
    Function utilized for keying in various products for billing. Finalization of bill also will be invoked frm here
    :param product_meta: Dict of {product_code: {'name': product_name, 'price': price}}
    :return: Checks-In the bill, on request does an interim print to see register, takes command for finalizing bill
    """

    basket = []
    item_volume = {}
    basket_value = 0
    print(f"Enter a product code to add any item..")

    while basket is not None:
        item = input()
        if item.lower() == 'finalize':
            finalize(item_volume)
            print_basket_value(basket)
            break
        elif item.lower() == 'print_register':
            print_basket_value(basket)
        else:
            if item not in product_meta:
                print(f"{item} is not a valid product code, please enter any code from {','.join(product_meta.keys())}")
            else:
                price = product_meta.get(item).get('price')
                basket.append((item, price))
                # basket_value += price

                if not item_volume.get(item):
                    item_volume[item] = 1
                else:
                    item_volume[item] = item_volume.get(item) + 1


def finalize(item_volume):
    """
    Utilizes Discount class to compute discounts given product volumes

    :param item_volume: Dict: {'product_code': number of occurences in basket}
    :return: Prints the register along with total amount
    """
    ds = Discount('discount')

    applicable_offers, residual = ds.get_applicable_discounts(item_volume)
    final_basket = ds.get_basket_with_discounts(item_volume, applicable_offers, residual)
    print_basket_value(final_basket)

    sys.exit(0)

if __name__ == '__main__':
    main()


