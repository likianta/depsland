import os
import typing as t
import winreg
from textwrap import dedent

from lambda_ex import grafting
from lk_utils import dumps
from lk_utils import fs
from lk_utils import run_cmd_args
from qmlease import AutoProp
from qmlease import QObject
from qmlease import app
from qmlease import signal
from qmlease import slot


class SetupWizard(QObject):
    all_finished = AutoProp(False, bool)
    nav: 'Navigation'
    navigation_ready = signal()
    page_changed = signal(int)
    
    # def __init__(self):
    #     super().__init__()
    #     self.all_finished_changed.connect(lambda _: self._wind_up)
    
    @slot(object, object)
    def init_navigation(self, prev: QObject, next_: QObject) -> None:
        self.nav = Navigation(prev, next_)
        
        @grafting(self.nav.page_changed.connect)
        def _(page: int, _: bool) -> None:
            self.page_changed.emit(page)
        
        self.navigation_ready.emit()
    
    def wind_up(self, dir_o: str) -> None:
        print('create executables')
        
        # to %DEPSLAND% root
        file_i = f'{dir_o}/build/exe/depsland.exe'
        file_o = f'{dir_o}/depsland.exe'
        fs.move(file_i, file_o, True)
        
        # to desktop
        file_i = f'{dir_o}/desktop.exe'
        file_o = fs.normpath('{}/Desktop/Depsland.lnk'
                             .format(os.environ['USERPROFILE']))
        self._create_desktop_shortcut(file_i, file_o)
        
        # add `DEPSLAND` to environment variables
        self._set_environment_variables(dir_o, level='user')
        #   do not use `level='system'` here, it is not worked.
        #   FIXME: we've found a failed case if user launches terminal as admin
        #       by default -- the error shows `depsland command not found`,
        #       though it is acctually existed in user's PATH variables.
        #       depsland setup program cannot handle it, setting
        #       `level='system'` may cause a fatal error. so i remained
        #       `level='user'` and maybe we need to prompt user to handle it by
        #       him/herself.
        print(':trf2', '[green]installation done[/]')
    
    @staticmethod
    def _create_desktop_shortcut(file_i: str, file_o: str) -> None:
        """
        this function was copied from `depsland.utils.gen_exe.main
        .create_shortcut`.
        """
        vbs = fs.xpath('shortcut_gen.vbs')
        command = dedent('''
                Set objWS = WScript.CreateObject("WScript.Shell")
                lnkFile = "{file_o}"
                Set objLink = objWS.CreateShortcut(lnkFile)
                objLink.TargetPath = "{file_i}"
                objLink.Save
            ''').format(
            file_i=file_i.replace('/', '\\'),
            file_o=file_o.replace('/', '\\'),
        )
        dumps(command, vbs, ftype='plain')
        run_cmd_args('cscript', '/nologo', vbs)
        fs.remove_file(vbs)
    
    @staticmethod
    def _set_environment_variables(dir_: str, level='user') -> None:
        new_depsland_env = dir_.replace('/', '\\')
        print(':v', new_depsland_env)
        
        class EnvironmentVariablesAccess:
            
            def __init__(self, level: str):
                self.level = level
                self.key = self.get_resgistry_key(level)
            
            @staticmethod
            def get_resgistry_key(level: str) -> winreg.HKEYType:
                """
                ref: https://stackoverflow.com/questions/573817
                """
                if level == 'user':
                    return winreg.OpenKey(
                        winreg.HKEY_CURRENT_USER,
                        'Environment',
                        0, winreg.KEY_ALL_ACCESS
                    )
                else:  # 'system'
                    return winreg.OpenKey(
                        winreg.HKEY_LOCAL_MACHINE,
                        r'SYSTEM\CurrentControlSet\Control\Session Manager'
                        r'\Environment',
                        0, winreg.KEY_READ | winreg.KEY_SET_VALUE
                    )
            
            def get_depsland_variable(self) -> str:
                try:
                    value, _ = winreg.QueryValueEx(self.key, 'DEPSLAND')
                except ValueError:
                    value = ''
                return value
            
            def get_path_variable(self) -> str:
                value, _ = winreg.QueryValueEx(self.key, 'Path')
                return value
            
            def remove_depsland_variable(self, old: str) -> None:
                pass  # do nothing. see also `set_depsland_variable`.
            
            @staticmethod
            def remove_depsland_from_path_variable(
                    paths: t.List[str], old: str
            ) -> None:
                paths.remove(old)
                if (x := old + r'\apps\.bin') in paths:
                    paths.remove(x)
            
            def set_depsland_variable(self, new: str) -> None:
                if self.level == 'user':
                    run_cmd_args('setx', 'DEPSLAND', new)
                else:
                    run_cmd_args('setx', 'DEPSLAND', new, '/m')
            
            def set_depsland_to_path_variable(
                    self, paths: t.List[str], new: str
            ) -> None:
                paths.insert(0, new)
                paths.insert(1, new + r'\apps\.bin')
                winreg.SetValueEx(
                    self.key, 'PATH', 0, winreg.REG_EXPAND_SZ,
                    ';'.join(filter(None, paths))
                )
            
            def close(self):
                winreg.CloseKey(self.key)
        
        env_access = EnvironmentVariablesAccess(level)
        old_depsland_env = env_access.get_depsland_variable()
        old_path_env = env_access.get_path_variable()
        print(':v', old_depsland_env, old_path_env[:80] + '...')
        
        if old_depsland_env != dir_:
            env_access.remove_depsland_variable(old_depsland_env)
            env_access.set_depsland_variable(new_depsland_env)
        
        if new_depsland_env not in old_path_env:
            old_paths = old_path_env.split(';')
            env_access.remove_depsland_from_path_variable(
                old_paths, old_depsland_env)
            env_access.set_depsland_to_path_variable(
                old_paths, new_depsland_env)
        
        env_access.close()


class Navigation(QObject):
    FIRST_PAGE = 0
    LAST_PAGE = 2
    # current_page = AutoProp(0, int)
    current_page = 0
    page_changed = signal(int, bool)
    #   bool: True means forward, False means backward.
    prev_btn: QObject
    next_btn: QObject
    _steps_checker: t.List[t.Optional[t.Callable[[], bool]]]
    
    def __init__(self, prev_btn: QObject, next_btn: QObject):
        super().__init__()
        self.prev_btn = prev_btn
        self.next_btn = next_btn
        self._steps_checker = [None] * (self.LAST_PAGE + 1)
        self._init_bindings()
    
    def add_step_checker(self, step: int, checker: t.Callable) -> None:
        """
        the step checker is only triggered when user clicks 'Next' button.
        """
        self._steps_checker[step] = checker
    
    def _init_bindings(self):
        
        @grafting(self.prev_btn.clicked.connect)
        def _() -> None:
            if self.current_page == self.FIRST_PAGE:
                # this case should not happen, did we forget to disable the
                #   button in the qml UI?
                raise Exception()
            self.current_page -= 1
            self.page_changed.emit(self.current_page, False)
        
        @grafting(self.next_btn.clicked.connect)
        def _() -> None:
            if checker := self._steps_checker[self.current_page]:
                if not checker():
                    return
            
            if self.current_page == self.LAST_PAGE:
                app.exit()
            else:
                self.current_page += 1
                self.page_changed.emit(self.current_page, True)
        
        @grafting(self.page_changed.connect)
        def _(page: int, _) -> None:
            print(f'page changed to {page}')
            if page == self.FIRST_PAGE:
                self.prev_btn['enabled'] = False
            else:
                self.prev_btn['enabled'] = True
            if page == self.LAST_PAGE:
                self.next_btn['text'] = 'Finish'
            else:
                self.next_btn['text'] = 'Next'


wizard = SetupWizard()
