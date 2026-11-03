struct ThreadState
{
    static thread_local int value;
};

thread_local int ThreadState::value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-2]

int main()
{
    ThreadState::value = 1;
    return 0;
}
