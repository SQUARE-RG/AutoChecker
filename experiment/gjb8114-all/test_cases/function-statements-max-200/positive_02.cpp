#include <iostream>

struct Calculator {
    int calculate(int n) {
        int total = 0;
        for (int i = 0; i < n; ++i) {
            if (i % 2 == 0) {
                total += i;
            } else {
                total -= i;
            }
        }
        switch (total) {
            case 0: total += 1; break;
            default: break;
        }
        return total;
    }
};

int main() { Calculator c; return c.calculate(10) < 0; }
