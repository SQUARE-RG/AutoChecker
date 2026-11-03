#include <iostream>

class Counter {
public:
    [[nodiscard]] auto GetCount() const { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-7-1]
        return count_;
    }

    void Increment();
private:
    int count_ = 0;
};

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
