<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;

class UserController extends Controller
{
    public function index($id = null)
    {
        $users = User::paginate(5);
        $editUser = null;

        if ($id) {
            $editUser = User::findOrFail($id);
        }

        return view('welcome', compact('users', 'editUser'));
    }


    public function upsert(Request $request)
    {
        $request->validate([
            'name' => 'required',
            'email' => 'required|email',
        ]);

        $hashedPassword = Hash::make('default_password');

        for ($index = 0; $index < 15; $index++) {
            User::upsert([
                [
                    'name' => $request->name,
                    'email' => $request->email,
                    'password' => $hashedPassword,
                ]
            ], ['email'], ['name', 'password']);
        }

        return redirect()->route('users.index')->with('success', 'User inserted or updated successfully!');
    }

    public function delete($id)
    {
        $user = User::findOrFail($id);
        $user->delete();

        return redirect()->route('users.index')->with('success', 'User deleted successfully!');
    }
}
