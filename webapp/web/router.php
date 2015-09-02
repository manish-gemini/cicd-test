<?php

$path = __DIR__ . $_SERVER["REQUEST_URI"];
if (file_exists($path) && !is_dir($path)) {
    return false;
} else {
    require "index.php";
}
