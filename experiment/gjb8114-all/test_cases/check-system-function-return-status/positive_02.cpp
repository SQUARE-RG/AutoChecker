#include <cstdlib>
#include <cstdio>

int main() {
    if (std::system("rm -f /tmp/ucasaat_demo") != 0) {
        std::perror("system command failed");
        return 1;
    }
    return 0;
}
