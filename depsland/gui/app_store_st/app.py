import airmise as air
import streamlit as st
import streamlit_canary as sc
from argsense import cli

@sc.init_state
class State:
    air_connected: bool

@cli
def main(host='localhost', port=2187):
    st.set_page_config('Depsland AppStore')
    st.title('Depsland AppStore')
    
    if not State.air_connected:
        air.connect(host, port)
        State.air_connected = True

def _fetch_applist():
    ...

if __name__ == '__main__':
    cli.run(main)
