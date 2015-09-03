<?php

// web/index.php
require_once __DIR__.'/../vendor/autoload.php';
use Symfony\Component\HttpFoundation\Request;

$app = new Silex\Application();

$app->register(new Silex\Provider\TwigServiceProvider(), array(
    'twig.path' => __DIR__.'/../views',
));

$app->register(new Silex\Provider\UrlGeneratorServiceProvider());

$app->get('/', function () use ($app) {
    return $app['twig']->render('index.twig', array(
        'name' => "Gemini",
        'build' => parse_ini_file(__DIR__ . '/../build.ini')
    ));
})->bind('home');

$app->get('/development/', function () use ($app) {
    return $app['twig']->render('index.twig', array(
        'name' => "Gemini",
        'build' => parse_ini_file(__DIR__ . '/../build.ini')
    ));
});

$app->get('/install/script', function () use ($app) {
    return $app['twig']->render('deploy.sh.twig', array(
        'name' => "Gemini",
        'build' => parse_ini_file(__DIR__ . '/../build.ini')
    ));
})->bind('install-script');

$app->post('/deploy/yaml', function (Request $request) use ($app) {
    return $app['twig']->render('deploy.yaml.twig', array(
        'name' => "Gemini",
        'build' => parse_ini_file(__DIR__ . '/../build.ini'),
        'config' => array(
            'host' => $request->get('HOSTIP'),
            'onprem' => $request->get('ONPREM'),
            'theme' => $request->get('THEME')
        )
    ));
})->bind('deploy-yaml');

$app->run();