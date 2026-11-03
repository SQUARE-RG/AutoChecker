#include <iostream>

struct LongHolder {
    explicit LongHolder(long value) : value_(value) {}
    long value() const { return value_; }
private:
    long value_;
};

int main() {
    LongHolder holders[] = {LongHolder{1L}, LongHolder{2L}};
    std::cout << holders[0].value() << '\n';
    return 0;
}
