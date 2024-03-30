from enum import Enum


class SaleType(Enum):
    Regular = 1
    Auction = 2
    Auction_or_highest_bidder = 3
    
