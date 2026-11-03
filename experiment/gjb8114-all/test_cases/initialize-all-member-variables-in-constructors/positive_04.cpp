#include <iostream>

class Sensor {
public:
    explicit Sensor(int& source)
        : threshold_(10), source_(source) {}
    int threshold() const { return threshold_; }
    int value() const { return source_; }
private:
    const int threshold_;
    int& source_;
};

int main() {
    int raw = 42;
    Sensor s(raw);
    std::cout << s.threshold() << " " << s.value() << '\n';
    return 0;
}
