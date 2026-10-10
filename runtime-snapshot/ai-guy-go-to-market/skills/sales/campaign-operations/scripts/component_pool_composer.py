"""Component-pool composer for per-lead cold-email sequences with hard word bands.

Pattern validated on a 30,331-lead × 22-touch build (2026-09-03): deterministic combo
search over (opener × pain × offer × close) variants picks the first combination inside
the band (85-100 target), falling back to the shortest combo. Post-hoc string trimming
of a pool-composed email does NOT converge (six QA cycles); combo search landed
1,999/2,000 framework emails in band on the first pass.

Adapt: SEG vocabulary, component pools, PAINS dict, SUBJECTS, FU texts, CLOSER texts,
and the client-rule constants (banned words, subjects rules, word bands) to the active
framework doc. Keep a 3rd compact offer/close variant in every pool so long
company+city interpolations still fit the band.
"""
import hashlib


def pick(email, salt, n):
    """Deterministic per-(lead, slot) index. Same email + salt => same pick every run."""
    return int(hashlib.sha256(f'{email}|{salt}'.encode()).hexdigest()[:12], 16) % n


def combo_body(email, key, op_pool, pains, offer_v, close_v, lo=85, hi=100):
    """Deterministic first-fit combo search inside [lo, hi]; falls back to shortest."""
    best = None
    cands = []
    for oi in range(len(op_pool)):
        for pi in range(len(pains)):
            for fi in range(99):
                try:
                    off = offer_v(fi)
                except IndexError:
                    break
                for ci in range(99):
                    try:
                        cl = close_v(ci)
                    except IndexError:
                        break
                    w = sum(len(x.split()) for x in (op_pool[oi], pains[pi], off, cl))
                    cands.append((w, oi, pi, fi, ci))
                    if lo <= w <= hi and best is None:
                        best = (oi, pi, fi, ci)
            if best:
                break
        if best:
            break
    if not best:
        # shortest available combo (keeps even pathological company+city names in tolerance)
        all_c = []
        for oi in range(len(op_pool)):
            for pi in range(len(pains)):
                for fi in range(99):
                    try:
                        off = offer_v(fi)
                    except IndexError:
                        break
                    for ci in range(99):
                        try:
                            cl = close_v(ci)
                        except IndexError:
                            break
                        w = sum(len(x.split()) for x in (op_pool[oi], pains[pi], off, cl))
                        all_c.append((w, oi, pi, fi, ci))
        best = min(all_c)
    _, oi, pi, fi, ci = best
    return '\n\n'.join([op_pool[oi], pains[pi], offer_v(fi), close_v(ci)])


def scrub_company(name):
    """Lead company names carry punctuation that violates client rules when interpolated."""
    import re
    if '&' in name:
        name = name.split('&')[0].strip()
    elif ',' in name:
        name = name.split(',')[0].strip()
    elif ' of ' in name.lower():
        name = name[: name.lower().find(' of ')].strip()
    if len(name.split()) > 5:
        name = ' '.join(name.split()[:4])
    name = name.replace('!', '').replace('$', 'S')
    if '\u2013' in name or '\u2014' in name or '-' in name:
        name = re.split(r'[\u2013\u2014\-]', name)[0].strip()
    name = re.sub(r'\b(dba|llc|inc|the)\b\.?$', '', name, flags=re.I).strip()
    return name or 'your place'


# QA exception for banned tokens that legitimately live in the lead's identity:
#   token must not match company (possessives stripped) or City/State before flagging.
#   comp = company.lower().replace("'", "").replace('\u2019', '')
#   hay = comp + ' ' + city.lower() + ' ' + state.lower()
