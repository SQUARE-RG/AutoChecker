int main()
{
    struct TimerState
    {
        long ticks : 12; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-11]
        unsigned long cycles : 12;
    };

    TimerState state;
    state.ticks = 1;
    state.cycles = 2;
    return 0;
}
