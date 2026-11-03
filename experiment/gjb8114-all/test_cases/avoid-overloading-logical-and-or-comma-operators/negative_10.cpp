#include <iostream>

class Logger {
public:
    explicit Logger(int id) : id_(id) {}

    friend const Logger& operator,(const Logger& lhs, const Logger& rhs) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-3]
        std::cout << lhs.id_ << ',' << rhs.id_ << '\n';
        return rhs;
    }

private:
    int id_;
};

int main() {
    Logger a(1);
    Logger b(2);
    (void)(a, b);
    return 0;
}
