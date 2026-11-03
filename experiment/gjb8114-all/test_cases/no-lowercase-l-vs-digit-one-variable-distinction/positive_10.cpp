#include <stdexcept>

void handle(int code) {
    try {
        if (code == 1) {
            throw std::runtime_error("one");
        }
        throw std::out_of_range("other");
    } catch (const std::runtime_error& value1Info) {
        (void)value1Info;
    } catch (const std::out_of_range& levelTotal) {
        (void)levelTotal;
    }
}

int main() {
    handle(1);
    handle(0);
    return 0;
}
