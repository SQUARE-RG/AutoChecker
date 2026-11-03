#include <cstdbool>

class Machine;

int next_state(Machine& machine, int n);

class Machine {
public:
    int run(int n) {
        return next_state(*this, n);
    }
};

int next_state(Machine& machine, int n) {
    if (n <= 0) {
        return 0;
    }
    return machine.run(n - 1); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-16]
}

int main() {
    Machine m;
    int result = m.run(0);
    return result;
}
