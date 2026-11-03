#include <iostream>

struct Signal {
    bool active;
    explicit operator bool() const { return active; }
};

int main() {
    Signal left{true};
    Signal right{false};
    bool both = left && right;
    bool either = left || right;
    std::cout << both << ' ' << either << '\n';
    return 0;
}
