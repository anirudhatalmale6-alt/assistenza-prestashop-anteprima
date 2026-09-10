#!/usr/bin/env python3
"""
Genera le 4 pagine dell'anteprima.

Perche' un generatore e non 4 file a mano: header, menu e footer devono essere
IDENTICI su tutte le pagine. Scritti a mano divergono alla prima modifica.
Modificare SEMPRE questo file, mai i .html in preview/.

    python3 build.py
"""
import pathlib, html, re

import sys
# due destinazioni: l'anteprima pubblica e i file dentro il plugin WordPress.
MODE = sys.argv[1] if len(sys.argv) > 1 else "preview"
OUT = (pathlib.Path(__file__).parent /
       ("preview" if MODE == "preview" else "plugin/webhouse-pagine/pagine"))

# ---------------------------------------------------------------- dati reali
# Forniti dal cliente il 10 set 2026. Nulla qui e' inventato.
AZIENDA      = "WebHouse S.a.s."
SEDE_LEGALE  = "via Sant&rsquo;Elena Imperatrice 25 &ndash; 31100 Treviso"
SEDE_OPER    = "via Jacopo Bernardi 13/a &ndash; 31100 Treviso (TV)"
EMAIL        = "info@webhousesas.net"
TEL1         = "+39 392 042 6808"
TEL1_RAW     = "393920426808"          # usato per il link wa.me / tel:
TEL2         = "+39 366 361 9529"
TEL2_RAW     = "393663619529"
CF           = "GNVMRC71A05L407Z"
PIVA         = "05143900263"
WA           = f"https://wa.me/{TEL1_RAW}"

# Unico dato ancora mancante: gli orari di apertura. Non li invento.
ORARI = '<span class="ph">[ORARI &mdash; dimmi tu]</span>'

PAGES = ["index", "assistenza", "gratis", "contattaci"]
SHORT = {"index":"HOME","assistenza":"ASSISTENZA","gratis":"GRATIS","contattaci":"CONTATTACI"}
TITLES = {
    "index":      "Assistenza PrestaShop urgente",
    "assistenza": "Assistenza PrestaShop",
    "gratis":     "Trasferisci e risolvi gratis",
    "contattaci": "Contattaci",
}
NAV = [("index", "Home"), ("assistenza", "Assistenza PrestaShop"),
       ("gratis", "Gratis"), ("contattaci", "Contattaci")]


def NOTE_BAR(page):
    if MODE != "preview":
        return ""
    return ('<div class="note">Anteprima di lavoro &mdash; pagina <b>' + SHORT[page] +
            '</b>. Manca solo il dato <span class="ph">evidenziato in giallo</span>.</div>')


def head(page):
    links = "\n      ".join(
        f'<a href="{p}.html"{" aria-current=\"page\"" if p == page else ""}>{lbl}</a>'
        for p, lbl in NAV)
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{TITLES[page]} &mdash; {AZIENDA}</title>
<meta name="description" content="Assistenza tecnica PrestaShop a Treviso. Trasferisci hosting e dominio da noi e risolviamo il problema gratis.">
{'<meta name="robots" content="noindex,nofollow">' if MODE == "preview" else ''}
<link rel="stylesheet" href="assets/style.css">
</head>
<body>

{NOTE_BAR(page)}

<header class="hdr">
  <div class="wrap hdr__in">
    <a class="logo" href="index.html">
      <span class="logo__mark">W</span>
      <span>Web<span class="logo__b">House</span></span>
    </a>
    <nav class="nav" id="nav">
      {links}
    </nav>
    <a class="btn btn--primary btn--sm" href="{WA}" target="_blank" rel="noopener">
      <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.25-1.38a9.9 9.9 0 0 0 4.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2Zm5.8 14.13c-.25.69-1.44 1.32-1.98 1.36-.53.05-1.02.24-3.45-.72-2.9-1.14-4.75-4.1-4.9-4.29-.14-.19-1.17-1.55-1.17-2.96s.74-2.1 1-2.39c.26-.29.57-.36.76-.36l.55.01c.17 0 .41-.07.64.49.25.6.83 2.06.9 2.21.07.14.12.31.02.5-.1.19-.15.31-.29.48-.14.17-.3.38-.43.51-.14.14-.29.3-.13.58.17.29.74 1.22 1.59 1.98 1.09.97 2.01 1.27 2.3 1.42.29.14.45.12.62-.07.17-.19.72-.84.91-1.13.19-.29.38-.24.64-.14.26.09 1.66.78 1.94.93.29.14.48.21.55.33.07.12.07.69-.18 1.38Z"/></svg>
      Scrivici su WhatsApp
    </a>
    <button class="burger" id="burger" aria-label="Menu" aria-expanded="false" aria-controls="nav"><span></span><span></span><span></span></button>
  </div>
</header>
"""


def cta(title, text):
    return f"""
<section class="cta" id="contatto">
  <div class="wrap">
    <h2>{title}</h2>
    <p>{text}</p>
    <a class="btn btn--primary" href="{WA}" target="_blank" rel="noopener">Scrivici su WhatsApp {TEL1}</a>
  </div>
</section>
"""


FOOTER = f"""
<footer class="ftr">
  <div class="wrap">
    <div class="ftr__grid">
      <div>
        <div class="logo"><span class="logo__mark">W</span><span>Web<span style="color:#FF8C00">House</span></span></div>
        <p>Assistenza tecnica PrestaShop e hosting gestito.<br>{AZIENDA}</p>
      </div>
      <div>
        <h4>Pagine</h4>
        {"<br>".join(f'<a href="{p}.html">{l}</a>' for p, l in NAV)}
      </div>
      <div>
        <h4>Sedi</h4>
        <p><b>Sede legale</b><br>{SEDE_LEGALE}</p>
        <p style="margin-top:10px"><b>Sede operativa</b><br>{SEDE_OPER}</p>
      </div>
      <div>
        <h4>Contatti</h4>
        <p>
          <a href="tel:+{TEL1_RAW}">{TEL1}</a><br>
          <a href="tel:+{TEL2_RAW}">{TEL2}</a><br>
          <a href="mailto:{EMAIL}">{EMAIL}</a>
        </p>
        <p style="margin-top:10px">P.IVA {PIVA}<br>C.F. {CF}</p>
      </div>
    </div>
    <div class="ftr__bar">
      <span>&copy; {AZIENDA} &mdash; Tutti i diritti riservati</span>
      <span>Anteprima di lavoro &mdash; non indicizzata</span>
    </div>
  </div>
</footer>

<script>
(function(){{
  var b=document.getElementById('burger'), n=document.getElementById('nav');
  if(!b||!n) return;
  b.addEventListener('click',function(){{
    var open=n.classList.toggle('is-open');
    b.setAttribute('aria-expanded',open?'true':'false');
  }});
  n.addEventListener('click',function(e){{
    if(e.target.tagName==='A'){{n.classList.remove('is-open');b.setAttribute('aria-expanded','false');}}
  }});
}})();
</script>
</body>
</html>
"""

# ------------------------------------------------------------------- icone
def ico(d):
    return f'<div class="card__ico"><svg viewBox="0 0 24 24">{d}</svg></div>'

I_REFRESH = '<path d="M21 12a9 9 0 1 1-3-6.7"/><path d="M21 3v6h-6"/>'
I_LAYERS  = '<path d="M12 2 3 7l9 5 9-5-9-5Z"/><path d="M3 17l9 5 9-5"/><path d="M3 12l9 5 9-5"/>'
I_SERVER  = '<rect x="2" y="3" width="20" height="7" rx="2"/><rect x="2" y="14" width="20" height="7" rx="2"/><path d="M6 6.5h.01M6 17.5h.01"/>'
I_ALERT   = '<path d="M10.3 3.6 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.6a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4"/><path d="M12 17h.01"/>'
I_CHART   = '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/>'
I_LOCK    = '<rect x="3" y="11" width="18" height="10" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>'
I_FILE    = '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6"/><path d="M12 12v6"/><path d="M9 15h6"/>'
I_BOLT    = '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8Z"/>'
I_SHIELD  = '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/>'
I_CART    = '<circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.7 13.4a2 2 0 0 0 2 1.6h9.7a2 2 0 0 0 2-1.6L23 6H6"/>'
I_CHECK   = '<path d="M20 6 9 17l-5-5"/>'

CHECK_SVG = '<svg viewBox="0 0 24 24">' + I_CHECK + '</svg>'


def card(icon, title, text):
    return f'<article class="card">{ico(icon)}<h3>{title}</h3><p>{text}</p></article>'


def step(n, title, text):
    return f'<article class="step"><div class="step__n">{n}</div><h3>{title}</h3><p>{text}</p></article>'


# =========================================================== PAGINA 1: HOME
HERO_SVG = """
      <svg viewBox="0 0 560 360" role="img" aria-label="Negozio online trasferito su un nuovo server">
        <defs>
          <linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stop-color="#003C6C"/><stop offset="1" stop-color="#002A4D"/>
          </linearGradient>
          <filter id="sh" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="10" stdDeviation="14" flood-color="#101013" flood-opacity=".10"/>
          </filter>
        </defs>
        <g filter="url(#sh)">
          <rect x="6" y="34" width="348" height="238" rx="14" fill="#fff" stroke="#DDE3EA"/>
          <path d="M6 48a14 14 0 0 1 14-14h320a14 14 0 0 1 14 14v14H6V48Z" fill="#101013"/>
        </g>
        <circle cx="30" cy="48" r="5" fill="#FF5F57"/><circle cx="48" cy="48" r="5" fill="#FEBC2E"/><circle cx="66" cy="48" r="5" fill="#28C840"/>
        <rect x="92" y="41" width="176" height="14" rx="7" fill="#2C2C33"/>
        <rect x="28" y="84" width="118" height="12" rx="6" fill="#101013"/>
        <rect x="28" y="106" width="192" height="9" rx="4.5" fill="#C3CCD6"/>
        <rect x="28" y="130" width="92" height="32" rx="5" fill="url(#g1)"/>
        <rect x="28" y="182" width="94" height="68" rx="9" fill="#F5F7F9" stroke="#DDE3EA"/>
        <rect x="133" y="182" width="94" height="68" rx="9" fill="#F5F7F9" stroke="#DDE3EA"/>
        <rect x="238" y="182" width="94" height="68" rx="9" fill="#F5F7F9" stroke="#DDE3EA"/>
        <rect x="42" y="197" width="38" height="8" rx="4" fill="#C3CCD6"/>
        <rect x="147" y="197" width="38" height="8" rx="4" fill="#C3CCD6"/>
        <rect x="252" y="197" width="38" height="8" rx="4" fill="#C3CCD6"/>
        <rect x="42" y="222" width="56" height="10" rx="5" fill="#003C6C"/>
        <rect x="147" y="222" width="56" height="10" rx="5" fill="#003C6C"/>
        <rect x="252" y="222" width="56" height="10" rx="5" fill="#003C6C"/>
        <path d="M366 152 h44" stroke="#FF8C00" stroke-width="3" fill="none" stroke-dasharray="8 7" stroke-linecap="round"/>
        <path d="M404 143 l12 9 -12 9" stroke="#FF8C00" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        <g filter="url(#sh)"><rect x="424" y="60" width="130" height="186" rx="14" fill="url(#g1)"/></g>
        <rect x="443" y="86" width="92" height="28" rx="7" fill="rgba(255,255,255,.22)"/>
        <rect x="443" y="125" width="92" height="28" rx="7" fill="rgba(255,255,255,.22)"/>
        <rect x="443" y="164" width="92" height="28" rx="7" fill="rgba(255,255,255,.22)"/>
        <circle cx="458" cy="100" r="4.5" fill="#FF8C00"/>
        <circle cx="458" cy="139" r="4.5" fill="#FF8C00"/>
        <circle cx="458" cy="178" r="4.5" fill="#FF8C00"/>
        <rect x="443" y="209" width="60" height="8" rx="4" fill="rgba(255,255,255,.45)"/>
        <g filter="url(#sh)" transform="translate(392,268)"><rect x="0" y="0" width="146" height="54" rx="27" fill="#FF8C00"/></g>
        <text x="465" y="302" text-anchor="middle" fill="#fff" font-family="Inter,sans-serif" font-size="20" font-weight="700" letter-spacing="1">GRATIS</text>
      </svg>
"""

def page_index():
    cards = "\n      ".join([
        card(I_REFRESH, "Aggiornamenti", "Portiamo PrestaShop, tema e moduli a una versione aggiornata, con backup prima di ogni passaggio."),
        card(I_LAYERS,  "Moduli su misura", "Quando il modulo che ti serve non esiste, lo sviluppiamo noi sulle esigenze del tuo negozio."),
        card(I_SERVER,  "Migrazione e hosting", "Spostiamo il negozio su server o dominio nuovo senza interruzioni e senza perdere ordini."),
        card(I_ALERT,   "Errori e pagine bianche", "Individuiamo l&rsquo;origine degli errori critici che bloccano il negozio e li correggiamo alla radice."),
        card(I_CHART,   "SEO e struttura", "Sistemiamo la struttura tecnica perch&eacute; Google legga bene il negozio: URL, tempi di risposta, dati strutturati."),
        card(I_LOCK,    "Accesso al backoffice", "Recuperiamo l&rsquo;accesso al pannello e risolviamo le anomalie su ordini, prodotti e permessi."),
        card(I_FILE,    "Nuove pagine", "Creiamo pagine e sezioni nuove: landing, categorie, banner promozionali, pagine istituzionali."),
        card(I_BOLT,    "Negozio lento", "Misuriamo dove si perde tempo nel caricamento e interveniamo su cache, query, immagini e server."),
    ])
    steps = "\n      ".join([
        step(1, "Raccontaci il problema", f"Scrivici su WhatsApp con due righe o un messaggio vocale. Ti risponde una persona che conosce PrestaShop, non un centralino." + (f" Siamo operativi {ORARI}." if MODE == "preview" else "")),
        step(2, "Guardiamo cosa succede davvero", "Analizziamo il malfunzionamento senza chiederti nulla in cambio. Ti spieghiamo in parole semplici da cosa dipende e cosa serve per sistemarlo."),
        step(3, "Trasferisci e risolviamo", "Sposti hosting e dominio da noi, ci occupiamo noi della migrazione e del problema. Il negozio resta online per tutta l&rsquo;operazione."),
    ])
    offer_items = "\n        ".join(f"<li>{CHECK_SVG} {t}</li>" for t in [
        "Migrazione di file, database e caselle email",
        "Trasferimento del dominio seguito da noi",
        "Certificato SSL installato e configurato",
        "Risoluzione del problema che ti blocca",
        "Nessuna interruzione durante il passaggio",
    ])
    faqs = "\n      ".join(faq(q, a, i == 0) for i, (q, a) in enumerate([
        ("Devo pagare qualcosa per l&rsquo;analisi?", "No. Guardiamo il problema e ti diciamo cosa serve senza chiederti nulla."),
        ("Il negozio resta online durante il trasferimento?", "S&igrave;. Prepariamo tutto sul nuovo server e spostiamo il dominio solo quando la copia funziona correttamente."),
        ("Su quali versioni di PrestaShop lavorate?", "Su tutte, comprese le installazioni vecchie rimaste indietro di diverse versioni."),
        ("E se il problema &egrave; troppo grosso?", "Te lo diciamo prima, con onest&agrave;. Se non rientra nel servizio gratuito ti facciamo una proposta chiara e decidi tu."),
    ]))
    return f"""
<section class="hero">
  <div class="wrap hero__grid">
    <div>
      <p class="eyebrow">Assistenza PrestaShop &mdash; trasferisci e risolvi</p>
      <h1>Negozio PrestaShop bloccato? Lo rimettiamo in piedi noi, gratis.</h1>
      <p class="hero__sub">
        Sposta hosting e dominio su di noi e ci occupiamo noi del problema che ti blocca il
        negozio, <strong>senza costi aggiuntivi</strong>. Un tecnico dedicato, un interlocutore
        solo, nessun preventivo a sorpresa.
      </p>
      <div class="hero__cta">
        <a class="btn btn--primary" href="{WA}" target="_blank" rel="noopener">Scrivici su WhatsApp</a>
        <a class="btn btn--ghost" href="#come-funziona">Come funziona</a>
      </div>
      <p class="hero__by">Un servizio di {AZIENDA} &mdash; Treviso</p>
    </div>
    <div class="hero__art">
      <!-- illustrazione disegnata da me: nessuna immagine presa dal sito di partenza -->
      {HERO_SVG}
    </div>
  </div>
</section>

<div class="strip">
  <div class="wrap strip__in">
    <span class="strip__lbl">Lavoriamo su tutte le versioni:</span>
    <span class="chip">PrestaShop 1.6</span><span class="chip">1.7</span>
    <span class="chip">8.x</span><span class="chip">9.x</span>
  </div>
</div>

<section class="section" id="come-funziona">
  <div class="wrap">
    <div class="section__head center">
      <h2>Dal primo messaggio al negozio che funziona</h2>
      <p class="lede">Non serve aprire ticket n&eacute; compilare moduli. Ci racconti cosa non va,
      guardiamo il problema e ti diciamo subito se possiamo risolverlo con il trasferimento.</p>
    </div>
    <div class="steps">
      {steps}
    </div>
  </div>
</section>

<section class="section section--cream2">
  <div class="wrap">
    <div class="section__head center"><h2>I problemi che ci portano pi&ugrave; spesso</h2></div>
    <div class="cards">
      {cards}
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="offer">
      <div>
        <h2>Perch&eacute; lo facciamo gratis</h2>
        <p>Perch&eacute; diventi nostro cliente hosting. Tu smetti di pagare due fornitori diversi
        &mdash; uno per lo spazio web e uno per chi ti sistema il sito &mdash; e noi ci prendiamo
        carico di entrambe le cose. Il lavoro tecnico lo assorbiamo noi: quello che paghi &egrave;
        l&rsquo;hosting, niente altro.</p>
        <a class="btn btn--light" href="gratis.html">Vedi come funziona</a>
      </div>
      <ul class="offer__list">
        {offer_items}
      </ul>
    </div>
  </div>
</section>

<section class="section section--cream">
  <div class="wrap">
    <div class="section__head center"><h2>Domande frequenti</h2></div>
    <div class="faq">
      {faqs}
    </div>
  </div>
</section>
""" + cta("Il tuo negozio &egrave; fermo? Parliamone adesso.",
          "Due righe su WhatsApp bastano per capire se possiamo aiutarti.")


def faq(q, a, open_=False):
    return f'<details{" open" if open_ else ""}><summary>{q}</summary><p>{a}</p></details>'


# ================================================== PAGINA 2: ASSISTENZA
def page_assistenza():
    cards = "\n      ".join([
        card(I_ALERT,  "Errori critici e negozio offline", "Pagina bianca, errore 500, checkout che si blocca a met&agrave;. Risaliamo alla causa leggendo i log, non procedendo per tentativi."),
        card(I_REFRESH,"Aggiornamenti che si sono rotti", "Aggiornamenti interrotti a met&agrave;, tema incompatibile, moduli che smettono di funzionare dopo il passaggio di versione."),
        card(I_BOLT,   "Prestazioni e lentezza", "Pagine che impiegano troppo a caricare, backoffice pesante, ricerca prodotti lenta sui cataloghi grandi."),
        card(I_LAYERS, "Conflitti tra moduli", "Due moduli che si sovrascrivono a vicenda, override che si accavallano, funzioni che smettono di rispondere senza un errore visibile."),
        card(I_CART,   "Ordini, pagamenti e IVA", "Ordini che non arrivano, notifiche che non partono, aliquote e regole fiscali configurate male."),
        card(I_SHIELD, "Sicurezza", "Installazioni compromesse, file modificati, accessi non autorizzati al pannello di amministrazione."),
    ])
    work = "\n      ".join([
        step(1, "Backup prima di toccare qualsiasi cosa", "Copia completa di file e database prima di ogni intervento. Se qualcosa non va, si torna indietro in pochi minuti."),
        step(2, "Prima l&rsquo;ambiente di prova, poi il negozio vero", "Le modifiche importanti le proviamo su una copia. Sul negozio online arriva solo ci&ograve; che ha gi&agrave; funzionato altrove."),
        step(3, "Ti diciamo cosa abbiamo fatto", "Chiudiamo ogni intervento con un riepilogo scritto: quali file abbiamo toccato, per quale motivo e che effetto ha avuto. Niente scatole nere."),
    ])
    return f"""
<section class="hero hero--sm">
  <div class="wrap">
    <p class="eyebrow">Assistenza tecnica specializzata</p>
    <h1>Assistenza PrestaShop, fatta da chi lavora solo su PrestaShop</h1>
    <p class="hero__sub">Non siamo un&rsquo;agenzia generalista che tocca un po&rsquo; di tutto.
    Lavoriamo su PrestaShop tutti i giorni: conosciamo i punti in cui si rompe, i moduli che
    creano conflitti e le versioni che danno problemi in aggiornamento.</p>
    <div class="hero__cta">
      <a class="btn btn--primary" href="{WA}" target="_blank" rel="noopener">Scrivici su WhatsApp</a>
      <a class="btn btn--ghost" href="gratis.html">Fallo risolvere gratis</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section__head center"><h2>Su cosa interveniamo</h2></div>
    <div class="cards cards--3">
      {cards}
    </div>
  </div>
</section>

<section class="section section--cream2">
  <div class="wrap">
    <div class="section__head center">
      <h2>Come lavoriamo</h2>
      <p class="lede">Tre regole che non saltiamo mai, nemmeno per le urgenze.</p>
    </div>
    <div class="steps">
      {work}
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="offer">
      <div>
        <h2>Le tue credenziali restano tue</h2>
        <p>Accediamo con i dati che ci fornisci e puoi revocarli quando vuoi. Prima di ogni
        intervento eseguiamo un backup completo. I tuoi dati non vengono mai condivisi con
        nessuno.</p>
        <a class="btn btn--light" href="contattaci.html">Parlaci del tuo caso</a>
      </div>
      <ul class="offer__list">
        <li>{CHECK_SVG} Backup completo prima di ogni modifica</li>
        <li>{CHECK_SVG} Accessi revocabili in qualsiasi momento</li>
        <li>{CHECK_SVG} Riepilogo scritto di ogni intervento</li>
        <li>{CHECK_SVG} Nessuna condivisione con terze parti</li>
      </ul>
    </div>
  </div>
</section>
""" + cta("Raccontaci cosa non funziona",
          "Guardiamo il problema senza impegno e ti diciamo con che tempi si risolve.")


# ====================================================== PAGINA 3: GRATIS
def page_gratis():
    incl = "\n        ".join(f"<li>{CHECK_SVG} {t}</li>" for t in [
        "Migrazione completa di file, database e caselle email",
        "Trasferimento del dominio, seguito da noi passo per passo",
        "Certificato SSL installato e configurato",
        "Risoluzione del problema tecnico che ti ha bloccato il negozio",
        "Verifica dopo lo spostamento: ordini, pagamenti, email",
        "Nessuna interruzione di servizio durante il passaggio",
    ])
    steps = "\n      ".join([
        step(1, "Ci scrivi e ci racconti il problema", f"Bastano due righe su WhatsApp al {TEL1}. Ti risponde un tecnico, non un modulo di contatto."),
        step(2, "Verifichiamo che il tuo caso rientri", "Guardiamo il negozio e ti confermiamo se il problema &egrave; coperto dal servizio gratuito. Se non lo &egrave;, te lo diciamo subito e senza costi."),
        step(3, "Prepariamo la copia sui nostri server", "Ricostruiamo il negozio sul nuovo hosting e lo proviamo. Il tuo sito attuale resta online e funzionante per tutto il tempo."),
        step(4, "Sistemiamo il problema", "Interveniamo sulla copia nuova, dove possiamo lavorare con calma senza rischiare di far danni sul negozio che sta vendendo."),
        step(5, "Spostiamo il dominio", "Solo quando tutto funziona spostiamo il dominio. Il passaggio &egrave; questione di minuti e lo pianifichiamo con te nell&rsquo;orario che preferisci."),
    ])
    # Le due domande su prezzi/durata dipendono da dati che il cliente non ha
    # ancora dato: in anteprima restano segnate in giallo, nel plugin le
    # ometto invece di pubblicare un segnaposto o un prezzo inventato.
    prezzi = [
        ("Sono vincolato per un periodo minimo?", '<span class="ph">[Da completare &mdash; dimmi la durata del contratto hosting]</span>'),
        ("Quanto costa l&rsquo;hosting?", '<span class="ph">[Da completare &mdash; dimmi i tuoi piani e i prezzi]</span>'),
    ] if MODE == "preview" else []
    faqs = "\n      ".join(faq(q, a, i == 0) for i, (q, a) in enumerate(prezzi + [
        ("E se dopo voglio andarmene?", "Ti diamo una copia completa di file e database e ti aiutiamo a spostarti. Il negozio &egrave; tuo."),
        ("Il trasferimento del dominio &egrave; complicato?", "Ce ne occupiamo noi. A te chiediamo solo il codice di autorizzazione del tuo attuale fornitore e ti spieghiamo dove trovarlo."),
        ("Perder&ograve; le email del dominio?", "No. Spostiamo anche le caselle di posta con i messaggi gi&agrave; presenti."),
    ]))
    return f"""
<section class="hero hero--sm">
  <div class="wrap">
    <p class="eyebrow">L&rsquo;offerta</p>
    <h1>Trasferisci hosting e dominio da noi. Il problema lo risolviamo gratis.</h1>
    <p class="hero__sub">Un&rsquo;offerta semplice, senza clausole scritte piccole: sposti il tuo
    PrestaShop sui nostri server e ci facciamo carico noi dell&rsquo;intervento tecnico che ti
    serve per rimetterlo in funzione.</p>
    <div class="hero__cta">
      <a class="btn btn--primary" href="{WA}" target="_blank" rel="noopener">Scrivici su WhatsApp</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="offer">
      <div>
        <h2>Cosa &egrave; compreso</h2>
        <p>Tutto quello che serve per portare il negozio da dove si trova adesso ai nostri
        server, funzionante e senza il problema che lo bloccava.</p>
      </div>
      <ul class="offer__list">
        {incl}
      </ul>
    </div>
  </div>
</section>

<section class="section section--cream2">
  <div class="wrap">
    <div class="section__head center"><h2>Come funziona, passo per passo</h2></div>
    <div class="steps steps--5">
      {steps}
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section__head center">
      <h2>Le condizioni, dette chiaramente</h2>
      <p class="lede">Preferiamo essere onesti prima che dopo.</p>
    </div>
    <div class="cond">
      <ul>
        <li>L&rsquo;intervento gratuito &egrave; legato al trasferimento di hosting <b>e</b> dominio da noi.</li>
        <li>Copre la risoluzione del problema esistente, non lo sviluppo di funzioni nuove.</li>
        <li>Se serve un lavoro molto pi&ugrave; ampio (rifacimento del tema, moduli su misura, migrazione a una versione maggiore) te lo diciamo prima e ti facciamo una proposta a parte. Sei libero di rifiutare.</li>
        <li>Se guardando il negozio capiamo di non poterti aiutare, te lo diciamo e finisce l&igrave;, senza che tu abbia speso nulla.</li>
      </ul>
    </div>
  </div>
</section>

<section class="section section--cream">
  <div class="wrap">
    <div class="section__head center"><h2>Domande frequenti</h2></div>
    <div class="faq">
      {faqs}
    </div>
  </div>
</section>
""" + cta("Vediamo se il tuo caso rientra",
          "Scrivici e in poco tempo sai se possiamo sistemarti il negozio senza costi.")


# ================================================== PAGINA 4: CONTATTACI
def page_contattaci():
    return f"""
<section class="hero hero--sm">
  <div class="wrap">
    <p class="eyebrow">Parliamone</p>
    <h1>Scrivici. Ti risponde un tecnico, non un centralino.</h1>
    <p class="hero__sub">Il modo pi&ugrave; veloce &egrave; WhatsApp: puoi anche mandarci un vocale
    o uno screenshot dell&rsquo;errore. Se preferisci scrivere, trovi il modulo qui sotto.</p>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="contact">

      <div class="contact__cards">
        <a class="ccard ccard--wa" href="{WA}" target="_blank" rel="noopener">
          <h3>WhatsApp</h3>
          <p>Il canale pi&ugrave; rapido. Mandaci un messaggio anche fuori orario: lo leggiamo appena rientriamo.</p>
          <span class="ccard__v">{TEL1}</span>
        </a>
        <a class="ccard" href="mailto:{EMAIL}">
          <h3>Email</h3>
          <p>Per richieste articolate o per allegare file e documentazione.</p>
          <span class="ccard__v">{EMAIL}</span>
        </a>
        <a class="ccard" href="tel:+{TEL2_RAW}">
          <h3>Telefono</h3>
          <p>{"Attivo " + ORARI if MODE == "preview" else "Chiamaci pure negli orari di ufficio."}</p>
          <span class="ccard__v">{TEL2}</span>
        </a>
        <div class="ccard">
          <h3>Dove siamo</h3>
          <p><b>Sede legale</b><br>{SEDE_LEGALE}</p>
          <p style="margin-top:8px"><b>Sede operativa</b><br>{SEDE_OPER}</p>
        </div>
      </div>

      <div class="contact__form">
        <div class="formcard">
          <h2>Raccontaci il problema</h2>
          <p class="formcard__note">Nell&rsquo;anteprima il modulo &egrave; solo grafico. Una volta
          in WordPress lo collego a Contact Form 7, che sul tuo sito &egrave; gi&agrave; installato,
          e le richieste arrivano a {EMAIL}.</p>
          <form onsubmit="return false;">
            <div class="f2">
              <label>Nome e cognome *<input type="text" required></label>
              <label>Email *<input type="email" required></label>
            </div>
            <div class="f2">
              <label>Telefono<input type="tel"></label>
              <label>Indirizzo del negozio *<input type="url" placeholder="https://"></label>
            </div>
            <label>Versione di PrestaShop, se la conosci
              <select>
                <option>Non lo so</option><option>1.6</option><option>1.7</option>
                <option>8.x</option><option>9.x</option>
              </select>
            </label>
            <label>Descrivi il problema *<textarea rows="5" required></textarea></label>
            <label class="chk"><input type="checkbox" required> Ho letto l&rsquo;informativa privacy e acconsento al trattamento dei dati.</label>
            <button class="btn btn--primary" type="submit">Invia la richiesta</button>
          </form>
          <p class="formcard__foot">I dati che ci lasci servono solo a ricontattarti: non li cediamo a nessuno.</p>
        </div>
      </div>

    </div>
  </div>
</section>
""" + cta("Il negozio &egrave; fermo adesso?",
          "Non aspettare la risposta all&rsquo;email: scrivici su WhatsApp e guardiamo subito.")


BODIES = {
    "index": page_index,
    "assistenza": page_assistenza,
    "gratis": page_gratis,
    "contattaci": page_contattaci,
}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for p in PAGES:
        (OUT / f"{p}.html").write_text(head(p) + BODIES[p]() + FOOTER, encoding="utf-8")
        print(f"[{MODE}] scritta", p + ".html")

if __name__ == "__main__":
    main()
