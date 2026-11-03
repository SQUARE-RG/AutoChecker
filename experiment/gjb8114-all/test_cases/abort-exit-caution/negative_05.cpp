#include <cstdlib>
#include <iostream>

class SessionGuard {
public:
    explicit SessionGuard(bool active) : active_(active) {}
    ~SessionGuard() {
        if (active_) {
            std::cerr << "session still active at shutdown\n";
            std::exit(EXIT_FAILURE); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-3]
        }
    }
private:
    bool active_;
};

int main() {
    SessionGuard guard(true);
    return 0;
}
