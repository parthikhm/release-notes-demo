<?php

use App\Http\Controllers\UserController;
use Illuminate\Support\Facades\Route;

Route::get('/{id?}', [UserController::class, 'index'])->name('users.index');

Route::post('/users/{id?}', [UserController::class, 'upsert'])->name('users.upsert');

Route::get('/user/delete/{id}', [UserController::class, 'delete'])->name('users.delete');
