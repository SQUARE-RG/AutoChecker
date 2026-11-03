#include <iostream>

struct LongHolder {
    LongHolder(long value) : value_(value) {} // CHECK-MESSAGES: :[[@LINE]]:5: warning: {{.*}} [ucassaat-r-2-2-3]
    long value() const { return value_; }
private:
    long value_;
};

int main() {
    LongHolder holders[] = {1L, 2L};
    std::cout << holders[0].value() << '\n';
    return 0;
}
