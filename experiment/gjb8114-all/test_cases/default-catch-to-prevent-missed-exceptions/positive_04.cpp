#include <stdexcept>

struct Widget {
    Widget() try {
        throw std::runtime_error("ctor fail");
    } catch (const std::runtime_error& e) {
        (void)e;
    } catch (...) {
    }
};

int main() {
    try {
        Widget w;
    } catch (...) {
    }
    return 0;
}
