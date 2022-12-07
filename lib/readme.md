
We prepare two libraries in this folder:

- qmlease: a flexible toolset to elegantly build QML based applications.
- pyside6_lite: unofficial tailored package based on pyside6, that aimed at the minimal distribution size.

# Steps

1. Git clone qmlease repo: `git clone https://github.com/likianta/qmlease`
2. Follow the guide of `qmlease/sidework/pyside_package_tailor/readme.zh.md`, create a `pyside6_lite` package. 

    The package is generated in `qmlease/sidework/pyside_package_tailor/dist`.

3. Copy them here, finally we get:

    ```
    lib
    |= qmlease
    |= pyside6_lite
       |= PySide6
       |= shiboken6
    ```
