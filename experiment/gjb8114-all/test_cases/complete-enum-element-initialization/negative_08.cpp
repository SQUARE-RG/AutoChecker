enum class State
{
    Start,
    Running,
    Finished = 8 // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-4]
};

int main()
{
    State state = State::Finished;
    return static_cast<int>(state);
}
