<?php

define('ABSPATH', '/var/www/');
define('WP_CORE_UPDATE', false);
define('WP_ALLOW_MULTISITE', true);
define('DB_NAME', 'docker');
define('DB_USER', 'root');
define('DB_PASSWORD', getenv('DB_PASSWORD'));
define('DB_HOST', getenv('DB_HOSTNAME') . ':' . getenv('DB_PORT'));

if (!isset($table_prefix)) {
    $table_prefix = 'wp_';
}

require_once(ABSPATH . 'wp-settings.php');

?>
