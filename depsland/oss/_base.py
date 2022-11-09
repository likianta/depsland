class BaseOss:
    type_ = 'base'
    path: 'BaseOssPath'
    
    def upload(self, file: str, link: str) -> None:
        """
        warning: if target exists, will overwrite.
        """
        raise NotImplementedError
    
    def download(self, link: str, file: str) -> None:
        raise NotImplementedError
    
    def delete(self, link: str) -> None:
        raise NotImplementedError

    @staticmethod
    def _update_progress(
            description: str,
            bytes_consumed: int, total_bytes: int
    ) -> None:
        print('{}: {:.2%}'.format(
            description,
            bytes_consumed / total_bytes
        ), end='\r')


class BaseOssPath:
    appid: str
    root: str
    
    def __init__(self, appid: str):
        self.appid = appid
        # `self.root` needs to be implemented in subclasses
    
    def __str__(self):
        return f'oss:/depsland/apps/{self.appid}'
    
    @property
    def manifest(self) -> str:
        return f'{self.root}/manifest.pkl'
    
    @property
    def assets(self) -> str:
        return f'{self.root}/assets'
    
    @property
    def pypi(self) -> str:
        return f'{self.root}/pypi'
