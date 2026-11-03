struct StateMachine
{
    enum State { IDLE, RUNNING, STOPPED };
};

int main()
{
    StateMachine::State state = StateMachine::IDLE;
    switch (state) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-6]
    {
        case StateMachine::IDLE:
            break;
        case StateMachine::RUNNING:
            break;
    }
    return 0;
}
