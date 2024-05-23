import streamlit as st
from streamlit_extras.bottom_container import bottom as st_bottom_bar
# from streamlit_scrollable_textbox import scrollableTextbox as st_textbox  # noqa


def _get_session() -> dict:
    if __name__ not in st.session_state:
        st.session_state[__name__] = {
            'last_command': '',
            'logger'      : Logger()
        }
    return st.session_state[__name__]


def main(expand: bool = False) -> None:
    with st_bottom_bar():
        with st.expander('Bottom bar', expand):
            tabs = st.tabs(('Log output', 'Command panel'))
            with tabs[0]:
                with st.container(height=150):
                    _add_output_panel()
            with tabs[1]:
                with st.container(height=150):
                    _add_command_panel()


def _add_output_panel() -> None:
    logger: Logger = _get_session()['logger']
    logger.init_widget()
    # _get_session()['logger'].set_widget(
    #     st.text_area(
    #         'Log',
    #         placeholder='The log of insallation will be shown here.',
    #         label_visibility=False
    #     )
    # )


def _add_command_panel() -> None:
    session = _get_session()
    rows = (st.container(), st.container())
    with rows[1]:
        if st.checkbox('Remember last input', True):
            value = session['last_command'] or None
        else:
            value = None
    with rows[0]:
        code = st.text_area(
            'Command here',
            value=value,
            placeholder=(
                session['last_command'] or
                'The command will be executed in the background.'
            ),
            label_visibility='collapsed',
        )
        if code:
            exec(code, globals())
            session['last_command'] = code


# -----------------------------------------------------------------------------

class Logger:
    _messages: list
    _refreshable_zone: st.empty = None
    
    def __init__(self) -> None:
        self._messages = []
    
    def init_widget(self) -> None:
        if self._refreshable_zone is None:
            # with st.container(height=120):
            #     self._refreshable_zone = st.empty()
            #     self._refreshable_zone.code(
            #         'The log of installation info will be shown here.'
            #     )
            self._refreshable_zone = st.empty()
            self._refreshable_zone.code(
                'The log of installation info will be shown here.'
            )
    
    def __call__(self, new_msg: str) -> None:
        # TODO: how to scroll to the bottom line?
        self._messages.append(new_msg)
        # with self._refreshable_zone:
        #     st_textbox('\n'.join(self._messages))
        self._refreshable_zone.code('\n'.join(self._messages))
        # self._refreshable_zone.html(
        #     '\n'.join(self._messages), height=100, scrolling=True,
        # )
    
    # @property
    # def all_messages(self) -> str:
    #     return '\n'.join(self._messages)
    
    def clear(self) -> None:
        """ clear previous messages. """
        self._messages.clear()


def get_logger() -> Logger:
    return _get_session()['logger']
