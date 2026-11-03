#include <iostream>

class Pair {
public:
    Pair();
    explicit Pair(int first);
    int sum() const { return first_ + second_; }
private:
    int first_;
    int second_;
};

Pair::Pair() {
    first_ = 0;
    second_ = 0;
}

Pair::Pair(int first) {
    first_ = first;
    second_ = 0;
}

int main() {
    Pair p;
    Pair q(5);
    std::cout << p.sum() << " " << q.sum() << '\n';
    return 0;
}
