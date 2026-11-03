struct StateMachine
{
    enum State { IDLE, RUNNING, STOPPED };
};

int main()
{
    StateMachine::State state = StateMachine::IDLE;
    switch (state)
    {
        case StateMachine::IDLE:
            break;
        case StateMachine::RUNNING:
            break;
        case StateMachine::STOPPED:
            break;
    }
    return 0;
}
