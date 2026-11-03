#include <iostream>

class Counter {
public:
    [[nodiscard]] auto GetCount() const;
    void Increment();
private:
    int count_ = 0;
};

auto Counter::GetCount() const {
    return count_;
}

void Counter::Increment() {
    ++count_;
}

int main() {
    Counter c;
    c.Increment();
    int value = c.GetCount();
    std::cout << value << '\n';
    return 0;
}
