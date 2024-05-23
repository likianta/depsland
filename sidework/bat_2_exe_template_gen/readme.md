# BAT 2 EXE Template Generator

1. Download mingw64 from
   [official release](https://github.com/niXman/mingw-builds-binaries/releases)

2. Extract it to someplace, and add `<extracted_mingw64>/bin` folder to your
   PATH.

3. Run command:

    ```sh
    cd sidework/bat_2_exe_templater

    # (A)
    # g++ template.cpp -o template.exe
    # (B) (suggest)
    g++ template.cpp -static -o template_static.exe

    # TODO: B is tested ok, but its size (2.4MB) is much larger than A (64KB).
    #   I need to find out why and how to reduce it.
    ```

4. Move "template_staic.exe" to `depsland/utils/gen_exe/template.exe`. (Note
   I've renamed from "template_static.exe" to "template.exe".)

5. Done.

Thanks to [silvandeleemput](https://github.com/silvandeleemput)'s great work, I
learned the magic idea of manipulating exe template to embed the bat command.
