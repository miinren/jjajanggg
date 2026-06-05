select
    c.country,
    c.customer_segment,
    count(o.order_id) as order_count,
    round(sum(o.total_amount), 2) as revenue
from {{ ref('stg_orders') }} o
left join {{ ref('stg_customers') }} c
    on o.customer_id = c.customer_id
group by
    c.country,
    c.customer_segment
    