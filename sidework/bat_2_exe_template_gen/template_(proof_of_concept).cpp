#include <shlwapi.h>
#include <stdlib.h>
#include <iostream>
#include <string>


int main(int argc, char **argv) {
    std::string command = "";

    command += argv[1];
    for (int i = 2; i < argc; i++) {
        bool has_space = strchr(argv[i], ' ') != NULL;
        if (has_space) {
            command += " \"";
            command += argv[i];
            command += "\"";
        } else {
            command += " ";
            command += argv[i];
        }
    }

    int return_code = system(command.c_str());
    return return_code;
}
