struct LoopState {
    static int counter;
};

int LoopState::counter = 0;

int main() {
    for (LoopState::counter = 0; LoopState::counter < 10; ++LoopState::counter) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-1]
    {
    }
    return 0;
}
