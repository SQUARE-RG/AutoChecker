enum class State {
    IDLE = 0,
    RUNNING = 1, // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-4]
    PAUSED
};

int main() {
    State s = State::PAUSED;
    (void)s;
    return 0;
}
