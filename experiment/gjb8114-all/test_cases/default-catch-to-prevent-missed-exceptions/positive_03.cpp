#include <stdexcept>

int main() {
    auto handler = [] {
        try {
            throw std::runtime_error("boom");
        } catch (const std::runtime_error& e) {
            (void)e;
        } catch (...) {
        }
    };
    handler();
    return 0;
}
