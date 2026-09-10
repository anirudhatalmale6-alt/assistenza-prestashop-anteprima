#!/usr/bin/env python3
"""
Genera le 4 pagine come DATI ELEMENTOR veri (_elementor_data), non come HTML.

Perche': il cliente deve poter aprire ogni pagina in Elementor e cambiare un
testo o un bottone cliccandoci sopra, e Yoast deve poter analizzare il
contenuto. Con l'HTML servito da plugin nessuna delle due cose era possibile.

Ogni testo sta dentro un widget heading / text-editor / button, quindi e'
modificabile dall'editor. Il layout usa i container flex nativi di Elementor.
Le rifiniture (ombre, card, chip) restano nel foglio di stile del plugin,
agganciato via classi CSS sui singoli elementi.

    python3 build_elementor.py        -> plugin/webhouse-pagine/elementor/*.json
"""
import json, pathlib, itertools

OUT = pathlib.Path(__file__).parent / "plugin/webhouse-pagine/elementor"

# ------------------------------------------------------------------ dati reali
AZIENDA   = "WebHouse S.a.s."
EMAIL     = "info@webhousesas.net"
TEL1      = "+39 392 042 6808"
TEL1_RAW  = "393920426808"
TEL2      = "+39 366 361 9529"
TEL2_RAW  = "393663619529"
CF        = "GNVMRC71A05L407Z"
PIVA      = "05143900263"
SEDE_LEG  = "via Sant&rsquo;Elena Imperatrice 25 &ndash; 31100 Treviso"
SEDE_OPE  = "via Jacopo Bernardi 13/a &ndash; 31100 Treviso (TV)"
WA        = f"https://wa.me/{TEL1_RAW}"

BLU       = "#003C6C"
BLU_SCURO = "#002A4D"
ARANCIO   = "#FF8C00"
INK       = "#101013"
INK_SOFT  = "#4A4A52"
GRIGIO    = "#EFF3F7"
GRIGIO2   = "#F5F7F9"

_ids = itertools.count(1)
def nid(p="e"):
    return f"{p}{next(_ids):07d}"


# --------------------------------------------------------------- primitive
def px(t=0, r=0, b=0, l=0):
    return {"unit": "px", "top": str(t), "right": str(r),
            "bottom": str(b), "left": str(l), "isLinked": False}


def container(children, *, bg=None, pad=(80, 20, 80, 20), width="boxed",
              row=False, wrap=True, gap=None, css=None, extra=None, w=None,
              align=None, justify=None):
    s = {"content_width": width}
    if bg:
        s["background_background"] = "classic"
        s["background_color"] = bg
    if pad:
        s["padding"] = px(*pad)
    if row:
        s["flex_direction"] = "row"
        s["flex_wrap"] = "wrap" if wrap else "nowrap"
    if gap is not None:
        s["flex_gap"] = {"unit": "px", "size": gap, "column": str(gap), "row": str(gap)}
    if align:
        s["flex_align_items"] = align
    if justify:
        s["flex_justify_content"] = justify
    if w:
        # La larghezza delle colonne NON la passo dai controlli di Elementor:
        # il nome del controllo cambia fra le versioni (qui provo su 4.3, il
        # cliente ha la 4.2) e su questa build non genera alcun CSS. Uso una
        # classe mia, che si comporta uguale su qualunque versione.
        s["_flex_size"] = "none"
        cls = f"wh-w{str(w).replace('.', '-')}"
        s["_css_classes"] = (s.get("_css_classes", "") + " " + cls).strip()
    if css:
        s["_css_classes"] = (css + " " + s.get("_css_classes", "")).strip()
    if extra:
        s.update(extra)
    # I CONTAINER usano "css_classes", i WIDGET "_css_classes": nomi diversi, e
    # cambiano fra le versioni di Elementor. Scrivo entrambe le chiavi: quella
    # che la versione installata non conosce viene semplicemente ignorata.
    if s.get("_css_classes"):
        s["css_classes"] = s["_css_classes"]
    if s.get("_element_id"):
        s["_element_id"] = s["_element_id"]
    return {"id": nid("c"), "elType": "container", "settings": s, "elements": children}


def widget(kind, settings):
    return {"id": nid("w"), "elType": "widget", "widgetType": kind,
            "settings": settings, "elements": []}


def heading(text, tag="h2", color=INK, size=None, align=None, css=None, mb=None):
    s = {"title": text, "header_size": tag, "title_color": color}
    if size:
        s["typography_typography"] = "custom"
        s["typography_font_size"] = {"unit": "px", "size": size}
        s["typography_font_weight"] = "700"
        s["typography_line_height"] = {"unit": "em", "size": 1.12}
        s["typography_letter_spacing"] = {"unit": "px", "size": -1}
    if align:
        s["align"] = align
    if css:
        s["_css_classes"] = css
    if mb is not None:
        s["_margin"] = px(0, 0, mb, 0)
    return widget("heading", s)


def testo(html_, color=INK_SOFT, size=16, align=None, css=None, mb=None):
    s = {"editor": html_, "text_color": color,
         "typography_typography": "custom",
         "typography_font_size": {"unit": "px", "size": size},
         "typography_line_height": {"unit": "em", "size": 1.62}}
    if align:
        s["align"] = align
    if css:
        s["_css_classes"] = css
    if mb is not None:
        s["_margin"] = px(0, 0, mb, 0)
    return widget("text-editor", s)


def bottone(text, url, *, bg=BLU, colore="#fff", esterno=True, css=None, size="md"):
    return widget("button", {
        "text": text,
        "link": {"url": url, "is_external": "true" if esterno else "", "nofollow": ""},
        "background_color": bg,
        "button_text_color": colore,
        "border_radius": px(4, 4, 4, 4),
        "text_padding": px(14, 24, 14, 24),
        "size": size,
        "typography_typography": "custom",
        "typography_font_size": {"unit": "px", "size": 16},
        "typography_font_weight": "500",
        **({"_css_classes": css} if css else {}),
    })


def html_widget(markup, css=None):
    s = {"html": markup}
    if css:
        s["_css_classes"] = css
    return widget("html", s)


def occhiello(text):
    return testo(f"<p>{text}</p>", color=ARANCIO, size=15, mb=14,
                 css="wh-eyebrow")


# --------------------------------------------------------- blocchi riusabili
SVG_ICONE = {
    "refresh": '<path d="M21 12a9 9 0 1 1-3-6.7"/><path d="M21 3v6h-6"/>',
    "layers":  '<path d="M12 2 3 7l9 5 9-5-9-5Z"/><path d="M3 17l9 5 9-5"/><path d="M3 12l9 5 9-5"/>',
    "server":  '<rect x="2" y="3" width="20" height="7" rx="2"/><rect x="2" y="14" width="20" height="7" rx="2"/><path d="M6 6.5h.01M6 17.5h.01"/>',
    "alert":   '<path d="M10.3 3.6 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.6a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "chart":   '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/>',
    "lock":    '<rect x="3" y="11" width="18" height="10" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "file":    '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6"/><path d="M12 12v6"/><path d="M9 15h6"/>',
    "bolt":    '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8Z"/>',
    "shield":  '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/>',
    "cart":    '<circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.7 13.4a2 2 0 0 0 2 1.6h9.7a2 2 0 0 0 2-1.6L23 6H6"/>',
}


def icona(nome):
    return ('<div class="wh-ico"><svg viewBox="0 0 24 24" fill="none" stroke="' + BLU +
            '" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">' +
            SVG_ICONE[nome] + '</svg></div>')


def card(nome_icona, titolo, corpo, w=23):
    return container([
        html_widget(icona(nome_icona)),
        heading(titolo, "h3", size=18, align="center", mb=8),
        testo(f"<p>{corpo}</p>", size=15, align="center"),
    ], pad=(30, 24, 30, 24), w=w, css="wh-card", bg="#fff")


def passo(numero, titolo, corpo, w=31):
    return container([
        html_widget(f'<div class="wh-num">{numero}</div>'),
        heading(titolo, "h3", size=20, mb=10),
        testo(f"<p>{corpo}</p>", size=15.5),
    ], pad=(32, 28, 32, 28), w=w, css="wh-card wh-step", bg="#fff")


def sezione_titolo(titolo, sottotitolo=None):
    figli = [heading(titolo, "h2", size=42, align="center", mb=16 if sottotitolo else 0)]
    if sottotitolo:
        figli.append(testo(f"<p>{sottotitolo}</p>", size=18, align="center"))
    return container(figli, pad=(0, 0, 44, 0), css="wh-sechead")


def faq(coppie):
    return widget("accordion", {
        "tabs": [{"_id": nid("t")[:7], "tab_title": q, "tab_content": f"<p>{a}</p>"}
                 for q, a in coppie],
        "title_color": INK,
        "tab_active_color": BLU,
        "content_color": INK_SOFT,
        "border_width": {"unit": "px", "size": 1},
        "_css_classes": "wh-faq",
    })


def cta_finale(titolo, testo_):
    return container([
        heading(titolo, "h2", color="#fff", size=40, align="center", mb=16),
        testo(f"<p>{testo_}</p>", color="rgba(255,255,255,.75)", size=18, align="center", mb=26),
        container([bottone(f"Scrivici su WhatsApp {TEL1}", WA)],
                  pad=None, row=True, justify="center"),
    ], bg=INK, pad=(80, 20, 80, 20), css="wh-cta")


def footer():
    col1 = container([
        html_widget('<div class="wh-logo wh-logo--dark"><span>W</span><i>Web<b>House</b></i></div>'),
        testo(f"<p>Assistenza tecnica PrestaShop e hosting gestito.<br>{AZIENDA}</p>",
              color="rgba(255,255,255,.66)", size=15),
    ], pad=None, w=30)
    col2 = container([
        heading("Sedi", "h4", color="#fff", size=15, mb=14),
        testo(f"<p><b>Sede legale</b><br>{SEDE_LEG}</p>"
              f"<p style='margin-top:10px'><b>Sede operativa</b><br>{SEDE_OPE}</p>",
              color="rgba(255,255,255,.66)", size=15),
    ], pad=None, w=34)
    col3 = container([
        heading("Contatti", "h4", color="#fff", size=15, mb=14),
        testo(f"<p><a href='tel:+{TEL1_RAW}'>{TEL1}</a><br>"
              f"<a href='tel:+{TEL2_RAW}'>{TEL2}</a><br>"
              f"<a href='mailto:{EMAIL}'>{EMAIL}</a></p>"
              f"<p style='margin-top:10px'>P.IVA {PIVA}<br>C.F. {CF}</p>",
              color="rgba(255,255,255,.66)", size=15),
    ], pad=None, w=30)
    return container([
        container([col1, col2, col3], pad=None, row=True, gap=40),
        html_widget(f'<div class="wh-ftr-bar">&copy; {AZIENDA} &mdash; Tutti i diritti riservati</div>'),
    ], bg=INK, pad=(60, 20, 34, 20), css="wh-footer")


def testata(attiva):
    voci = [("Home", "index"), ("Assistenza PrestaShop", "assistenza"),
            ("Gratis", "gratis"), ("Contattaci", "contattaci")]
    link = "".join(
        f'<a href="{{{{{p}}}}}"{" class=\"is-active\"" if p == attiva else ""}>{t}</a>'
        for t, p in voci)
    return html_widget(
        '<div class="wh-hdr"><div class="wh-hdr__in">'
        '<a class="wh-logo" href="{{index}}"><span>W</span><i>Web<b>House</b></i></a>'
        f'<nav class="wh-nav" id="wh-nav">{link}</nav>'
        f'<a class="wh-hdr__cta" href="{WA}" target="_blank" rel="noopener">Scrivici su WhatsApp</a>'
        '<button class="wh-burger" id="wh-burger" aria-label="Menu"><span></span><span></span><span></span></button>'
        '</div></div>')


# ================================================================== PAGINE
HERO_SVG = ('<div class="wh-hero-art"><svg viewBox="0 0 560 360" role="img" '
            'aria-label="Negozio trasferito su un nuovo server">'
            '<defs><linearGradient id="whg" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{BLU}"/><stop offset="1" stop-color="{BLU_SCURO}"/>'
            '</linearGradient></defs>'
            '<rect x="6" y="34" width="348" height="238" rx="14" fill="#fff" stroke="#DDE3EA"/>'
            '<path d="M6 48a14 14 0 0 1 14-14h320a14 14 0 0 1 14 14v14H6V48Z" fill="#101013"/>'
            '<circle cx="30" cy="48" r="5" fill="#FF5F57"/><circle cx="48" cy="48" r="5" fill="#FEBC2E"/>'
            '<circle cx="66" cy="48" r="5" fill="#28C840"/>'
            '<rect x="92" y="41" width="176" height="14" rx="7" fill="#2C2C33"/>'
            '<rect x="28" y="84" width="118" height="12" rx="6" fill="#101013"/>'
            '<rect x="28" y="106" width="192" height="9" rx="4.5" fill="#C3CCD6"/>'
            '<rect x="28" y="130" width="92" height="32" rx="5" fill="url(#whg)"/>'
            '<rect x="28" y="182" width="94" height="68" rx="9" fill="#F5F7F9" stroke="#DDE3EA"/>'
            '<rect x="133" y="182" width="94" height="68" rx="9" fill="#F5F7F9" stroke="#DDE3EA"/>'
            '<rect x="238" y="182" width="94" height="68" rx="9" fill="#F5F7F9" stroke="#DDE3EA"/>'
            f'<rect x="42" y="222" width="56" height="10" rx="5" fill="{BLU}"/>'
            f'<rect x="147" y="222" width="56" height="10" rx="5" fill="{BLU}"/>'
            f'<rect x="252" y="222" width="56" height="10" rx="5" fill="{BLU}"/>'
            f'<path d="M366 152 h44" stroke="{ARANCIO}" stroke-width="3" fill="none" stroke-dasharray="8 7" stroke-linecap="round"/>'
            f'<path d="M404 143 l12 9 -12 9" stroke="{ARANCIO}" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            '<rect x="424" y="60" width="130" height="186" rx="14" fill="url(#whg)"/>'
            '<rect x="443" y="86" width="92" height="28" rx="7" fill="rgba(255,255,255,.22)"/>'
            '<rect x="443" y="125" width="92" height="28" rx="7" fill="rgba(255,255,255,.22)"/>'
            '<rect x="443" y="164" width="92" height="28" rx="7" fill="rgba(255,255,255,.22)"/>'
            f'<circle cx="458" cy="100" r="4.5" fill="{ARANCIO}"/>'
            f'<circle cx="458" cy="139" r="4.5" fill="{ARANCIO}"/>'
            f'<circle cx="458" cy="178" r="4.5" fill="{ARANCIO}"/>'
            f'<rect x="392" y="268" width="146" height="54" rx="27" fill="{ARANCIO}"/>'
            '<text x="465" y="302" text-anchor="middle" fill="#fff" font-family="Inter,sans-serif" '
            'font-size="20" font-weight="700" letter-spacing="1">GRATIS</text>'
            '</svg></div>')


def pagina_index():
    hero = container([
        container([
            occhiello("Assistenza PrestaShop &mdash; trasferisci e risolvi"),
            heading("Negozio PrestaShop bloccato? Lo rimettiamo in piedi noi, gratis.",
                    "h1", size=50, mb=20),
            testo("<p>Sposta hosting e dominio su di noi e ci occupiamo noi del problema che ti "
                  "blocca il negozio, <strong>senza costi aggiuntivi</strong>. Un tecnico dedicato, "
                  "un interlocutore solo, nessun preventivo a sorpresa.</p>", size=19, mb=28),
            container([
                bottone("Scrivici su WhatsApp", WA),
                bottone("Come funziona", "#come-funziona", bg="rgba(0,0,0,0)",
                        colore=BLU, esterno=False, css="wh-btn-ghost"),
            ], pad=None, row=True, gap=12),
            testo(f"<p>Un servizio di {AZIENDA} &mdash; Treviso</p>", size=14, mb=0),
        ], pad=None, w=52),
        container([html_widget(HERO_SVG)], pad=None, w=44),
    ], bg=GRIGIO, pad=(72, 20, 76, 20), row=True, gap=40, align="center")

    strip = container([
        html_widget('<div class="wh-strip"><span>Lavoriamo su tutte le versioni:</span>'
                    '<em>PrestaShop 1.6</em><em>1.7</em><em>8.x</em><em>9.x</em></div>')
    ], bg=GRIGIO, pad=(0, 20, 26, 20))

    passi = container([
        sezione_titolo("Dal primo messaggio al negozio che funziona",
                       "Non serve aprire ticket n&eacute; compilare moduli. Ci racconti cosa non va, "
                       "guardiamo il problema e ti diciamo subito se possiamo risolverlo con il trasferimento."),
        container([
            passo(1, "Raccontaci il problema",
                  "Scrivici su WhatsApp con due righe o un messaggio vocale. Ti risponde una persona "
                  "che conosce PrestaShop, non un centralino."),
            passo(2, "Guardiamo cosa succede davvero",
                  "Analizziamo il malfunzionamento senza chiederti nulla in cambio. Ti spieghiamo in "
                  "parole semplici da cosa dipende e cosa serve per sistemarlo."),
            passo(3, "Trasferisci e risolviamo",
                  "Sposti hosting e dominio da noi, ci occupiamo noi della migrazione e del problema. "
                  "Il negozio resta online per tutta l&rsquo;operazione."),
        ], pad=None, row=True, gap=26),
    ], pad=(84, 20, 84, 20), extra={"_element_id": "come-funziona"})

    servizi = container([
        sezione_titolo("I problemi che ci portano pi&ugrave; spesso"),
        container([
            card("refresh", "Aggiornamenti", "Portiamo PrestaShop, tema e moduli a una versione aggiornata, con backup prima di ogni passaggio."),
            card("layers", "Moduli su misura", "Quando il modulo che ti serve non esiste, lo sviluppiamo noi sulle esigenze del tuo negozio."),
            card("server", "Migrazione e hosting", "Spostiamo il negozio su server o dominio nuovo senza interruzioni e senza perdere ordini."),
            card("alert", "Errori e pagine bianche", "Individuiamo l&rsquo;origine degli errori critici che bloccano il negozio e li correggiamo alla radice."),
            card("chart", "SEO e struttura", "Sistemiamo la struttura tecnica perch&eacute; Google legga bene il negozio: URL, tempi di risposta, dati strutturati."),
            card("lock", "Accesso al backoffice", "Recuperiamo l&rsquo;accesso al pannello e risolviamo le anomalie su ordini, prodotti e permessi."),
            card("file", "Nuove pagine", "Creiamo pagine e sezioni nuove: landing, categorie, banner promozionali, pagine istituzionali."),
            card("bolt", "Negozio lento", "Misuriamo dove si perde tempo nel caricamento e interveniamo su cache, query, immagini e server."),
        ], pad=None, row=True, gap=22),
    ], bg=GRIGIO2, pad=(84, 20, 84, 20))

    offerta = container([
        container([
            container([
                heading("Perch&eacute; lo facciamo gratis", "h2", color="#fff", size=40, mb=18),
                testo("<p>Perch&eacute; diventi nostro cliente hosting. Tu smetti di pagare due "
                      "fornitori diversi &mdash; uno per lo spazio web e uno per chi ti sistema il "
                      "sito &mdash; e noi ci prendiamo carico di entrambe le cose. Il lavoro tecnico "
                      "lo assorbiamo noi: quello che paghi &egrave; l&rsquo;hosting, niente altro.</p>",
                      color="rgba(255,255,255,.9)", size=17.5, mb=26),
                bottone("Vedi come funziona", "{{gratis}}", bg="#fff", colore=BLU, esterno=False),
            ], pad=None, w=55),
            container([html_widget(
                '<ul class="wh-check">'
                '<li>Migrazione di file, database e caselle email</li>'
                '<li>Trasferimento del dominio seguito da noi</li>'
                '<li>Certificato SSL installato e configurato</li>'
                '<li>Risoluzione del problema che ti blocca</li>'
                '<li>Nessuna interruzione durante il passaggio</li></ul>')], pad=None, w=41),
        ], bg=BLU, pad=(56, 52, 56, 52), row=True, gap=40, align="center", css="wh-offer"),
    ], pad=(84, 20, 84, 20))

    faq_sec = container([
        sezione_titolo("Domande frequenti"),
        container([faq([
            ("Devo pagare qualcosa per l&rsquo;analisi?",
             "No. Guardiamo il problema e ti diciamo cosa serve senza chiederti nulla."),
            ("Il negozio resta online durante il trasferimento?",
             "S&igrave;. Prepariamo tutto sul nuovo server e spostiamo il dominio solo quando la copia funziona correttamente."),
            ("Su quali versioni di PrestaShop lavorate?",
             "Su tutte, comprese le installazioni vecchie rimaste indietro di diverse versioni."),
            ("E se il problema &egrave; troppo grosso?",
             "Te lo diciamo prima, con onest&agrave;. Se non rientra nel servizio gratuito ti facciamo una proposta chiara e decidi tu."),
        ])], pad=None, w=72),
    ], bg=GRIGIO, pad=(84, 20, 84, 20), align="center")

    return [testata("index"), hero, strip, passi, servizi, offerta, faq_sec,
            cta_finale("Il tuo negozio &egrave; fermo? Parliamone adesso.",
                       "Due righe su WhatsApp bastano per capire se possiamo aiutarti."),
            footer()]


def pagina_assistenza():
    hero = container([
        occhiello("Assistenza tecnica specializzata"),
        heading("Assistenza PrestaShop, fatta da chi lavora solo su PrestaShop", "h1", size=46, mb=18),
        testo("<p>Non siamo un&rsquo;agenzia generalista che tocca un po&rsquo; di tutto. Lavoriamo "
              "su PrestaShop tutti i giorni: conosciamo i punti in cui si rompe, i moduli che creano "
              "conflitti e le versioni che danno problemi in aggiornamento.</p>", size=19, mb=28),
        container([
            bottone("Scrivici su WhatsApp", WA),
            bottone("Fallo risolvere gratis", "{{gratis}}", bg="rgba(0,0,0,0)", colore=BLU,
                    esterno=False, css="wh-btn-ghost"),
        ], pad=None, row=True, gap=12),
    ], bg=GRIGIO, pad=(64, 20, 68, 20))

    interventi = container([
        sezione_titolo("Su cosa interveniamo"),
        container([
            card("alert", "Errori critici e negozio offline", "Pagina bianca, errore 500, checkout che si blocca a met&agrave;. Risaliamo alla causa leggendo i log, non per tentativi.", w=31),
            card("refresh", "Aggiornamenti che si sono rotti", "Aggiornamenti interrotti a met&agrave;, tema incompatibile, moduli che smettono di funzionare dopo il passaggio di versione.", w=31),
            card("bolt", "Prestazioni e lentezza", "Pagine che impiegano troppo a caricare, backoffice pesante, ricerca prodotti lenta sui cataloghi grandi.", w=31),
            card("layers", "Conflitti tra moduli", "Due moduli che si sovrascrivono a vicenda, override che si accavallano, funzioni che smettono di rispondere senza un errore visibile.", w=31),
            card("cart", "Ordini, pagamenti e IVA", "Ordini che non arrivano, notifiche che non partono, aliquote e regole fiscali configurate male.", w=31),
            card("shield", "Sicurezza", "Installazioni compromesse, file modificati, accessi non autorizzati al pannello di amministrazione.", w=31),
        ], pad=None, row=True, gap=22),
    ], pad=(84, 20, 84, 20))

    metodo = container([
        sezione_titolo("Come lavoriamo", "Tre regole che non saltiamo mai, nemmeno per le urgenze."),
        container([
            passo(1, "Backup prima di toccare qualsiasi cosa",
                  "Copia completa di file e database prima di ogni intervento. Se qualcosa non va, si torna indietro in pochi minuti."),
            passo(2, "Prima l&rsquo;ambiente di prova, poi il negozio vero",
                  "Le modifiche importanti le proviamo su una copia. Sul negozio online arriva solo ci&ograve; che ha gi&agrave; funzionato altrove."),
            passo(3, "Ti diciamo cosa abbiamo fatto",
                  "Chiudiamo ogni intervento con un riepilogo scritto: quali file abbiamo toccato, per quale motivo e che effetto ha avuto."),
        ], pad=None, row=True, gap=26),
    ], bg=GRIGIO2, pad=(84, 20, 84, 20))

    sicurezza = container([
        container([
            container([
                heading("Le tue credenziali restano tue", "h2", color="#fff", size=40, mb=18),
                testo("<p>Accediamo con i dati che ci fornisci e puoi revocarli quando vuoi. Prima "
                      "di ogni intervento eseguiamo un backup completo. I tuoi dati non vengono mai "
                      "condivisi con nessuno.</p>", color="rgba(255,255,255,.9)", size=17.5, mb=26),
                bottone("Parlaci del tuo caso", "{{contattaci}}", bg="#fff", colore=BLU, esterno=False),
            ], pad=None, w=55),
            container([html_widget(
                '<ul class="wh-check">'
                '<li>Backup completo prima di ogni modifica</li>'
                '<li>Accessi revocabili in qualsiasi momento</li>'
                '<li>Riepilogo scritto di ogni intervento</li>'
                '<li>Nessuna condivisione con terze parti</li></ul>')], pad=None, w=41),
        ], bg=BLU, pad=(56, 52, 56, 52), row=True, gap=40, align="center", css="wh-offer"),
    ], pad=(84, 20, 84, 20))

    return [testata("assistenza"), hero, interventi, metodo, sicurezza,
            cta_finale("Raccontaci cosa non funziona",
                       "Guardiamo il problema senza impegno e ti diciamo con che tempi si risolve."),
            footer()]


def pagina_gratis():
    hero = container([
        occhiello("L&rsquo;offerta"),
        heading("Trasferisci hosting e dominio da noi. Il problema lo risolviamo gratis.",
                "h1", size=46, mb=18),
        testo("<p>Un&rsquo;offerta semplice, senza clausole scritte piccole: sposti il tuo PrestaShop "
              "sui nostri server e ci facciamo carico noi dell&rsquo;intervento tecnico che ti serve "
              "per rimetterlo in funzione.</p>", size=19, mb=28),
        container([bottone("Scrivici su WhatsApp", WA)], pad=None, row=True),
    ], bg=GRIGIO, pad=(64, 20, 68, 20))

    compreso = container([
        container([
            container([
                heading("Cosa &egrave; compreso", "h2", color="#fff", size=40, mb=18),
                testo("<p>Tutto quello che serve per portare il negozio da dove si trova adesso ai "
                      "nostri server, funzionante e senza il problema che lo bloccava.</p>",
                      color="rgba(255,255,255,.9)", size=17.5),
            ], pad=None, w=45),
            container([html_widget(
                '<ul class="wh-check">'
                '<li>Migrazione completa di file, database e caselle email</li>'
                '<li>Trasferimento del dominio, seguito da noi passo per passo</li>'
                '<li>Certificato SSL installato e configurato</li>'
                '<li>Risoluzione del problema tecnico che ti ha bloccato il negozio</li>'
                '<li>Verifica dopo lo spostamento: ordini, pagamenti, email</li>'
                '<li>Nessuna interruzione di servizio durante il passaggio</li></ul>')], pad=None, w=51),
        ], bg=BLU, pad=(56, 52, 56, 52), row=True, gap=40, align="center", css="wh-offer"),
    ], pad=(84, 20, 84, 20))

    passi = container([
        sezione_titolo("Come funziona, passo per passo"),
        container([
            passo(1, "Ci scrivi e ci racconti il problema",
                  f"Bastano due righe su WhatsApp al {TEL1}. Ti risponde un tecnico, non un modulo di contatto."),
            passo(2, "Verifichiamo che il tuo caso rientri",
                  "Guardiamo il negozio e ti confermiamo se il problema &egrave; coperto dal servizio gratuito. Se non lo &egrave;, te lo diciamo subito e senza costi."),
            passo(3, "Prepariamo la copia sui nostri server",
                  "Ricostruiamo il negozio sul nuovo hosting e lo proviamo. Il tuo sito attuale resta online e funzionante per tutto il tempo."),
            passo(4, "Sistemiamo il problema",
                  "Interveniamo sulla copia nuova, dove possiamo lavorare con calma senza rischiare di far danni sul negozio che sta vendendo."),
            passo(5, "Spostiamo il dominio",
                  "Solo quando tutto funziona spostiamo il dominio. Il passaggio &egrave; questione di minuti e lo pianifichiamo con te nell&rsquo;orario che preferisci."),
        ], pad=None, row=True, gap=26),
    ], bg=GRIGIO2, pad=(84, 20, 84, 20))

    condizioni = container([
        sezione_titolo("Le condizioni, dette chiaramente", "Preferiamo essere onesti prima che dopo."),
        container([html_widget(
            '<ul class="wh-cond">'
            '<li>L&rsquo;intervento gratuito &egrave; legato al trasferimento di hosting <b>e</b> dominio da noi.</li>'
            '<li>Copre la risoluzione del problema esistente, non lo sviluppo di funzioni nuove.</li>'
            '<li>Se serve un lavoro molto pi&ugrave; ampio (rifacimento del tema, moduli su misura, '
            'migrazione a una versione maggiore) te lo diciamo prima e ti facciamo una proposta a parte. '
            'Sei libero di rifiutare.</li>'
            '<li>Se guardando il negozio capiamo di non poterti aiutare, te lo diciamo e finisce l&igrave;, '
            'senza che tu abbia speso nulla.</li></ul>')], pad=None, w=72),
    ], pad=(84, 20, 84, 20), align="center")

    faq_sec = container([
        sezione_titolo("Domande frequenti"),
        container([faq([
            ("E se dopo voglio andarmene?",
             "Ti diamo una copia completa di file e database e ti aiutiamo a spostarti. Il negozio &egrave; tuo."),
            ("Il trasferimento del dominio &egrave; complicato?",
             "Ce ne occupiamo noi. A te chiediamo solo il codice di autorizzazione del tuo attuale fornitore e ti spieghiamo dove trovarlo."),
            ("Perder&ograve; le email del dominio?",
             "No. Spostiamo anche le caselle di posta con i messaggi gi&agrave; presenti."),
        ])], pad=None, w=72),
    ], bg=GRIGIO, pad=(84, 20, 84, 20), align="center")

    return [testata("gratis"), hero, compreso, passi, condizioni, faq_sec,
            cta_finale("Vediamo se il tuo caso rientra",
                       "Scrivici e in poco tempo sai se possiamo sistemarti il negozio senza costi."),
            footer()]


def pagina_contattaci():
    hero = container([
        occhiello("Parliamone"),
        heading("Scrivici. Ti risponde un tecnico, non un centralino.", "h1", size=46, mb=18),
        testo("<p>Il modo pi&ugrave; veloce &egrave; WhatsApp: puoi anche mandarci un vocale o uno "
              "screenshot dell&rsquo;errore. Se preferisci scrivere, trovi il modulo qui sotto.</p>",
              size=19),
    ], bg=GRIGIO, pad=(64, 20, 68, 20))

    contatti = container([
        container([
            container([
                heading("WhatsApp", "h3", size=17, mb=7),
                testo("<p>Il canale pi&ugrave; rapido. Mandaci un messaggio anche fuori orario: lo leggiamo appena rientriamo.</p>", size=14.5, mb=10),
                testo(f"<p><a href='{WA}'>{TEL1}</a></p>", color=ARANCIO, size=15.5),
            ], pad=(22, 24, 22, 24), w=48, css="wh-card wh-card--wa", bg="#fff"),
            container([
                heading("Email", "h3", size=17, mb=7),
                testo("<p>Per richieste articolate o per allegare file e documentazione.</p>", size=14.5, mb=10),
                testo(f"<p><a href='mailto:{EMAIL}'>{EMAIL}</a></p>", color=BLU, size=15.5),
            ], pad=(22, 24, 22, 24), w=48, css="wh-card", bg="#fff"),
            container([
                heading("Telefono", "h3", size=17, mb=7),
                testo("<p>Chiamaci pure negli orari di ufficio.</p>", size=14.5, mb=10),
                testo(f"<p><a href='tel:+{TEL2_RAW}'>{TEL2}</a></p>", color=BLU, size=15.5),
            ], pad=(22, 24, 22, 24), w=48, css="wh-card", bg="#fff"),
            container([
                heading("Dove siamo", "h3", size=17, mb=7),
                testo(f"<p><b>Sede legale</b><br>{SEDE_LEG}</p>"
                      f"<p style='margin-top:8px'><b>Sede operativa</b><br>{SEDE_OPE}</p>", size=14.5),
            ], pad=(22, 24, 22, 24), w=48, css="wh-card", bg="#fff"),
        ], pad=None, row=True, gap=14, w=40),
        container([
            container([
                heading("Raccontaci il problema", "h2", size=28, mb=12),
                widget("shortcode", {"shortcode": "[contact-form-7 id=\"\" title=\"Contatti\"]",
                                     "_css_classes": "wh-form"}),
                testo("<p><em>Qui va il modulo di Contact Form 7. Crealo in Contatto &gt; Aggiungi "
                      "nuovo, poi incolla il suo shortcode in questo blocco.</em></p>",
                      size=13.5, css="wh-form-note"),
            ], pad=(34, 32, 34, 32), css="wh-card", bg="#fff"),
        ], pad=None, w=57),
    ], pad=(84, 20, 84, 20), row=True, gap=34, align="start")

    return [testata("contattaci"), hero, contatti,
            cta_finale("Il negozio &egrave; fermo adesso?",
                       "Non aspettare la risposta all&rsquo;email: scrivici su WhatsApp e guardiamo subito."),
            footer()]


PAGINE = {
    "index": pagina_index,
    "assistenza": pagina_assistenza,
    "gratis": pagina_gratis,
    "contattaci": pagina_contattaci,
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for nome, fn in PAGINE.items():
        data = fn()
        (OUT / f"{nome}.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        n = json.dumps(data).count('"elType"')
        print(f"scritta {nome}.json  ({n} elementi)")


if __name__ == "__main__":
    main()
