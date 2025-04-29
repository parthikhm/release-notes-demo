<?php

use App\Http\Controllers\UserController;
use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('welcome');
});

Route::post('/index', [UserController::class, 'index'])->name('index');

Route::get('/index/{id}', [UserController::class, 'show'])->name('show');

Route::get('/home', [UserController::class, 'home'])->name('home');
