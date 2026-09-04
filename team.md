# Team

Everyone in this page is generated from [`data/people.yaml`](https://github.com/nyuad-ctp/ctp-common/blob/main/data/people.yaml) — that file is the single source of truth. Edit it to update the directory.

{% set leadership = people | selectattr('category', 'equalto', 'leadership') | list %}
{% set scientists = people | selectattr('category', 'equalto', 'scientist') | list %}
{% set specialists = people | selectattr('category', 'equalto', 'specialist') | list %}
{% set machine_shop = people | selectattr('category', 'equalto', 'machine_shop') | list %}
{% set adjacent = people | selectattr('category', 'equalto', 'adjacent') | list %}

## Leadership

| Role | Name | Email | Ext. | Mobile | Office |
|------|------|-------|------|--------|--------|
{% for p in leadership -%}
| {{ p.role }} | **{{ p.name }}** | [{{ p.email }}](mailto:{{ p.email }}) | {{ p.ext or '—' }} | {{ p.mobile or '—' }} | {{ p.office or '—' }} |
{% endfor %}

## Team / Cluster Leads

The coordination leads across CTP, as recorded in [`data/people.yaml`](https://github.com/NYUAD-Core-Technology-Platforms/ctp-common/blob/main/data/people.yaml) (`team_lead: true`).

| Name | Role | Email | Ext. | Mobile |
|------|------|-------|------|--------|
{% set leads = people | selectattr('team_lead', 'defined') | selectattr('team_lead') | list %}
{% for p in leads -%}
| **{{ p.name }}** | {{ p.role }} | [{{ p.email }}](mailto:{{ p.email }}) | {{ p.ext or '-' }} | {{ p.mobile or '-' }} |
{% endfor %}

## Research Instrumentation Scientists

| Name | Platform | Email | Ext. | Mobile | Office |
|------|----------|-------|------|--------|--------|
{% for p in scientists -%}
| **{{ p.name }}** | {% if p.platform %}[{{ p.platform }}](platforms/{{ p.platform }}.md){% else %}cross-CTP{% endif %} | [{{ p.email }}](mailto:{{ p.email }}) | {{ p.ext or '—' }} | {{ p.mobile or '—' }} | {{ p.office or '—' }} |
{% endfor %}

## Research Instrumentation Specialists

| Name | Platform | Email | Ext. | Mobile | Office |
|------|----------|-------|------|--------|--------|
{% for p in specialists -%}
| **{{ p.name }}** | {% if p.platform %}[{{ p.platform }}](platforms/{{ p.platform }}.md){% else %}cross-CTP{% endif %} | [{{ p.email }}](mailto:{{ p.email }}) | {{ p.ext or '—' }} | {{ p.mobile or '—' }} | {{ p.office or '—' }} |
{% endfor %}

## Machine Shop & technical support

| Name | Role | Email | Ext. | Mobile | Office |
|------|------|-------|------|--------|--------|
{% for p in machine_shop -%}
| **{{ p.name }}** | {{ p.role }} | [{{ p.email }}](mailto:{{ p.email }}) | {{ p.ext or '—' }} | {{ p.mobile or '—' }} | {{ p.office or '—' }} |
{% endfor %}

## Adjacent teams

Research Materials Acquisition, accounts, logistics, and other day-to-day partners.

| Name | Role | Email | Ext. | Mobile | Office |
|------|------|-------|------|--------|--------|
{% for p in adjacent -%}
| **{{ p.name }}** | {{ p.role }} | [{{ p.email }}](mailto:{{ p.email }}) | {{ p.ext or '—' }} | {{ p.mobile or '—' }} | {{ p.office or '—' }} |
{% endfor %}

## Institutional services

Generic mailboxes — no individual owner.

| Service | Email | Phone |
|---------|-------|-------|
{% for s in services -%}
| **{{ s.name }}** | {% if s.email %}[{{ s.email }}](mailto:{{ s.email }}){% else %}—{% endif %} | {{ s.phone }} |
{% endfor %}

---

## By platform

Click a platform to see its full description and equipment list.

{% set platforms_with_team = people | selectattr('platform') | groupby('platform') %}
{% for platform_id, members in platforms_with_team -%}
### [{{ platform_id }}](platforms/{{ platform_id }}.md)

{% for p in members -%}
- **{{ p.name }}** — {{ p.role }} · [{{ p.email }}](mailto:{{ p.email }})
{% endfor %}

{% endfor %}

---

!!! info "Phone format"
    5-digit numbers are NYUAD internal extensions. Dial **+971 2 628 &lt;ext&gt;** from outside the campus network. Mobile numbers are UAE local format.
