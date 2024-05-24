from typing import List


class AttachToEventParams:
    """
    Parameters for attaching products to an event.
        - product_ids: List of product ids where the method need to update discounts
        - discounts: List of product discounts which the method need to apply to the products.
        - event id: What identifier of the event need to be added to the products.
    """
    def __init__(self, product_ids: List[str], discounts: List[float], event_id: str):
        self.product_ids = product_ids
        self.discounts = discounts
        self.event_id = event_id
