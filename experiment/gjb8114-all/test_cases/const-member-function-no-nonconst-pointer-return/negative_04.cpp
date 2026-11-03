#include <iostream>

class Table {
public:
    Table() : values_{1, 2, 3} {}

    int& at(int i) const { return values_[i]; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-2]

private:
    mutable int values_[3];
};

int main() {
    const Table t;
    t.at(0) = 9;
    return 0;
}
