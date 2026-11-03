#include <iostream>

class Flag {
public:
    explicit Flag(bool on) : on_(on) {}
    bool value() const { return on_; }

    // Overload logical NOT, which is not prohibited by this rule.
    bool operator!() const { return !on_; }

private:
    bool on_;
};

int main() {
    Flag flag(true);
    bool a = flag.value();
    bool b = !flag; // uses overloaded operator!
    bool combined = (a && b) || (a && !b);
    std::cout << combined << '\n';
    return 0;
}
