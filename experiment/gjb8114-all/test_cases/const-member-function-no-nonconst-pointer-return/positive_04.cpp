#include <iostream>

class Table {
public:
    Table() : values_{1, 2, 3} {}

    const int& at(int i) const { return values_[i]; }

private:
    int values_[3];
};

int main() {
    const Table t;
    int x = t.at(0);
    return x;
}
