#include <iostream>

class SessionGuard {
public:
    explicit SessionGuard(bool active) : active_(active) {}
    ~SessionGuard() {
        if (active_) {
            std::cerr << "session still active at shutdown\n";
        }
    }
    bool had_active_session() const { return active_; }
private:
    bool active_;
};

int main() {
    SessionGuard guard(true);
    return guard.had_active_session() ? 1 : 0;
}
