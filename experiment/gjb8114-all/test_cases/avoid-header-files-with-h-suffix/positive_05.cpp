#include <ctime>

int main() {
    std::time_t now = std::time(nullptr);
    return now < static_cast<std::time_t>(0) ? 1 : 0;
}
