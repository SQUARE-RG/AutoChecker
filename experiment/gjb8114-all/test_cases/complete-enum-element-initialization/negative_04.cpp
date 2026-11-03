int main()
{
    enum State
    {
        IDLE,
        RUNNING = 1,
        STOPPED = 2 // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-4]
    };
    State s = STOPPED;
    return static_cast<int>(s);
}
