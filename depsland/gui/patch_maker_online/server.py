import airmise as air


def listen_for_clients() -> None:
    air.Server().run(
        {'register_client': _register_client}, host='localhost', port=2192
    )


def _register_client(
    client_ip: str, client_port: int, client_name: str
) -> None:
    print(
        """
        Here is coming a new client:
            {NAME}@{IP}:{PORT}
        As server side, we can open the channel by following url:
            http://localhost:2190/?ip={IP}&port={PORT}
        See also `./remote_client.py:init_air_client:st.query_params`.
        """.format(NAME=client_name, IP=client_ip, PORT=client_port)
    )


if __name__ == '__main__':
    # launch server:
    #   python depsland/gui/patch_maker_online/server.py
    # or by depsland:
    #   python -m depsland patch_maker_server
    # expose service to public (optional):
    #   bore local -s <secret> -t 47.102.108.149 -p 2190 2190
    listen_for_clients()
