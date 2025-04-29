<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class UserController extends Controller
{
    public function index(Request $request)
    {
        // Handle the request to show the index page
        return view('index');
    }

    public function home(Request $request)
    {
        // Handle the request to show the index page
        return view('home');
    }
}
