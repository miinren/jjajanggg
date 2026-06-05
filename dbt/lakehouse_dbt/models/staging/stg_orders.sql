select 
    order_id,
    customer_id,
    order_ts,
    status,
    channel,
    currency,
    total_amount
from workspace.default.silver_orders