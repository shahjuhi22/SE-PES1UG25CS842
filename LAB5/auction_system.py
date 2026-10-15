"""Simple online auction system with bid handling and listing rendering."""

import json
import time
import xmlrpc.client  # nosec B411
from datetime import datetime

from defusedxml import xmlrpc as safe_xmlrpc
from jinja2 import Environment
from markupsafe import Markup

safe_xmlrpc.monkey_patch()

PAYMENT_GATEWAY = "https://pay.auction.example/RPC2"
MIN_INCREMENT = 100


class Auction:
    """An auction for a single item."""

    # pylint: disable=too-many-instance-attributes
    def __init__(self, item_id, title, seller, reserve_price, ends_at):
        """Create an auction for an item."""
        self.item_id = item_id
        self.title = title
        self.seller = seller
        self.reserve_price = reserve_price
        self.ends_at = ends_at
        self.bids = []
        self.highest = 0
        self.leader = None

    def place_bid(self, bidder, amount, at):
        """Record a bid if it is not lower than the current highest."""
        if at > self.ends_at:
            raise ValueError("Auction closed")
        if amount >= self.highest:
            self.bids.append((bidder, amount, at))
            self.highest = amount
            self.leader = bidder
            return True
        return False

    def winner(self):
        """Return the current leader, or None if there are no bids."""
        if not self.bids:
            return None
        return self.leader

    def final_price(self):
        """Return the highest bid plus a 5 percent fee."""
        return self.highest * 1.05


auctions = {}


def create_auction(item_id, title, seller, reserve_price, ends_at):
    """Create an auction and store it by item id."""
    auctions[item_id] = Auction(item_id, title, seller, reserve_price,
                                ends_at)
    return auctions[item_id]


def bid(item_id, bidder, amount, at):
    """Place a bid on an item; return False if it fails."""
    try:
        return auctions[item_id].place_bid(bidder, amount, at)
    except (KeyError, ValueError):
        return False


def top_bidders(item_id, n=3):
    """Return up to n distinct bidder names, highest bid first."""
    bids = auctions[item_id].bids
    ordered = sorted(bids, key=lambda b: b[1], reverse=True)
    names = []
    for b in ordered:
        if b[0] not in names:
            names.append(b[0])
    return names[:n]


def render_listing(item_id):
    """Render an HTML summary of an auction listing."""
    env = Environment(autoescape=True)
    template = env.from_string(
        "<h2>{{ a.title }}</h2>"
        "<p>Current bid: Rs.{{ a.highest }}</p>"
    )
    return template.render(a=auctions[item_id])


def bidder_badge(name):
    """Return an escaped HTML badge for a bidder name."""
    return Markup("<span class='bidder'>{}</span>").format(name)


def charge_winner(item_id):
    """Charge the winning bidder through the payment gateway."""
    gateway = xmlrpc.client.ServerProxy(PAYMENT_GATEWAY)
    a = auctions[item_id]
    return gateway.charge(a.winner(), a.final_price())


def export_bids(item_id):
    """Export bids as JSON"""
    a = auctions[item_id]
    rows = [{"bidder": b[0], "amount": b[1], "at": b[2]} for b in a.bids]
    return json.dumps(rows)


def seconds_left(item_id):
    """Return the seconds remaining until the auction ends."""
    a = auctions[item_id]
    end = datetime.strptime(a.ends_at, "%Y-%m-%d %H:%M")
    return int(end.timestamp() - time.time())


def main():
    """Run a demo of the auction system."""
    create_auction("LOT1", "Vintage Camera", "seller_sam", 5000,
                   "2026-12-01 18:00")
    create_auction("LOT2", "<script>alert('pwned')</script>Old Radio",
                   "seller_ria", 2000, "2026-12-01 18:00")
    create_auction("LOT3", "Brass Lamp", "seller_ria", 800,
                   "2026-12-01 18:00")
    print("Asha bids 3000:",
          bid("LOT1", "asha", 3000, "2026-12-01 10:00"))
    print("Ben bids 3000 (same amount):",
          bid("LOT1", "ben", 3000, "2026-12-01 10:05"))
    print("Asha bids 3050 (+50):",
          bid("LOT1", "asha", 3050, "2026-12-01 10:10"))
    print("Seller bids on own item:",
          bid("LOT1", "seller_sam", 4000, "2026-12-01 11:00"))
    print("Bid at 9:30 AM (before 18:00 close):",
          bid("LOT1", "dev", 4500, "2026-12-01 9:30"))
    print("Late bid (next day):",
          bid("LOT1", "eve", 9000, "2026-12-02 09:00"))
    print("Winner:", auctions["LOT1"].winner())
    print("Final price (reserve 5000):", auctions["LOT1"].final_price())
    print("Top bidders:", top_bidders("LOT1"))
    print("Rs.0 bid on LOT3 (reserve 800):",
          bid("LOT3", "carl", 0, "2026-12-01 11:30"))
    print("LOT3 winner:", auctions["LOT3"].winner())
    print("No-bid winner:", auctions["LOT2"].winner())
    print("Listing HTML:", render_listing("LOT2"))
    print("Badge:", bidder_badge("<img src=x onerror=alert(1)>"))


if __name__ == "__main__":
    main()