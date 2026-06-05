select
    payment_id,
    order_id,
    payment_ts,
    payment_method,
    payment_status,
    amount,
    currency
from workspace.default.silver_payments