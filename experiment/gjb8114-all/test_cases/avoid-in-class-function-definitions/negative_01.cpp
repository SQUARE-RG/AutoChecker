#include <iostream>

class Account {
public:
    void Deposit(int amount) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-7-1]
    {
        balance_ += amount;
    }

    int GetBalance() const;

private:
    int balance_ = 0;
};

int Account::GetBalance() const {
    return balance_;
}

int main() {
    Account account;
    account.Deposit(5);
    std::cout << account.GetBalance() << '\n';
    return 0;
}
