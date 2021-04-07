import pandas as pd

class Product:
    """
    Product class helps grab the metadata from products CSV
    """

    def __init__(self, df_name):
        self.df = pd.read_csv(f'{df_name}.csv')
        self.valid_product_codes = self.df['ProductCode']
        self.product_meta = self.get_meta_dict(self.df)

    def get_meta_dict(self, df):
        """
        Takes in products metadata & returns {'product_code': {'name': product_name, 'price': product_price}}
        :param df: pandas dataframe
        :return: Dict
        """

        meta = {}

        for i in df.itertuples():
            meta[i[1].lower()] = {'name': i[2], 'price': i[3]}

        return meta