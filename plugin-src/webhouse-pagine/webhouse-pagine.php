<?php
/**
 * Plugin Name: WebHouse - Pagine Assistenza PrestaShop
 * Description: Crea le 4 pagine (Home, Assistenza PrestaShop, Gratis, Contattaci) come vere pagine Elementor, modificabili dall'editor e gestibili con Yoast. Disattivandolo il sito torna com'era.
 * Version:     2.1.0
 * Author:      Anirudha Talmale
 * Text Domain: webhouse-pagine
 *
 * COSA FA
 * - All'attivazione crea 4 pagine WordPress e ci mette dentro il contenuto
 *   Elementor vero (_elementor_data). Ogni titolo, testo e bottone si modifica
 *   aprendo la pagina con "Modifica con Elementor".
 * - Le pagine usano il template Canvas di Elementor: niente header/footer del
 *   tema sopra e sotto, la grafica e' quella del progetto.
 * - Yoast funziona normalmente: titolo, descrizione, canonical, Open Graph,
 *   schema e analisi del contenuto.
 * - Alla disattivazione rimette la homepage come l'ha trovata e mette le
 *   pagine in bozza. Non cancella niente.
 *
 * NOTA sui link interni: nei dati Elementor i collegamenti fra le 4 pagine
 * sono scritti come {{index}}, {{assistenza}}... e vengono sostituiti con i
 * permalink veri al momento dell'attivazione. Cosi' i menu funzionano
 * qualunque sia il dominio o la struttura dei permalink.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'WH_PAGINE_VER', '2.1.0' );
define( 'WH_PAGINE_DIR', plugin_dir_path( __FILE__ ) );
define( 'WH_PAGINE_URL', plugin_dir_url( __FILE__ ) );

/** file json => [slug, titolo] */
function wh_pagine_map() {
	return array(
		'index'      => array( 'assistenza-prestashop-home', 'Home' ),
		'assistenza' => array( 'assistenza-prestashop',      'Assistenza PrestaShop' ),
		'gratis'     => array( 'gratis',                     'Gratis' ),
		'contattaci' => array( 'contattaci',                 'Contattaci' ),
	);
}

/* ------------------------------------------------------------- attivazione */

function wh_pagine_activate() {
	$ids = get_option( 'wh_pagine_ids', array() );

	// 1) prima le pagine devono esistere tutte, perche' i link interni di una
	//    puntano alle altre e mi servono i permalink definitivi.
	foreach ( wh_pagine_map() as $file => $info ) {
		list( $slug, $titolo ) = $info;

		if ( ! empty( $ids[ $file ] ) && get_post( $ids[ $file ] ) ) {
			wp_update_post( array( 'ID' => $ids[ $file ], 'post_status' => 'publish' ) );
			continue;
		}

		$esistente = get_page_by_path( $slug, OBJECT, 'page' );
		if ( $esistente ) {
			$ids[ $file ] = $esistente->ID;
			wp_update_post( array( 'ID' => $esistente->ID, 'post_status' => 'publish' ) );
			continue;
		}

		$id = wp_insert_post( array(
			'post_title'  => $titolo,
			'post_name'   => $slug,
			'post_status' => 'publish',
			'post_type'   => 'page',
		) );
		if ( $id && ! is_wp_error( $id ) ) {
			$ids[ $file ] = $id;
		}
	}
	update_option( 'wh_pagine_ids', $ids );

	// 2) ora il contenuto Elementor, con i link risolti
	foreach ( wh_pagine_map() as $file => $info ) {
		if ( empty( $ids[ $file ] ) ) {
			continue;
		}
		wh_pagine_scrivi_elementor( (int) $ids[ $file ], $file, $ids );
	}

	// 3) homepage, salvando com'era per poterla rimettere
	if ( ! empty( $ids['index'] ) && false === get_option( 'wh_pagine_front_backup' ) ) {
		update_option( 'wh_pagine_front_backup', array(
			'show_on_front' => get_option( 'show_on_front' ),
			'page_on_front' => get_option( 'page_on_front' ),
		) );
		update_option( 'show_on_front', 'page' );
		update_option( 'page_on_front', (int) $ids['index'] );
	}

	wh_pagine_svuota_cache_elementor();
	flush_rewrite_rules();
}
register_activation_hook( __FILE__, 'wh_pagine_activate' );

/**
 * Mette il contenuto Elementor dentro una pagina.
 *
 * Il json viene riscritto ogni volta che si attiva il plugin: se aggiorno le
 * pagine e il cliente riattiva, si allinea. Le sue modifiche fatte in Elementor
 * verrebbero sovrascritte, per questo la riscrittura avviene SOLO
 * all'attivazione e mai a ogni caricamento.
 */
function wh_pagine_scrivi_elementor( $post_id, $file, $ids ) {
	$path = WH_PAGINE_DIR . 'elementor/' . $file . '.json';
	if ( ! file_exists( $path ) ) {
		return;
	}
	$json = file_get_contents( $path );
	if ( false === $json ) {
		return;
	}

	// {{slug}} => permalink vero
	foreach ( wh_pagine_map() as $f => $info ) {
		$url  = ! empty( $ids[ $f ] ) ? get_permalink( (int) $ids[ $f ] ) : home_url( '/' );
		$json = str_replace( '{{' . $f . '}}', esc_url_raw( $url ), $json );
	}

	update_post_meta( $post_id, '_elementor_data', wp_slash( $json ) );
	update_post_meta( $post_id, '_elementor_edit_mode', 'builder' );
	update_post_meta( $post_id, '_elementor_template_type', 'wp-page' );
	update_post_meta( $post_id, '_elementor_version', defined( 'ELEMENTOR_VERSION' ) ? ELEMENTOR_VERSION : '3.0.0' );
	update_post_meta( $post_id, '_wp_page_template', 'elementor_canvas' );
}

/** Elementor tiene un css per pagina: dopo aver riscritto i dati va rigenerato */
function wh_pagine_svuota_cache_elementor() {
	if ( class_exists( '\\Elementor\\Plugin' ) ) {
		\Elementor\Plugin::instance()->files_manager->clear_cache();
	}
}

/* ---------------------------------------------------------- disattivazione */

function wh_pagine_deactivate() {
	$bk = get_option( 'wh_pagine_front_backup' );
	if ( is_array( $bk ) ) {
		update_option( 'show_on_front', $bk['show_on_front'] );
		update_option( 'page_on_front', $bk['page_on_front'] );
		delete_option( 'wh_pagine_front_backup' );
	}

	// in bozza, non cancellate: il lavoro resta recuperabile
	foreach ( (array) get_option( 'wh_pagine_ids', array() ) as $id ) {
		if ( get_post( $id ) ) {
			wp_update_post( array( 'ID' => $id, 'post_status' => 'draft' ) );
		}
	}

	flush_rewrite_rules();
}
register_deactivation_hook( __FILE__, 'wh_pagine_deactivate' );

/* -------------------------------------------------------------- front-end */

/** true se la pagina aperta e' una delle nostre */
function wh_pagine_nostra() {
	if ( ! is_page() ) {
		return false;
	}
	$ids = (array) get_option( 'wh_pagine_ids', array() );
	return in_array( (int) get_queried_object_id(), array_map( 'intval', $ids ), true );
}

/**
 * Un solo <title>.
 *
 * Il template Canvas di Elementor (canvas.php) stampa un <title> suo, ma solo
 * "se il tema non dichiara title-tag". Con un tema che non lo dichiara si
 * finisce con DUE <title>: quello del Canvas e quello di Yoast. Per Google
 * sono un errore.
 *
 * La soluzione e' dichiarare title-tag: il Canvas allora salta il suo, e il
 * titolo resta uno solo, quello che il cliente modifica da Yoast (o, se non
 * ci fosse un plugin SEO, quello del core di WordPress).
 *
 * ATTENZIONE: title-tag va dichiarato PRIMA di wp_loaded. Su template_redirect
 * WordPress risponde con una notice "called incorrectly" che, se il sito ha il
 * debug a schermo, viene stampata in cima alla pagina e rompe l'<head>.
 * Quindi si dichiara qui, su after_setup_theme. E' una capacita' standard che
 * quasi tutti i temi moderni dichiarano gia': se il tema la dichiara di suo,
 * questa riga non cambia nulla.
 */
function wh_pagine_un_solo_title() {
	add_theme_support( 'title-tag' );
}
add_action( 'after_setup_theme', 'wh_pagine_un_solo_title', 20 );

/**
 * Seconda meta' della stessa cosa.
 *
 * Dichiarando title-tag il Canvas smette di stampare il suo <title>, ma in
 * cambio si attiva quello del core (_wp_render_title_tag). Se c'e' un plugin
 * SEO ne scrive uno anche lui: torniamo a due. Quindi, quando un plugin SEO
 * e' attivo, il titolo del core lo tolgo e lascio il suo - che e' quello
 * modificabile dal cliente.
 */
function wh_pagine_titolo_al_seo() {
	if ( ! wh_pagine_nostra() ) {
		return;
	}
	$seo = defined( 'WPSEO_VERSION' )        // Yoast
		|| defined( 'RANK_MATH_VERSION' )    // Rank Math
		|| defined( 'SEOPRESS_VERSION' )     // SEOPress
		|| defined( 'AIOSEO_VERSION' );      // All in One SEO
	if ( $seo ) {
		// Due renderer diversi a seconda del tipo di tema, e vanno tolti
		// entrambi: i temi classici usano _wp_render_title_tag, quelli a
		// blocchi (Twenty Twenty-Four/Five e simili) _block_template_render_title_tag.
		// Togliendo solo il primo, su un tema a blocchi il doppio <title> resta.
		remove_action( 'wp_head', '_wp_render_title_tag', 1 );
		remove_action( 'wp_head', '_block_template_render_title_tag', 1 );
	}
}
add_action( 'wp_head', 'wh_pagine_titolo_al_seo', 0 );

/** il foglio di stile con le rifiniture (testata, card, chip, liste) */
function wh_pagine_assets() {
	if ( ! wh_pagine_nostra() ) {
		return;
	}
	wp_enqueue_style( 'wh-pagine', WH_PAGINE_URL . 'assets/elementor.css', array(), WH_PAGINE_VER );
}
add_action( 'wp_enqueue_scripts', 'wh_pagine_assets', 20 );

/** il menu mobile della testata */
function wh_pagine_js() {
	if ( ! wh_pagine_nostra() ) {
		return;
	}
	?>
	<script>
	(function(){
		var b=document.getElementById('wh-burger'), n=document.getElementById('wh-nav');
		if(!b||!n) return;
		b.addEventListener('click',function(){ n.classList.toggle('is-open'); });
		n.addEventListener('click',function(e){
			if(e.target.tagName==='A'){ n.classList.remove('is-open'); }
		});
	})();
	</script>
	<?php
}
add_action( 'wp_footer', 'wh_pagine_js', 20 );

/* ---------------------------------------------------------------- pannello */

function wh_pagine_avviso() {
	$screen = get_current_screen();
	if ( ! $screen || 'plugins' !== $screen->id || ! current_user_can( 'manage_options' ) ) {
		return;
	}
	$ids = get_option( 'wh_pagine_ids', array() );
	if ( empty( $ids ) ) {
		return;
	}

	$link = array();
	foreach ( wh_pagine_map() as $file => $info ) {
		if ( ! empty( $ids[ $file ] ) ) {
			$link[] = '<a href="' . esc_url( get_permalink( $ids[ $file ] ) ) . '" target="_blank">'
				. esc_html( $info[1] ) . '</a>';
		}
	}

	echo '<div class="notice notice-success"><p><b>Pagine WebHouse:</b> '
		. wp_kses_post( implode( ' &middot; ', $link ) )
		. '<br>Per modificarle: Pagine &rarr; apri la pagina &rarr; <b>Modifica con Elementor</b>. '
		. 'Il SEO si imposta dal riquadro Yoast sotto ogni pagina.</p></div>';
}
add_action( 'admin_notices', 'wh_pagine_avviso' );

/** se Elementor non c'e', dillo invece di lasciare pagine vuote */
function wh_pagine_serve_elementor() {
	if ( defined( 'ELEMENTOR_VERSION' ) ) {
		return;
	}
	$screen = get_current_screen();
	if ( ! $screen || 'plugins' !== $screen->id ) {
		return;
	}
	echo '<div class="notice notice-error"><p><b>WebHouse:</b> serve il plugin Elementor '
		. 'attivo, altrimenti le 4 pagine restano vuote.</p></div>';
}
add_action( 'admin_notices', 'wh_pagine_serve_elementor' );
