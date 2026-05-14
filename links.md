# Public links & contacts

Generated from [`data/links.yaml`](https://github.com/nyuad-ctp/ctp-common/blob/main/data/links.yaml).

## Web

| Resource | URL |
|----------|-----|
| CTP website | <{{ public.ctp_website }}> |
| Linktree (forms, news, quick links) | <{{ public.linktree }}> |
| Booking system (CTPSS) — requires NYU network/VPN | <{{ public.booking_system }}> |
| CTP Requisition Form (Google Form, NYU login) | <{{ public.requisition_form }}> |
| Competitive Bid Exception form | <{{ public.competitive_bid_exception }}> |

## Email

| Mailbox | When to use |
|---------|-------------|
| [{{ contact.generic_email }}](mailto:{{ contact.generic_email }}) | Public-facing CTP admin mailbox |
| [{{ contact.user_group_email }}](mailto:{{ contact.user_group_email }}) | Training & equipment-access requests (users) |
| [{{ contact.all_members_email }}](mailto:{{ contact.all_members_email }}) | Distribution list — reaches every CTP staff member |

## Mailing address

{{ address.line1 }}{% if address.line2 %}  
{{ address.line2 }}{% endif %}  
{{ address.city }}, {{ address.country }}
