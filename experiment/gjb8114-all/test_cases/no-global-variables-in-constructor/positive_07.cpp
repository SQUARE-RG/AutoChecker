#include <iostream>

int gScale = 3;

class Measurement {
public:
    explicit Measurement(int raw);
    int scaled() const;
private:
    int value;
    int factor;
};

Measurement::Measurement(int raw) : value(raw), factor(1) {}

int Measurement::scaled() const {
    return value * factor * gScale;
}

int main() {
    Measurement m(5);
    std::cout << m.scaled() << '\n';
    return 0;
}
