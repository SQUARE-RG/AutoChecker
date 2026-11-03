#include <string>

int main() {
    std::string status = "ready";
    if ("ready" != status) {
        return 1;
    }
    return 0;
}
