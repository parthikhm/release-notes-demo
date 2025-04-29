<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Laravel Livewire Modal</title>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.5/dist/css/bootstrap.min.css" rel="stylesheet"
        integrity="sha384-SgOJa3DmI69IUzQ2PVdRZhwQ+dy64/BUtbMJw1MZ8t5HZApcHrRKUc4W0kG879m7" crossorigin="anonymous">
    @livewireStyles
</head>

<body>
    <div class="container mt-5">
        <!-- Button to trigger Form modal -->
        <button type="button" class="btn btn-primary" wire:click="$emit('openModal', 'form')" data-bs-toggle="modal"
            data-bs-target="#liveModal">
            Launch Form Modal
        </button>

        <!-- Button to trigger Table modal -->
        <button type="button" class="btn btn-primary" wire:click="$emit('openModal', 'table')" data-bs-toggle="modal"
            data-bs-target="#liveModal">
            Launch Table Modal
        </button>

        <div class="modal fade" id="liveModal" tabindex="-1" aria-labelledby="liveModalLabel" aria-hidden="true"
            wire:ignore.self>
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="liveModalLabel">Livewire Modal</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <input type="text" class="form-control" placeholder="Enter your name" wire:model="name">
                        <input type="email" class="form-control mt-2" placeholder="Enter your email"
                            wire:model="email">
                        <input type="text" class="form-control mt-2" placeholder="Enter your phone number"
                            wire:model="phone">
                        <input type="text" class="form-control mt-2" placeholder="Enter your address"
                            wire:model="address">
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.5/dist/js/bootstrap.bundle.min.js"
        integrity="sha384-k6d4wzSIapyDyv1kpU366/PK5hCdSbCRGRCMv+eplOQJWyd1fbcAu9OCUj5zNLiq" crossorigin="anonymous">
    </script>

    @livewireScripts
</body>

</html>
