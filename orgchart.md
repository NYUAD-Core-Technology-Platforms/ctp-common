# Organizational chart

How Core Technology Platforms is organized: the Director and CTP Administration, the platform clusters with their leads, and the direct reports. Rendered from [`data/clusters.yaml`](https://github.com/NYUAD-Core-Technology-Platforms/ctp-common/blob/main/data/clusters.yaml) and [`data/people.yaml`](https://github.com/NYUAD-Core-Technology-Platforms/ctp-common/blob/main/data/people.yaml), the single source of truth. See also the [team directory](team.md) for contacts and the [platforms index](platforms/index.md) for what each lab does.

<style>
.org-top { display: flex; gap: 1rem; align-items: flex-start; flex-wrap: wrap; margin: 1rem 0 1.4rem; }
.org-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(13.5rem, 1fr)); gap: 0.9rem; align-items: start; }
.org-col { display: grid; gap: 0.5rem; }
.org-lead { background: #57068C; color: #fff; border-radius: 8px; padding: 0.7rem 0.9rem; min-width: 12rem; }
.org-cl { margin: 0 !important; font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.85; color: inherit; }
.org-ln { margin: 0.2rem 0 0 !important; font-size: 1.02rem; font-weight: 700; color: inherit; }
.org-dir { border-left: 4px solid #d4a017; }
.org-vacant { background: rgba(87, 6, 140, 0.12); color: #57068C; border: 1px dashed #57068C; }
[data-md-color-scheme="slate"] .org-vacant { background: rgba(180, 120, 230, 0.15); color: #cfa5f0; border-color: #cfa5f0; }
.org-vacant .org-ln { font-style: italic; }
.org-card { border: 1px solid rgba(128, 128, 128, 0.45); border-radius: 8px; padding: 0.5rem 0.9rem; font-size: 0.85rem; font-weight: 600; }
.org-role { display: block; font-size: 0.72rem; font-weight: 400; opacity: 0.75; margin-top: 0.1rem; }
.org-side { display: grid; gap: 0.4rem; }
.org-lbl { margin: 0 !important; font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.7; }
</style>

{% set byid = {} %}
{% for p in people %}{% set _ = byid.update({p.netid: p}) %}{% endfor %}

<div class="org-top" markdown="0">
  <div class="org-lead org-dir">
    <p class="org-cl">Director, Core Technology Platforms</p>
    <p class="org-ln">{{ byid[default_validator].name }}</p>
  </div>
  <div class="org-side">
    <p class="org-lbl">CTP Administration</p>
    {% for id in administration %}<div class="org-card">{{ byid[id].name }}<span class="org-role">{{ byid[id].role }}</span></div>{% endfor %}
  </div>
  <div class="org-side">
    <p class="org-lbl">Direct reports (no team)</p>
    {% for id in no_team %}<div class="org-card">{{ byid[id].name }}<span class="org-role">{{ byid[id].role }}</span></div>{% endfor %}
  </div>
</div>

<div class="org-grid" markdown="0">
{% for c in clusters %}
  <div class="org-col">
    <div class="org-lead{% if not c.lead %} org-vacant{% endif %}">
      <p class="org-cl">{{ c.name }}</p>
      <p class="org-ln">{% if c.lead %}{{ byid[c.lead].name }}{% else %}Lead to be named{% endif %}</p>
    </div>
    {% for id in c.members %}{% if id != c.lead %}<div class="org-card">{{ byid[id].name }}<span class="org-role">{{ byid[id].role }}</span></div>{% endif %}{% endfor %}
  </div>
{% endfor %}
</div>

*Clusters without a named lead and the direct reports are overseen by the Director. To correct anything on this chart, edit `data/clusters.yaml` (composition) or `data/people.yaml` (names and titles).*
