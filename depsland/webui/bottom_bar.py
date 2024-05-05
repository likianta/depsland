import streamlit as st
from streamlit_extras.bottom_container import bottom as st_bottom_bar


def _get_session() -> dict:
    if __name__ not in st.session_state:
        st.session_state[__name__] = {
            'last_command': '',
            'logger'      : Logger()
        }
    return st.session_state[__name__]


class Logger:
    _messages: list = []
    _widget: st.empty = None
    
    def set_widget(self, widget: st.empty) -> None:
        self._widget = widget
    
    def __bool__(self) -> bool:
        return bool(self._widget)
    
    def __call__(self, new_msg: str) -> None:
        self._messages.append(new_msg)
        self._widget.code('\n'.join(self._messages))
    
    @property
    def all_message(self) -> str:
        return '\n'.join(self._messages)
    
    def clear(self) -> None:
        self._messages.clear()


def get_logger() -> Logger:
    return _get_session()['logger']


def main(expand: bool = False) -> None:
    with st_bottom_bar():
        with st.expander('Bottom bar', expand):
            tabs = st.tabs(('Log output', 'Command panel'))
            with tabs[0]:
                _add_output_panel()
            with tabs[1]:
                _add_command_panel()


def _add_output_panel() -> None:
    with st.container(height=100):
        logger: Logger = _get_session()['logger']
        if logger:
            logger.set_widget(x := st.empty())
            x.code(logger.all_message)
            logger.clear()
        else:
            logger.set_widget(st.empty())
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
        )
        if code:
            exec(code, globals())
            session['last_command'] = code
