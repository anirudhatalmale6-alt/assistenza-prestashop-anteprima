<?php
/**
 * Plugin Name: WebHouse - Pagine Assistenza PrestaShop
 * Description: Crea le 4 pagine del sito di assistenza PrestaShop (Home, Assistenza, Gratis, Contattaci) e le mostra con la grafica dedicata, indipendentemente dal tema attivo. Disattivando il plugin il sito torna esattamente com'era.
 * Version:     1.0.0
 * Author:      Anirudha Talmale
 * Text Domain: webhouse-pagine
 *
 * COME FUNZIONA
 * - All'attivazione crea 4 pagine WordPress (o riusa quelle gia' create da una
 *   attivazione precedente: non duplica mai).
 * - Quando una di quelle pagine viene aperta, il plugin serve direttamente il
 *   suo HTML completo invece del template del tema. Cosi' la grafica e' sempre
 *   la stessa qualunque tema sia attivo, e il tema non ci mette header/footer
 *   suoi sopra e sotto.
 * - I link interni e il CSS vengono riscritti al volo sugli URL veri di WordPress.
 * - Alla disattivazione ripristina l'impostazione della homepage come era prima
 *   e NON cancella nulla. Le pagine restano, in bozza, e si possono eliminare
 *   a mano dal pannello.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'WH_PAGINE_VER', '1.0.0' );
define( 'WH_PAGINE_DIR', plugin_dir_path( __FILE__ ) );
define( 'WH_PAGINE_URL', plugin_dir_url( __FILE__ ) );

/** file HTML => [slug pagina, titolo] */
function wh_pagine_map() {
	return array(
		'index'      => array( 'assistenza-prestashop-home', 'Home' ),
		'assistenza' => array( 'assistenza-prestashop',      'Assistenza PrestaShop' ),
		'gratis'     => array( 'gratis',                     'Gratis' ),
		'contattaci' => array( 'contattaci',                 'Contattaci' ),
	);
}

/* -------------------------------------------------------------- attivazione */

function wh_pagine_activate() {
	$creati = get_option( 'wh_pagine_ids', array() );

	foreach ( wh_pagine_map() as $file => $info ) {
		list( $slug, $titolo ) = $info;

		// Gia' creata da un'attivazione precedente e ancora esistente? riusala.
		if ( ! empty( $creati[ $file ] ) && get_post( $creati[ $file ] ) ) {
			wp_update_post( array( 'ID' => $creati[ $file ], 'post_status' => 'publish' ) );
			continue;
		}

		// Esiste gia' una pagina con quello slug? adottala invece di duplicare.
		$esistente = get_page_by_path( $slug, OBJECT, 'page' );
		if ( $esistente ) {
			$creati[ $file ] = $esistente->ID;
			update_post_meta( $esistente->ID, '_wh_pagina', $file );
			wp_update_post( array( 'ID' => $esistente->ID, 'post_status' => 'publish' ) );
			continue;
		}

		$id = wp_insert_post( array(
			'post_title'   => $titolo,
			'post_name'    => $slug,
			'post_status'  => 'publish',
			'post_type'    => 'page',
			'post_content' => 'Questa pagina viene generata dal plugin "WebHouse - Pagine Assistenza PrestaShop".',
		) );

		if ( $id && ! is_wp_error( $id ) ) {
			update_post_meta( $id, '_wh_pagina', $file );
			$creati[ $file ] = $id;
		}
	}

	update_option( 'wh_pagine_ids', $creati );

	// Homepage: la imposto sulla nostra Home, ma salvo prima com'era,
	// cosi' alla disattivazione posso rimettere tutto a posto.
	if ( ! empty( $creati['index'] ) && get_option( 'wh_pagine_front_backup' ) === false ) {
		update_option( 'wh_pagine_front_backup', array(
			'show_on_front' => get_option( 'show_on_front' ),
			'page_on_front' => get_option( 'page_on_front' ),
		) );
		update_option( 'show_on_front', 'page' );
		update_option( 'page_on_front', (int) $creati['index'] );
	}

	flush_rewrite_rules();
}
register_activation_hook( __FILE__, 'wh_pagine_activate' );

/* ----------------------------------------------------------- disattivazione */

function wh_pagine_deactivate() {
	// rimetti la homepage come l'ho trovata
	$bk = get_option( 'wh_pagine_front_backup' );
	if ( is_array( $bk ) ) {
		update_option( 'show_on_front', $bk['show_on_front'] );
		update_option( 'page_on_front', $bk['page_on_front'] );
		delete_option( 'wh_pagine_front_backup' );
	}

	// le pagine non le cancello: le metto in bozza, cosi' spariscono dal sito
	// ma nulla va perso.
	foreach ( (array) get_option( 'wh_pagine_ids', array() ) as $id ) {
		if ( get_post( $id ) ) {
			wp_update_post( array( 'ID' => $id, 'post_status' => 'draft' ) );
		}
	}

	flush_rewrite_rules();
}
register_deactivation_hook( __FILE__, 'wh_pagine_deactivate' );

/* --------------------------------------------------------------- rendering */

/** quale file HTML corrisponde alla pagina richiesta (o null) */
function wh_pagine_file_corrente() {
	if ( ! is_page() ) {
		return null;
	}
	$id   = get_queried_object_id();
	$file = get_post_meta( $id, '_wh_pagina', true );

	return ( $file && array_key_exists( $file, wh_pagine_map() ) ) ? $file : null;
}

/** riscrive link interni e CSS sugli URL veri di WordPress */
function wh_pagine_riscrivi( $html ) {
	$html = str_replace( 'href="assets/style.css"',
		'href="' . esc_url( WH_PAGINE_URL . 'assets/style.css?v=' . WH_PAGINE_VER ) . '"', $html );

	foreach ( wh_pagine_map() as $file => $info ) {
		$id  = 0;
		$ids = get_option( 'wh_pagine_ids', array() );
		if ( ! empty( $ids[ $file ] ) ) {
			$id = (int) $ids[ $file ];
		}
		$url = $id ? get_permalink( $id ) : home_url( '/' );
		$html = str_replace( 'href="' . $file . '.html"', 'href="' . esc_url( $url ) . '"', $html );
	}

	return $html;
}

function wh_pagine_render( $template ) {
	$file = wh_pagine_file_corrente();
	if ( ! $file ) {
		return $template;
	}

	$path = WH_PAGINE_DIR . 'pagine/' . $file . '.html';
	if ( ! file_exists( $path ) ) {
		return $template; // manca il file: lascia fare al tema, niente pagina bianca
	}

	$html = file_get_contents( $path );
	if ( false === $html ) {
		return $template;
	}

	status_header( 200 );
	if ( ! headers_sent() ) {
		header( 'Content-Type: text/html; charset=UTF-8' );
	}
	echo wh_pagine_riscrivi( $html ); // phpcs:ignore WordPress.Security.EscapeOutput
	exit;
}
add_filter( 'template_include', 'wh_pagine_render', 99 );

/* ------------------------------------------------------- avviso nel pannello */

function wh_pagine_avviso() {
	if ( ! current_user_can( 'manage_options' ) ) {
		return;
	}
	$screen = get_current_screen();
	if ( ! $screen || 'plugins' !== $screen->id ) {
		return;
	}
	$ids = get_option( 'wh_pagine_ids', array() );
	if ( empty( $ids ) ) {
		return;
	}

	echo '<div class="notice notice-success"><p><b>Pagine WebHouse attive:</b> ';
	$link = array();
	foreach ( wh_pagine_map() as $file => $info ) {
		if ( ! empty( $ids[ $file ] ) ) {
			$link[] = '<a href="' . esc_url( get_permalink( $ids[ $file ] ) ) . '" target="_blank">'
				. esc_html( $info[1] ) . '</a>';
		}
	}
	echo wp_kses_post( implode( ' &middot; ', $link ) );
	echo '</p></div>';
}
add_action( 'admin_notices', 'wh_pagine_avviso' );
