select
    cast(payment_ts as date) as payment_date,
    count(*) as total_payments,
    sum(case when payment_status = 'success' then 1 else 0 end) as successful_payments,
    sum(case when payment_status = 'failed' then 1 else 0 end) as failed_payments,
    round(avg(case when payment_status = 'success' then 1.0 else 0.0 end), 4) as payment_success_rate
from {{ ref('stg_payments') }}
group by
    cast(payment_ts as date)