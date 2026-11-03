#include <iostream>

class Account {
public:
    Account() : balance_(0) {}
    explicit Account(int initial) : balance_(initial) {}
    int Balance() const { return balance_; }
private:
    int balance_;
};

int main() {
    Account empty;
    Account funded(100);
    std::cout << empty.Balance() + funded.Balance() << '\n';
    return 0;
}
