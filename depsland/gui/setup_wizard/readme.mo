
[## Note]

[
    - [`pox ...] is alias to [`poetry run python ...]
    - [`strun ...] is alias to [`poetry run -- streamlit run --browser.gatherUsageStats false --runner.magicEnabled false --server.headless true --server.port ...]
]

[## Demo Run]

[
    = Start server for client support
        [$sh
            pox depsland/gui/setup_wizard/depsland_installer_client_support.py start-server
        ]
        It will run at [port=2186].
    = Start a demo client
        [$sh
            # (open a new terminal tab)
            pox depsland/gui/setup_wizard/depsland_installer_client_support.py start-client localhost
        ]
        In the console, we will get a "public port" printed. Use it in the next step.
    = Start GUI with debug arguments.
        [$sh
            strun 3001 depsland/gui/setup_wizard/depsland_installer_online.py -- --debug --client-public-host localhost --client-public-port <public_port_from_last_step> --target-appid hello_world_tkinter --target-version 0.5.0
        ]
]

[## Production Run]

...
