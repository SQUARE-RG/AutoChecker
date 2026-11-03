#include <cstdlib>
#include <iostream>

int main() {
    int status = std::system("mkdir -p /tmp/ucasaat_demo");
    if (status != 0) {
        std::cerr << "command failed with status " << status << '\n';
        return 1;
    }
    return 0;
}
