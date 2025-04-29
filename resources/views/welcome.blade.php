<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>User Registration Form</title>

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.5/dist/css/bootstrap.min.css" rel="stylesheet"
        integrity="sha384-SgOJa3DmI69IUzQ2PVdRZhwQ+dy64/BUtbMJw1MZ8t5HZApcHrRKUc4W0kG879m7" crossorigin="anonymous">

    <!-- Material Icons -->
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">

    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap"
        rel="stylesheet">

    <!-- Custom CSS -->
    <style>
        :root {
            --primary-color: #4361ee;
            --secondary-color: #3f37c9;
            --accent-color: #4895ef;
            --success-color: #4cc9f0;
            --warning-color: #f72585;
            --light-color: #f8f9fa;
            --dark-color: #212529;
            --gray-color: #6c757d;
        }

        body {
            font-family: 'Poppins', sans-serif;
            background-color: #f5f7fa;
            color: #333;
        }

        .card {
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
            border: none;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            margin-bottom: 20px;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        }

        .card-header {
            background-color: var(--primary-color);
            color: white;
            border-radius: 15px 15px 0 0 !important;
            padding: 1.2rem;
            font-weight: 600;
        }

        .btn-primary {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
            border-radius: 8px;
            padding: 0.6rem 1.5rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }

        .btn-primary:hover {
            background-color: var(--secondary-color);
            border-color: var(--secondary-color);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(67, 97, 238, 0.3);
        }

        .btn-danger {
            background-color: var(--warning-color);
            border-color: var(--warning-color);
            border-radius: 8px;
            padding: 0.6rem 1.5rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }

        .btn-danger:hover {
            background-color: #d90429;
            border-color: #d90429;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(247, 37, 133, 0.3);
        }

        .btn-warning {
            background-color: var(--accent-color);
            border-color: var(--accent-color);
            color: white;
            border-radius: 8px;
            padding: 0.6rem 1.5rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }

        .btn-warning:hover {
            background-color: #3a7bd5;
            border-color: #3a7bd5;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(72, 149, 239, 0.3);
        }

        .form-control {
            border-radius: 8px;
            padding: 0.75rem 1rem;
            border: 1px solid #e0e0e0;
            transition: all 0.3s ease;
        }

        .form-control:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 0.25rem rgba(67, 97, 238, 0.25);
        }

        .form-label {
            font-weight: 500;
            margin-bottom: 0.5rem;
            color: #555;
        }

        .table {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
        }

        .table thead {
            background-color: var(--primary-color);
            color: white;
        }

        .table thead th {
            font-weight: 500;
            border: none;
            padding: 1rem;
        }

        .table tbody td {
            padding: 1rem;
            vertical-align: middle;
        }

        .alert {
            border-radius: 10px;
            border: none;
            padding: 1rem 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
        }

        .alert-success {
            background-color: #d1fae5;
            color: #065f46;
        }

        .pagination {
            margin-top: 2rem;
        }

        .page-link {
            color: var(--primary-color);
            border-radius: 8px;
            margin: 0 5px;
            border: none;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
        }

        .page-link:hover {
            background-color: var(--primary-color);
            color: white;
            transform: translateY(-2px);
        }

        .page-item.active .page-link {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
        }

        .action-buttons {
            display: flex;
            gap: 0.5rem;
        }

        .main-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }

        .section-title {
            color: var(--primary-color);
            font-weight: 600;
            margin-bottom: 1.5rem;
            position: relative;
            padding-bottom: 0.5rem;
        }

        .section-title::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 50px;
            height: 3px;
            background-color: var(--primary-color);
        }

        .form-card {
            margin-bottom: 2rem;
        }

        .table-card {
            margin-top: 2rem;
        }

        .card-body {
            padding: 1.5rem;
        }

        .material-icons {
            vertical-align: middle;
            margin-right: 5px;
        }

        .btn-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }

        .btn-icon .material-icons {
            margin-right: 5px;
        }

        @media (max-width: 768px) {
            .action-buttons {
                flex-direction: column;
            }

            .btn {
                width: 100%;
                margin-bottom: 0.5rem;
            }

            .main-container {
                padding: 1rem;
            }

            .card-header {
                padding: 1rem;
            }

            .card-body {
                padding: 1rem;
            }

            .table-responsive {
                margin-bottom: 1rem;
            }
        }

        @media (max-width: 576px) {
            .main-container {
                padding: 0.5rem;
            }

            .section-title {
                font-size: 1.5rem;
            }

            .card-header {
                font-size: 1rem;
            }

            .form-label {
                font-size: 0.9rem;
            }

            .table thead th {
                padding: 0.75rem;
                font-size: 0.9rem;
            }

            .table tbody td {
                padding: 0.75rem;
                font-size: 0.9rem;
            }
        }
    </style>
</head>

<body>
    <div class="main-container">
        <h1 class="section-title mb-4">User Management System</h1>

        @if (session('success'))
            <div id="success-alert" class="alert alert-success">
                <span class="material-icons">check_circle</span> {{ session('success') }}
            </div>
        @endif

        <div class="row">
            <div class="col-lg-5">
                <div class="card form-card">
                    <div class="card-header">
                        <span class="material-icons">person_add</span>
                        {{ isset($editUser) ? 'Edit User' : 'Add New User' }}
                    </div>
                    <div class="card-body">
                        <form method="POST" action="{{ route('users.upsert') }}">
                            @csrf

                            @if (isset($editUser))
                                <input type="hidden" name="id" value="{{ $editUser->id }}">
                            @endif

                            <div class="mb-3">
                                <label for="name" class="form-label">Name</label>
                                <div class="input-group">
                                    <span class="input-group-text"><span class="material-icons">person</span></span>
                                    <input type="text" class="form-control" id="name" name="name"
                                        value="{{ $editUser->name ?? '' }}" required placeholder="Enter full name">
                                </div>
                            </div>

                            <div class="mb-4">
                                <label for="email" class="form-label">Email</label>
                                <div class="input-group">
                                    <span class="input-group-text"><span class="material-icons">email</span></span>
                                    <input type="email" class="form-control" id="email" name="email"
                                        value="{{ $editUser->email ?? '' }}" required placeholder="Enter email address">
                                </div>
                            </div>

                            <div class="d-grid">
                                <button type="submit" class="btn btn-primary btn-icon">
                                    <span class="material-icons">{{ isset($editUser) ? 'update' : 'add' }}</span>
                                    {{ isset($editUser) ? 'Update User' : 'Add User' }}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>

            <div class="col-lg-7">
                <div class="card table-card">
                    <div class="card-header">
                        <span class="material-icons">people</span> User List
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table id="users-table" class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Email</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    @foreach ($users as $user)
                                        <tr>
                                            <td>{{ $user->name }}</td>
                                            <td>{{ $user->email }}</td>
                                            <td>
                                                <div class="action-buttons">
                                                    <form method="GET"
                                                        action="{{ route('users.index', $user->id) }}">
                                                        <button type="submit" class="btn btn-warning btn-icon">
                                                            <span class="material-icons">edit</span> Edit
                                                        </button>
                                                    </form>

                                                    <form method="GET"
                                                        action="{{ route('users.delete', $user->id) }}">
                                                        @csrf
                                                        @method('DELETE')
                                                        <button type="submit" class="btn btn-danger btn-icon">
                                                            <span class="material-icons">delete</span> Delete
                                                        </button>
                                                    </form>
                                                </div>
                                            </td>
                                        </tr>
                                    @endforeach
                                </tbody>
                            </table>
                        </div>

                        <div class="d-flex justify-content-center mt-4">
                            {{ $users->links() }}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.5/dist/js/bootstrap.bundle.min.js"
        integrity="sha384-k6d4wzSIapyDyv1kpU366/PK5hCdSbCRGRCMv+eplOQJWyd1fbcAu9OCUj5zNLiq" crossorigin="anonymous">
    </script>

    <!-- Custom JS -->
    <script>
        // Auto-hide success alert after 5 seconds
        setTimeout(function() {
            let alert = document.getElementById('success-alert');
            if (alert) {
                alert.style.display = 'none';
            }
        }, 5000);
    </script>
</body>

</html>
